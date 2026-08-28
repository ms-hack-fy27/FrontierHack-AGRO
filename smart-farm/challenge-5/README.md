# Challenge 5: Orquestração Multi-Agente Interativa

Tempo estimado: ~20 minutos

## Objetivos

Executar uma orquestração simples de dois agentes utilizando a versão mais recente do **Microsoft Agent Framework** em Python (`azure-ai-projects`).

1. Solicitar um prompt ao usuário interativamente.
2. Enviar o prompt para o **Agente 1** (`smart-farm-classifier-agent`), responsável por verificar métricas da lavoura através da ferramenta `check_health_monitor`.
3. Repassar o contexto de resposta do Agente 1 diretamente para o **Agente 2** (`smart-farm-advisor-agent`), que analisa os dados e gera um parecer agronômico.
4. Exibir de forma gráfica no terminal cada etapa de transição e a resposta final do agente conselheiro.

---

## Fluxo de Orquestração

```text
 ┌───────────────────────────────────┐
 │        👤  USUÁRIO (PROMPT)       │
 └─────────────────┬─────────────────┘
                   │
                   │  1. Prompt do Usuário
                   ▼
 ┌───────────────────────────────────┐
 │  🤖 AGENTE 1: MONITOR DE SAÚDE    │
 │   (smart-farm-classifier-agent)      │
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
```

---

## Como Executar

Abra o terminal na pasta do desafio e execute o script em Python:

```powershell
cd smart-farm\challenge-5
python orchestrate_interactive.py
```

### O que o script faz:

1. **Garante a existência dos Agentes**: Conecta-se ao serviço Azure AI Projects / Microsoft Foundry e reutiliza ou cria os agentes `smart-farm-classifier-agent` e `smart-farm-advisor-agent`.
2. **Coleta de Prompt**: Pergunta interativamente qual consulta você deseja fazer para a fazenda.
3. **Execução do Agente 1**: Envia o prompt ao Monitor de Saúde da Lavoura, que invoca a ferramenta `check_health_monitor` e gera o relatório analítico.
4. **Repasse de Contexto**: Pega a saída do Agente 1 e a envia como contexto para o Agente 2 (Conselheiro Agronômico).
5. **Visualização Gráfica**: Exibe banners gráficos no terminal demonstrando a transição de mensagens entre o Usuário -> Agente 1 -> Agente 2 -> Resposta Final.

---

## Critérios de Sucesso

- [ ] Script Python executa sem erros na versão mais recente do Agentic Framework (`azure-ai-projects`).
- [ ] O prompt do usuário é capturado via CLI.
- [ ] O Agente 1 (`smart-farm-classifier-agent`) processa a solicitação e executa a ferramenta de monitoramento.
- [ ] A resposta do Agente 1 é repassada como contexto ao Agente 2 (`smart-farm-advisor-agent`).
- [ ] A interface exibe visualmente no terminal o repasse de mensagens e a resposta final do Agente 2.
