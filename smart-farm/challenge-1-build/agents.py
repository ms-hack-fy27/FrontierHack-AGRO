"""
Challenge 1: Build Agents -- SDK Track
Agents for GreenRise AgroTech smart farm crop-zone health monitoring.
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FunctionTool, PromptAgentDefinition
from azure.identity import DefaultAzureCredential
from openai.types.responses.response_input_param import FunctionCallOutput


def _find_repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / ".env").exists():
            return parent
    return Path(__file__).resolve().parents[2]


REPO_ROOT = _find_repo_root()
load_dotenv(REPO_ROOT / ".env")
PROJECT_CONNECTION_STRING = os.getenv("PROJECT_CONNECTION_STRING")
MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-5.4")
DATA_PATH = Path(__file__).resolve().parent / "smart_farm_data.json"


def _load_zones() -> list[dict]:
    with open(DATA_PATH, "r", encoding="utf-8") as data_file:
        return json.load(data_file)["zones"]


def check_health_monitor(zone_id: str) -> str:
    """Compare one GreenRise AgroTech crop zone's four readings with its configured thresholds."""
    zone = next(
        (item for item in _load_zones() if item["zone_id"] == zone_id or item["name"] == zone_id),
        None,
    )
    if not zone:
        return json.dumps({"error": f"Crop zone '{zone_id}' not found"})

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
            direction = "above max" if value > threshold["max"] else "below min"
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


CHECK_CROP_HEALTH_TOOL = FunctionTool(
    name="check_health_monitor",
    description="Compare a GreenRise AgroTech crop zone's soil moisture, temperature, humidity, and pH with its thresholds and return threshold analysis.",
    parameters={
        "type": "object",
        "properties": {
            "zone_id": {"type": "string", "description": "Zone ID such as ZONE-ALPHA or the zone name"}
        },
        "required": ["zone_id"],
        "additionalProperties": False,
    },
    strict=False,
)


class CropHealthMonitorAgent:
    def __init__(self):
        self.agent = None
        self.client = None
        self.openai = None

    def create(self):
        self.client = AIProjectClient(endpoint=PROJECT_CONNECTION_STRING, credential=DefaultAzureCredential())
        self.openai = self.client.get_openai_client()
        instructions = """
You are the crop health monitor for GreenRise AgroTech. Always use check_health_monitor for every requested zone.
Return a structured status for each zone with zone ID, crop, status (normal, warning, or critical),
all four metrics, threshold comparisons, anomalies, and a recommended immediate next step.
Use the reported status as a signal but let the threshold analysis ground your explanation. Never invent readings.
"""
        self.agent = self.client.agents.create_version(
            agent_name="smart-farm-monitor-agent",
            definition=PromptAgentDefinition(model=MODEL_DEPLOYMENT_NAME, instructions=instructions, tools=[CHECK_CROP_HEALTH_TOOL]),
        )
        return self.agent

    def run(self, input_text: str) -> str:
        conversation = self.openai.conversations.create()
        try:
            reference = {"agent_reference": {"name": self.agent.name, "type": "agent_reference"}}
            response = self.openai.responses.create(input=input_text, conversation=conversation.id, extra_body=reference)
            while True:
                calls = [item for item in response.output if item.type == "function_call"]
                if not calls:
                    return response.output_text
                outputs = []
                for call in calls:
                    args = json.loads(call.arguments)
                    result = check_health_monitor(args["zone_id"]) if call.name == "check_health_monitor" else json.dumps({"error": "Unknown tool"})
                    outputs.append(FunctionCallOutput(type="function_call_output", call_id=call.call_id, output=result))
                response = self.openai.responses.create(input=outputs, conversation=conversation.id, extra_body=reference)
        finally:
            self.openai.conversations.delete(conversation_id=conversation.id)

    def cleanup(self):
        if self.agent:
            self.client.agents.delete_version(agent_name=self.agent.name, agent_version=self.agent.version)
        if self.client:
            self.client.close()


class AgriculturalAdvisorAgent:
    def __init__(self):
        self.agent = None
        self.client = None
        self.openai = None

    def create(self):
        self.client = AIProjectClient(endpoint=PROJECT_CONNECTION_STRING, credential=DefaultAzureCredential())
        self.openai = self.client.get_openai_client()
        instructions = """
You are an agricultural advisor for GreenRise AgroTech. You do not have tools; reason only from the
crop-zone health analysis supplied in the user message. Apply these domain patterns:
- low soil moisture plus high temperature indicates irrigation stress;
- high humidity plus low pH indicates fungal or disease risk;
- multiple critical readings require urgent agronomist escalation.
Give practical actions, urgency, and what to recheck. Distinguish evidence from hypotheses and do not invent data.
"""
        self.agent = self.client.agents.create_version(
            agent_name="smart-farm-advisor-agent",
            definition=PromptAgentDefinition(model=MODEL_DEPLOYMENT_NAME, instructions=instructions),
        )
        return self.agent

    def run(self, input_text: str) -> str:
        conversation = self.openai.conversations.create()
        try:
            response = self.openai.responses.create(
                input=input_text,
                conversation=conversation.id,
                extra_body={"agent_reference": {"name": self.agent.name, "type": "agent_reference"}},
            )
            return response.output_text
        finally:
            self.openai.conversations.delete(conversation_id=conversation.id)

    def cleanup(self):
        if self.agent:
            self.client.agents.delete_version(agent_name=self.agent.name, agent_version=self.agent.version)
        if self.client:
            self.client.close()


def main():
    if not PROJECT_CONNECTION_STRING:
        print("PROJECT_CONNECTION_STRING not set. Run challenge 0 first!")
        sys.exit(1)
    monitor = CropHealthMonitorAgent()
    advisor = AgriculturalAdvisorAgent()
    try:
        monitor.create()
        advisor.create()
        zone_ids = [zone["zone_id"] for zone in _load_zones()]
        result = monitor.run("Check every crop zone and return the structured status. Zone IDs: " + json.dumps(zone_ids))
        print("=== Crop Health Monitor ===\n" + result)
        print("=== Agricultural Advisor ===\n" + advisor.run(result))
    finally:
        monitor.cleanup()
        advisor.cleanup()


if __name__ == "__main__":
    main()
