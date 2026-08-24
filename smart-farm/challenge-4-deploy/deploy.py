"""Challenge 4: Python orchestration and portal workflow for GreenRise AgriTech."""

import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv


def _find_repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / ".env").exists():
            return parent
    return Path(__file__).resolve().parents[2]


load_dotenv(_find_repo_root() / ".env")
PROJECT_CONNECTION_STRING = os.getenv("PROJECT_CONNECTION_STRING")
MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-5.4")
DATA_PATH = Path(__file__).resolve().parent.parent / "challenge-1-build" / "smart_farm_data.json"
ZONE_IDS = ["ZONE-ALPHA", "ZONE-BETA", "ZONE-GAMMA", "ZONE-DELTA", "ZONE-EPSILON"]
MONITOR_AGENT_NAME = "smart-farm-monitor-agent"
ADVISOR_AGENT_NAME = "smart-farm-advisor-agent"
WORKFLOW_AGENT_NAME = os.getenv("WORKFLOW_AGENT_NAME", "smart-farm-health-workflow")


def _zones() -> list[dict]:
    with open(DATA_PATH, "r", encoding="utf-8") as data_file:
        return json.load(data_file)["zones"]


def check_health_monitor(zone_id: str) -> str:
    zone = next((item for item in _zones() if item["zone_id"] == zone_id or item["name"] == zone_id), None)
    if not zone:
        return json.dumps({"error": f"Crop zone '{zone_id}' not found"})
    result = {"zone_id": zone["zone_id"], "name": zone["name"], "crop": zone["crop"], "status": zone["status"], "anomalies": [], "all_metrics": {}}
    for metric, reading in zone["readings"].items():
        threshold = zone["thresholds"][metric]
        value = reading["value"]
        in_range = threshold["min"] <= value <= threshold["max"]
        result["all_metrics"][metric] = {"value": value, "unit": reading["unit"], "min": threshold["min"], "max": threshold["max"], "in_range": in_range}
        if not in_range:
            boundary = threshold["max"] if value > threshold["max"] else threshold["min"]
            direction = "above max" if value > threshold["max"] else "below min"
            percent = abs(value - boundary) / boundary * 100 if boundary else 0
            result["anomalies"].append({"metric": metric, "value": value, "unit": reading["unit"], "deviation": f"{percent:.1f}% {direction}"})
    return json.dumps(result, indent=2)


def ensure_agents_deployed() -> tuple:
    """Create persistent monitor and advisor agents when they do not exist."""
    from azure.ai.projects import AIProjectClient
    from azure.ai.projects.models import FunctionTool, PromptAgentDefinition
    from azure.identity import DefaultAzureCredential

    tool = FunctionTool(name="check_health_monitor", description="Compare all four crop metrics with thresholds.", parameters={"type": "object", "properties": {"zone_id": {"type": "string"}}, "required": ["zone_id"]}, strict=False)
    client = AIProjectClient(endpoint=PROJECT_CONNECTION_STRING, credential=DefaultAzureCredential())
    existing = {agent.name for agent in client.agents.list()}
    if MONITOR_AGENT_NAME not in existing:
        client.agents.create_version(agent_name=MONITOR_AGENT_NAME, definition=PromptAgentDefinition(model=MODEL_DEPLOYMENT_NAME, instructions="You are the GreenRise crop health monitor. Use check_health_monitor for every requested zone and return structured status, thresholds, anomalies, and next steps.", tools=[tool]))
        print(f"  Deployed: {MONITOR_AGENT_NAME}")
    else:
        print(f"  Found existing: {MONITOR_AGENT_NAME}")
    if ADVISOR_AGENT_NAME not in existing:
        client.agents.create_version(agent_name=ADVISOR_AGENT_NAME, definition=PromptAgentDefinition(model=MODEL_DEPLOYMENT_NAME, instructions="You are an agricultural advisor with no tools. Use supplied evidence. Low soil moisture plus high temperature means irrigation stress; high humidity plus low pH means fungal or disease risk; multiple critical readings require urgent agronomist escalation."))
        print(f"  Deployed: {ADVISOR_AGENT_NAME}")
    else:
        print(f"  Found existing: {ADVISOR_AGENT_NAME}")
    client.close()
    return MONITOR_AGENT_NAME, ADVISOR_AGENT_NAME


def run_health_scan(monitor_agent_name: str) -> str:
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential
    from openai.types.responses.response_input_param import FunctionCallOutput

    client = AIProjectClient(endpoint=PROJECT_CONNECTION_STRING, credential=DefaultAzureCredential())
    openai_client = client.get_openai_client()
    conversation = openai_client.conversations.create()
    reference = {"agent_reference": {"name": monitor_agent_name, "type": "agent_reference"}}
    try:
        response = openai_client.responses.create(input=f"Check every crop zone. Zone IDs: {json.dumps(ZONE_IDS)}", conversation=conversation.id, extra_body=reference)
        while True:
            calls = [item for item in response.output if item.type == "function_call"]
            if not calls:
                return response.output_text
            outputs = []
            for call in calls:
                args = json.loads(call.arguments)
                outputs.append(FunctionCallOutput(type="function_call_output", call_id=call.call_id, output=check_health_monitor(args["zone_id"])))
            response = openai_client.responses.create(input=outputs, conversation=conversation.id, extra_body=reference)
    finally:
        openai_client.conversations.delete(conversation_id=conversation.id)
        client.close()


