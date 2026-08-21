"""Challenge 2: Monitor crop health agents with Application Insights."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def _find_repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / ".env").exists():
            return parent
    return Path(__file__).resolve().parents[2]


load_dotenv(_find_repo_root() / ".env")
if os.getenv("AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING") != "true":
    print("AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING must be true in .env")
    sys.exit(1)

PROJECT_CONNECTION_STRING = os.getenv("PROJECT_CONNECTION_STRING")
MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-5.4")
APPINSIGHTS_CONNECTION_STRING = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")


def setup_tracing():
    """Instrument before importing azure.ai.projects, then configure the exporter."""
    from azure.ai.projects.telemetry import AIProjectInstrumentor
    from azure.monitor.opentelemetry import configure_azure_monitor

    AIProjectInstrumentor().instrument()
    configure_azure_monitor(connection_string=APPINSIGHTS_CONNECTION_STRING, enable_live_metrics=True)


def run_traced_agent():
    from azure.ai.projects import AIProjectClient
    from azure.ai.projects.models import PromptAgentDefinition
    from azure.identity import DefaultAzureCredential

    client = AIProjectClient(endpoint=PROJECT_CONNECTION_STRING, credential=DefaultAzureCredential())
    openai_client = client.get_openai_client()
    agent = client.agents.create_version(
        agent_name="smart-farm-tracing-agent",
        definition=PromptAgentDefinition(
            model=MODEL_DEPLOYMENT_NAME,
            instructions="You are a smart farm monitoring assistant. Summarize the supplied zone statuses and call out the critical zone.",
        ),
    )
    conversation = openai_client.conversations.create()
    try:
        response = openai_client.responses.create(
            input="GreenRise AgriTech: ZONE-ALPHA warning, ZONE-BETA normal, ZONE-GAMMA critical, ZONE-DELTA normal, ZONE-EPSILON warning. Return a concise risk summary.",
            conversation=conversation.id,
            extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
        )
        print(response.output_text)
    finally:
        openai_client.conversations.delete(conversation_id=conversation.id)
        client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        client.close()


def main():
    if not PROJECT_CONNECTION_STRING:
        print("PROJECT_CONNECTION_STRING not set. Run challenge 0 first!")
        sys.exit(1)
    setup_tracing()
    run_traced_agent()
    print("Traced call complete. Review Foundry Traces and Application Insights.")


if __name__ == "__main__":
    main()
