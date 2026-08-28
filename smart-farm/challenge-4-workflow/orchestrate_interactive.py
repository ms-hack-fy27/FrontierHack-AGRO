"""
Challenge 5: Interactive Multi-Agent Orchestration -- Microsoft Agent Framework (Python)
GreenRise AgriTech Smart Farm Lab

Orchestrates two agents:
1. smart-farm-classifier-agent (Agent 1): Tool-grounded agent for metric threshold analysis.
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

MONITOR_AGENT_NAME = "smart-farm-classifier-agent"
ADVISOR_AGENT_NAME = "smart-farm-advisor-agent"


def _load_zones() -> list[dict]:
    if not DATA_PATH.exists():
        print(f"Error: Data file not found at {DATA_PATH}")
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as data_file:
        return json.load(data_file)["zones"]


def check_health_monitor(zone_id: str) -> str:
    """Tool for comparing growing zone metrics with configured thresholds."""
    zones = _load_zones()
    zone = next(
        (item for item in zones if item["zone_id"] == zone_id or item["name"] == zone_id),
        None,
    )
    if not zone:
        return json.dumps({"error": f"Growing zone '{zone_id}' was not found."})

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
            direction = "above the maximum" if value > threshold["max"] else "below the minimum"
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
    """Verify that both agents already exist in Azure AI Projects / Foundry."""
    from azure.ai.projects.models import FunctionTool

    existing = {agent.name for agent in client.agents.list()}
    missing = [
        agent_name
        for agent_name in (MONITOR_AGENT_NAME, ADVISOR_AGENT_NAME)
        if agent_name not in existing
    ]
    if missing:
        raise RuntimeError(
            "Required agent(s) do not exist in Microsoft Foundry: "
            + ", ".join(missing)
            + ". Create them before running Challenge 5."
        )

    tool = FunctionTool(
        name="check_health_monitor",
        description="Compares the four soil and climate metrics for a zone with its configured thresholds.",
        parameters={
            "type": "object",
            "properties": {
                "zone_id": {"type": "string", "description": "Zone ID or name (for example, ZONE-ALPHA)"}
            },
            "required": ["zone_id"],
            "additionalProperties": False,
        },
        strict=False,
    )

    print(f"  [✓] Existing agent located: {MONITOR_AGENT_NAME}")
    print(f"  [✓] Existing agent located: {ADVISOR_AGENT_NAME}")

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
            "Based on the crop health monitor report below, "
            "provide a detailed agronomic diagnosis and practical action recommendations:\n\n"
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
                     🌱 MULTI-AGENT ORCHESTRATION - GREENRISE AGRITECH (CHALLENGE 5)
================================================================================
    [ Execution Flow ]

   ┌───────────────────────────────────┐
     │        👤  USER (PROMPT)           │
   └─────────────────┬─────────────────┘
                     │
                                         │  1. Initial Prompt
                     ▼
   ┌───────────────────────────────────┐
     │  🤖 AGENT 1: HEALTH MONITOR       │
   │   (smart-farm-classifier-agent)      │
   └─────────────────┬─────────────────┘
                     │
                                         │  2. Analysis Context / Anomalies
                     ▼
   ┌───────────────────────────────────┐
     │  🤖 AGENT 2: AGRONOMIC ADVISOR    │
   │   (smart-farm-advisor-agent)      │
   └─────────────────┬─────────────────┘
                     │
                                         │  3. Diagnosis and Final Assessment
                     ▼
   ┌───────────────────────────────────┐
     │      📄 FINAL RESPONSE DISPLAYED  │
   └───────────────────────────────────┘
================================================================================
""")


def main():
    if not PROJECT_CONNECTION_STRING:
        print("❌ Error: PROJECT_CONNECTION_STRING is not configured in the .env file!")
        print("Please run Challenge 0 before continuing.")
        sys.exit(1)

    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential

    display_flow_header()

    print("🔌 Connecting to the Azure AI Projects client...")
    client = AIProjectClient(
        endpoint=PROJECT_CONNECTION_STRING,
        credential=DefaultAzureCredential()
    )

    completed_successfully = False
    try:
        print("\n🔍 Checking agents in Microsoft Foundry...")
        monitor_name, advisor_name = ensure_agents_deployed(client)

        print("\n--------------------------------------------------------------------------------")
        prompt_default = "Analyze the health status of all zones (ZONE-ALPHA, ZONE-BETA, ZONE-GAMMA, ZONE-DELTA, ZONE-EPSILON) and identify anomalies."
        user_input = input("💬 Enter the prompt for the agents (press Enter to use the default):\n> ").strip()

        if not user_input:
            user_input = prompt_default
            print(f"ℹ️ Using default prompt: '{user_input}'")

        # --- STEP 1: AGENT 1 (MONITOR) ---
        print("\n" + "="*80)
        print(" 📥 [STEP 1] SENDING PROMPT TO AGENT 1: HEALTH MONITOR")
        print("="*80)
        print(f"  ► Target Agent: {monitor_name}")
        print(f"  ► Received Prompt: \"{user_input}\"")
        print("  ⏳ Processing readings and running tools (check_health_monitor)...")

        monitor_output = run_monitor_agent(client, monitor_name, user_input)

        print("\n" + "-"*80)
        print(" 📤 [AGENT 1 COMPLETE] RESPONSE GENERATED BY THE HEALTH MONITOR:")
        print("-"*80)
        print(monitor_output)

        # --- STEP 2: AGENT 2 (ADVISOR) ---
        print("\n" + "="*80)
        print(" 🔄 [PASSING CONTEXT] AGENT 1  ═══►  AGENT 2 (AGRONOMIC ADVISOR)")
        print("="*80)
        print(f"  ► Target Agent: {advisor_name}")
        print("  ► Transferred Data: Health Monitor analysis report")
        print("  ⏳ Generating agronomic assessment and action plan...")

        final_advisor_output = run_advisor_agent(client, advisor_name, monitor_output)

        # --- STEP 3: FINAL RESULT ---
        print("\n" + "="*80)
        print(" 🎯 [FINAL STEP] FINAL RESPONSE FROM THE AGRONOMIC ADVISOR")
        print("="*80)
        print(final_advisor_output)
        print("="*80 + "\n")
        completed_successfully = True

    finally:
        client.close()
        if completed_successfully:
            print("✅ Orchestration flow completed successfully!")


if __name__ == "__main__":
    main()