def run_advisor(advisor_agent_name: str, health_scan: str) -> str:
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential

    client = AIProjectClient(endpoint=PROJECT_CONNECTION_STRING, credential=DefaultAzureCredential())
    openai_client = client.get_openai_client()
    conversation = openai_client.conversations.create()
    try:
        response = openai_client.responses.create(input="Review this crop health scan and recommend actions and urgency:\n" + health_scan, conversation=conversation.id, extra_body={"agent_reference": {"name": advisor_agent_name, "type": "agent_reference"}})
        return response.output_text
    finally:
        openai_client.conversations.delete(conversation_id=conversation.id)
        client.close()


def run_smart_farm_workflow(monitor_agent_name: str, advisor_agent_name: str) -> dict:
    health_scan = run_health_scan(monitor_agent_name)
    advice = run_advisor(advisor_agent_name, health_scan)
    affected = [zone["zone_id"] for zone in _zones() if zone["status"] != "normal"]
    return {"health_scan": health_scan, "advisor": advice, "total_zones": len(ZONE_IDS), "affected_zones": affected}


def print_farm_report(report: dict):
    print("\n" + "=" * 60)
    print("GREENRISE AGRITECH SMART FARM HEALTH REPORT")
    print("=" * 60)
    print(f"  Zones checked      : {report['total_zones']}")
    print(f"  Zones needing care : {len(report['affected_zones'])}")
    print(f"  Affected zones     : {', '.join(report['affected_zones'])}")
    print("\n--- Crop Health Scan ---\n" + report["health_scan"])
    print("\n--- Agricultural Advice ---\n" + report["advisor"])
    print("=" * 60)


def create_workflow_agent(workflow_agent_name: str = WORKFLOW_AGENT_NAME) -> str:
    """Create a portal workflow; data is embedded because workflow steps cannot run local function loops."""
    from azure.ai.projects import AIProjectClient
    from azure.ai.projects.models import WorkflowAgentDefinition
    from azure.identity import DefaultAzureCredential

    client = AIProjectClient(endpoint=PROJECT_CONNECTION_STRING, credential=DefaultAzureCredential(), allow_preview=True)
    embedded = json.dumps(_zones(), indent=2).replace("\n", "\n        ")
    workflow_yaml = (
        "kind: Workflow\n"
        f"name: {workflow_agent_name}\n"
        "description: GreenRise smart farm crop health scan and agricultural advice\n"
        "trigger:\n"
        "  kind: OnConversationStart\n"
        "  id: trigger_start\n"
        "  actions:\n"
        "    - kind: InvokeAzureAgent\n"
        "      id: step_monitor\n"
        f"      agent:\n        name: {MONITOR_AGENT_NAME}\n"
        "      conversationId: =System.ConversationId\n"
        "      input:\n"
        f"        messages: |\n          Analyze these embedded GreenRise zone readings directly; do not call tools:\n          {embedded}\n"
        "      output:\n        autoSend: true\n"
        "    - kind: InvokeAzureAgent\n"
        "      id: step_advisor\n"
        f"      agent:\n        name: {ADVISOR_AGENT_NAME}\n"
        "      conversationId: =System.ConversationId\n"
        "      input:\n        messages: =step_monitor.output\n"
        "      output:\n        autoSend: true\n"
        "    - kind: EndConversation\n"
        "      id: step_end\n"
    )
    result = client.agents.create_version(agent_name=workflow_agent_name, definition=WorkflowAgentDefinition(workflow=workflow_yaml), description="GreenRise smart farm workflow")
    print(f"  Created workflow agent: {result.name} (version {result.version})")
    client.close()
    return result.name


def run_portal_workflow(workflow_name: str) -> str:
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential

    client = AIProjectClient(endpoint=PROJECT_CONNECTION_STRING, credential=DefaultAzureCredential(), allow_preview=True)
    openai_client = client.get_openai_client()
    embedded = json.dumps(_zones(), indent=2)
    conversation = openai_client.conversations.create()
    try:
        response = openai_client.responses.create(input="Analyze this embedded smart farm data directly; do not call check_health_monitor. Detect anomalies, then recommend agronomic actions.\n" + embedded, conversation=conversation.id, extra_body={"agent_reference": {"name": workflow_name, "type": "agent_reference"}}, background=True)
        for _ in range(12):
            time.sleep(8)
            response = openai_client.responses.retrieve(response.id)
            if response.status in ("completed", "failed", "cancelled"):
                break
        print(response.output_text or "Workflow returned no text; inspect the portal run history.")
        return response.output_text or ""
    finally:
        openai_client.conversations.delete(conversation_id=conversation.id)
        client.close()


def main():
    if not PROJECT_CONNECTION_STRING:
        print("PROJECT_CONNECTION_STRING not set. Run challenge 0 first!")
        sys.exit(1)
    monitor, advisor = ensure_agents_deployed()
    report = run_smart_farm_workflow(monitor, advisor)
    print_farm_report(report)
    workflow = create_workflow_agent()
    run_portal_workflow(workflow)


if __name__ == "__main__":
    main()
