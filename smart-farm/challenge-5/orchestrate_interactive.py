"""
Challenge 5: Interactive Multi-Agent Orchestration -- Microsoft Agent Framework (Python)
GreenRise AgriTech Smart Farm Lab

Orchestrates two agents:
1. smart-farm-monitor-agent (Agent 1): Tool-grounded agent for metric threshold analysis.
2. smart-farm-advisor-agent (Agent 2): Tool-free agent for agronomic reasoning & recommendations.

Flow: User Prompt -> Agent 1 -> Response Context -> Agent 2 -> Final Agronomic Response.
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def _find_repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / ".env").exists():
            return parent
    return Path(__file__).resolve().parents[2]


REPO_ROOT = _find_repo_root()
load_dotenv(REPO_ROOT / ".env")
PROJECT_CONNECTION_STRING = os.getenv("PROJECT_CONNECTION_STRING")
MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-5.4")
DATA_PATH = Path(__file__).resolve().parent.parent / "challenge-1-build" / "smart_farm_data.json"

MONITOR_AGENT_NAME = "smart-farm-monitor-agent"
ADVISOR_AGENT_NAME = "smart-farm-advisor-agent"


def _load_zones() -> list[dict]:
    if not DATA_PATH.exists():
        print(f"Erro: Arquivo de dados não encontrado em {DATA_PATH}")
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as data_file:
        return json.load(data_file)["zones"]


def check_health_monitor(zone_id: str) -> str:
    """Ferramenta para comparar métricas da zona de cultivo com limites configurados."""
    zones = _load_zones()
    zone = next(
        (item for item in zones if item["zone_id"] == zone_id or item["name"] == zone_id),
        None,
    )
    if not zone:
        return json.dumps({"error": f"Zona de cultivo '{zone_id}' não encontrada."})

    analysis = {
        "zone_id": zone["zone_id"],
        "name": zone["name"],
        "crop": zone["crop"],
        "reported_status": zone["status"],
        "last_inspection": zone["last_inspection"],
        "anomalies": [],
        "all_metrics": {},
    }
    for metric, reading in zone["readings"].items():
        value = reading["value"]
        threshold = zone["thresholds"][metric]
        in_range = threshold["min"] <= value <= threshold["max"]
        analysis["all_metrics"][metric] = {
            "value": value,
            "unit": reading["unit"],
            "min": threshold["min"],
            "max": threshold["max"],
            "in_range": in_range,
        }
        if not in_range:
            boundary = threshold["max"] if value > threshold["max"] else threshold["min"]
            direction = "acima do máximo" if value > threshold["max"] else "abaixo do mínimo"
            percent = abs(value - boundary) / boundary * 100 if boundary else 0
            analysis["anomalies"].append({
                "metric": metric,
                "value": value,
                "unit": reading["unit"],
                "threshold_min": threshold["min"],
                "threshold_max": threshold["max"],
                "deviation": f"{percent:.1f}% {direction}",
            })
    return json.dumps(analysis, indent=2)


def ensure_agents_deployed(client) -> tuple[str, str]:
    """Garante que os dois agentes estão implantados no Azure AI Projects / Foundry."""
    from azure.ai.projects.models import FunctionTool, PromptAgentDefinition

    tool = FunctionTool(
        name="check_health_monitor",
        description="Compara as quatro métricas do solo/clima de uma zona com seus limites configurados.",
        parameters={
            "type": "object",
            "properties": {
                "zone_id": {"type": "string", "description": "ID ou nome da zona (ex: ZONE-ALPHA)"}
            },
            "required": ["zone_id"],
            "additionalProperties": False,
        },
        strict=False,
    )

    existing = {agent.name for agent in client.agents.list()}

    if MONITOR_AGENT_NAME not in existing:
        instructions = """
Você é o monitor de saúde de lavouras da GreenRise AgriTech.
Sempre utilize a ferramenta check_health_monitor para obter os dados de cada zona solicitada.
Retorne um status estruturado indicando ID da zona, cultura, status (normal, aviso ou crítico),
métricas, anomalias e recomendação imediata.
"""
        client.agents.create_version(
            agent_name=MONITOR_AGENT_NAME,
            definition=PromptAgentDefinition(
                model=MODEL_DEPLOYMENT_NAME,
                instructions=instructions,
                tools=[tool]
            )
        )
        print(f"  [+] Agente criado: {MONITOR_AGENT_NAME}")
    else:
        print(f"  [✓] Agente existente localizado: {MONITOR_AGENT_NAME}")

    if ADVISOR_AGENT_NAME not in existing:
        instructions = """
