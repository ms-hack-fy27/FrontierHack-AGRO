"""
Challenge 1: Build Agents -- SDK Track
Agents for GreenRise AgriTech smart farm crop-zone health monitoring.
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

class SmartFarmClassifierAgent:
    def __init__(self):
        self.agent = None
        self.client = None
        self.openai = None

    def create(self):
        self.client = AIProjectClient(endpoint=PROJECT_CONNECTION_STRING, credential=DefaultAzureCredential())
        self.openai = self.client.get_openai_client()
        instructions = """
 ## Purpose
-  You are AI assistant for GreenRise AgriTech that helps user to classify crops and zones.  Try load data via tools or use default thresholds = 
- soil_moisture = min: 30.0, max: 65.0
- temperature: min": 12.0, max: 30.0
- humidity:  min: 45.0, "max": 80.0
- ph_level: min: 6.0, "max": 7.0

##OutputFormat 
- Classification Summary table ONLY
- rows = for each zone.
- columns = for each metric
- use 🔴 for critical, ⚠️ for high, and ✅ for low.
- add column priority based on metrics classification

##Language
- Tone = direct
- Answer using same language used by customer

## Scope 
- Before answering, check if the request is related to this Purpose.
- If in scope: continue with conversation.
- If out of scope: do not answer the request content. Just explain your purpose                   

## Guardrails
- Do not create customer data.
- Do not recommend anything
- If key data is missing, ask precise follow-up questions.
"""
        self.agent = self.client.agents.create_version(
            agent_name="smart-farm-classifier-agent",
            definition=PromptAgentDefinition(model=MODEL_DEPLOYMENT_NAME, instructions=instructions),
        )
        return self.agent 
    
    def run(self, input_text: str) -> str:
        """Run agent with the given input."""
        conversation = self.openai.conversations.create()

        response = self.openai.responses.create(
            input=input_text,
            conversation=conversation.id,
            extra_body={"agent_reference": {"name": self.agent.name, "type": "agent_reference"}},
        )

        self.openai.conversations.delete(conversation_id=conversation.id)
        return response.output_text


class SmartFarmAdvisorAgent:
    def __init__(self):
        self.agent = None
        self.client = None
        self.openai = None

    def create(self):
        self.client = AIProjectClient(endpoint=PROJECT_CONNECTION_STRING, credential=DefaultAzureCredential())
        self.openai = self.client.get_openai_client()
        instructions = """
You are an agricultural advisor for GreenRise AgriTech. You do not have tools; reason only from the
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

def main():
    if not PROJECT_CONNECTION_STRING:
        print("PROJECT_CONNECTION_STRING not set. Run challenge 0 first!")
        sys.exit(1)
    
    classifier_agent = SmartFarmClassifierAgent()
    advisor_agent = SmartFarmAdvisorAgent()
    
    classifier_agent.create()
    advisor_agent.create()
    
    result = classifier_agent.run("""
Classify follow zones:
    Zone: ZONE-ALPHA
    Crop: Tomato
    Soil moisture: 52
    Temperature: 28
    Humidity: 60
    pH level: 6.5

    Zone: ZONE-BETA
    Crop: Lettuce
    Soil moisture: 70
    Temperature: 40
    Humidity: 90
    pH level: 8
""")
    print("=== Classifier Agent ===\n" + result)


if __name__ == "__main__":
    main()