Você é o conselheiro agronômico da GreenRise AgriTech. Você não possui ferramentas;
raciocine com base na análise de saúde recebida.
Aplique estes padrões agronômicos:
- Baixa umidade do solo + alta temperatura = estresse de irrigação;
- Alta umidade + baixo pH = risco de fungos/doenças;
- Múltiplas leituras críticas = escalonamento urgente para o agrônomo.
Forneça ações práticas, nível de urgência e o que reavaliar.
"""
        client.agents.create_version(
            agent_name=ADVISOR_AGENT_NAME,
            definition=PromptAgentDefinition(
                model=MODEL_DEPLOYMENT_NAME,
                instructions=instructions
            )
        )
        print(f"  [+] Agente criado: {ADVISOR_AGENT_NAME}")
    else:
        print(f"  [✓] Agente existente localizado: {ADVISOR_AGENT_NAME}")

    return MONITOR_AGENT_NAME, ADVISOR_AGENT_NAME


def run_monitor_agent(client, agent_name: str, input_prompt: str) -> str:
    from openai.types.responses.response_input_param import FunctionCallOutput

    openai_client = client.get_openai_client()
    conversation = openai_client.conversations.create()
    reference = {"agent_reference": {"name": agent_name, "type": "agent_reference"}}

    try:
        response = openai_client.responses.create(
            input=input_prompt,
            conversation=conversation.id,
            extra_body=reference
        )
        while True:
            calls = [item for item in response.output if item.type == "function_call"]
            if not calls:
                return response.output_text
            outputs = []
            for call in calls:
                args = json.loads(call.arguments)
                tool_result = check_health_monitor(args.get("zone_id", ""))
                outputs.append(
                    FunctionCallOutput(
                        type="function_call_output",
                        call_id=call.call_id,
                        output=tool_result
                    )
                )
            response = openai_client.responses.create(
                input=outputs,
                conversation=conversation.id,
                extra_body=reference
            )
    finally:
        openai_client.conversations.delete(conversation_id=conversation.id)


def run_advisor_agent(client, agent_name: str, monitor_context: str) -> str:
    openai_client = client.get_openai_client()
    conversation = openai_client.conversations.create()
    reference = {"agent_reference": {"name": agent_name, "type": "agent_reference"}}

    try:
        prompt_with_context = (
            "Com base no relatório retornado pelo Monitor de Saúde da Lavoura abaixo, "
            "forneça um diagnóstico agronômico detalhado e recomendações práticas de ação:\n\n"
            f"{monitor_context}"
        )
        response = openai_client.responses.create(
            input=prompt_with_context,
            conversation=conversation.id,
            extra_body=reference
        )
        return response.output_text
    finally:
        openai_client.conversations.delete(conversation_id=conversation.id)


def display_flow_header():
    print("""
================================================================================
           🌱 ORQUESTRAÇÃO MULTI-AGENTE - GREENRISE AGRITECH (CHALLENGE 5)
================================================================================
  [ Fluxo de Execução ]

   ┌───────────────────────────────────┐
   │        👤  USUÁRIO (PROMPT)       │
   └─────────────────┬─────────────────┘
                     │
                     │  1. Prompt Inicial
                     ▼
   ┌───────────────────────────────────┐
   │  🤖 AGENTE 1: MONITOR DE SAÚDE    │
   │   (smart-farm-monitor-agent)      │
   └─────────────────┬─────────────────┘
                     │
                     │  2. Contexto de Análise / Anomalias
                     ▼
   ┌───────────────────────────────────┐
   │  🤖 AGENTE 2: ADVISOR AGRONÔMICO  │
   │   (smart-farm-advisor-agent)      │
   └─────────────────┬─────────────────┘
                     │
                     │  3. Diagnóstico e Parecer Final
                     ▼
   ┌───────────────────────────────────┐
   │      📄 RESPOSTA FINAL EXIBIDA    │
   └───────────────────────────────────┘
================================================================================
""")


def main():
    if not PROJECT_CONNECTION_STRING:
        print("❌ Erro: PROJECT_CONNECTION_STRING não configurada no arquivo .env!")
        print("Por favor, execute o Challenge 0 antes de continuar.")
        sys.exit(1)

    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential

    display_flow_header()

    print("🔌 Conectando ao Azure AI Projects Client...")
    client = AIProjectClient(
        endpoint=PROJECT_CONNECTION_STRING,
        credential=DefaultAzureCredential()
    )

    try:
        print("\n🔍 Verificando agentes no Microsoft Foundry...")
        monitor_name, advisor_name = ensure_agents_deployed(client)

        print("\n--------------------------------------------------------------------------------")
        prompt_default = "Analise o estado de saúde de todas as zonas (ZONE-ALPHA, ZONE-BETA, ZONE-GAMMA, ZONE-DELTA, ZONE-EPSILON) e identifique anomalias."
        user_input = input(f"💬 Digite o prompt para os agentes (pressione Enter para usar o padrão):\n> ").strip()

        if not user_input:
            user_input = prompt_default
            print(f"ℹ️ Usando prompt padrão: '{user_input}'")

        # --- ETAPA 1: AGENTE 1 (MONITOR) ---
        print("\n" + "="*80)
        print(" 📥 [ETAPA 1] ENVIANDO PROMPT PARA AGENTE 1: MONITOR DE SAÚDE")
        print("="*80)
        print(f"  ► Agente Alvo: {monitor_name}")
        print(f"  ► Prompt Recebido: \"{user_input}\"")
        print("  ⏳ Processando leituras e executando ferramentas (check_health_monitor)...")

        monitor_output = run_monitor_agent(client, monitor_name, user_input)

        print("\n" + "-"*80)
        print(" 📤 [AGENTE 1 FINALIZADO] RESPOSTA GERADA PELO MONITOR DE SAÚDE:")
        print("-"*80)
        print(monitor_output)

        # --- ETAPA 2: AGENTE 2 (ADVISOR) ---
        print("\n" + "="*80)
        print(" 🔄 [REPASSANDO CONTEXTO] AGENTE 1  ═══►  AGENTE 2 (ADVISOR AGRONÔMICO)")
        print("="*80)
        print(f"  ► Agente Alvo: {advisor_name}")
        print("  ► Dados Transferidos: Relatório analítico do Monitor de Saúde")
        print("  ⏳ Gerando parecer agronômico e plano de ação...")

        final_advisor_output = run_advisor_agent(client, advisor_name, monitor_output)

        # --- ETAPA 3: RESULTADO FINAL ---
        print("\n" + "="*80)
        print(" 🎯 [ETAPA FINAL] RESPOSTA FINAL DO AGENTE CONSELEIRO AGRONÔMICO")
        print("="*80)
        print(final_advisor_output)
        print("="*80 + "\n")

    finally:
        client.close()
        print("✅ Execução do fluxo de orquestração concluída com sucesso!")


if __name__ == "__main__":
    main()
