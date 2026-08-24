"""
Challenge 1: Build Agents — SDK Track
Intent Classification Agent and Resolution Advisor Agent for NovaTel Communications.

Usage:
    python agents.py

Builds both agents with system prompts, tools, and conversation handling.
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


# Resolve repo root by finding .env in parent directories.
def _find_repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / ".env").exists():
            return parent
    return Path(__file__).resolve().parents[2]


REPO_ROOT = _find_repo_root()

# Load environment
env_path = REPO_ROOT / ".env"
load_dotenv(env_path)

PROJECT_CONNECTION_STRING = os.getenv("PROJECT_CONNECTION_STRING")
MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-5.4")
CALL_DATA_PATH = Path(__file__).resolve().parent / "call_data.json"


def _load_call_batch() -> list[dict]:
    """Load call records to send as a batch payload in demo requests."""
    with open(CALL_DATA_PATH, "r") as f:
        data = json.load(f)
    return data.get("calls", [])


# =============================================================================
# Tool Function: lookup_customer
# This is already implemented — agents can call this to get customer context
# =============================================================================

def lookup_customer(call_id: str) -> str:
    """
    Reads call_data.json and returns full context for a given call:
    customer info, account details, call summary, and history.
    """
    with open(CALL_DATA_PATH, "r") as f:
        data = json.load(f)

    call = None
    for c in data["calls"]:
        if c["call_id"] == call_id or c["customer_id"] == call_id:
            call = c
            break

    if not call:
        return json.dumps({"error": f"Call or customer '{call_id}' not found"})

    return json.dumps({
        "call_id": call["call_id"],
        "customer_id": call["customer_id"],
        "customer_name": call["customer_name"],
        "account_tier": call["account_tier"],
        "tenure_months": call["tenure_months"],
        "summary": call["summary"],
        "transcript_snippet": call["transcript_snippet"],
        "open_tickets": call["open_tickets"],
        "last_interaction": call["last_interaction"],
        "status": call["status"],
    }, indent=2)


# Tool definition for the agent (Foundry FunctionTool format)
LOOKUP_CUSTOMER_TOOL = FunctionTool(
    name="lookup_customer",
    description="Look up customer and call details by call ID (e.g., 'CALL-001') or customer ID (e.g., 'CUST-4421'). Returns account tier, tenure, call summary, transcript, and interaction history.",
    parameters={
        "type": "object",
        "properties": {
            "call_id": {
                "type": "string",
                "description": "The call ID (e.g., 'CALL-001') or customer ID (e.g., 'CUST-4421') to look up",
            }
        },
        "required": ["call_id"],
        "additionalProperties": False,
    },
    strict=False,
)


# =============================================================================
# Intent Classification Agent
# =============================================================================

class IntentClassificationAgent:
    def __init__(self):
        self.agent = None
        self.client = None
        self.openai = None

    def create(self):
        """Create the intent classification agent in Foundry."""
        self.client = AIProjectClient(
            endpoint=PROJECT_CONNECTION_STRING,
            credential=DefaultAzureCredential(),
        )
        self.openai = self.client.get_openai_client()

        system_prompt = """
        You are a call center intent classification specialist for NovaTel Communications.
        When asked to classify calls, use the lookup_customer tool to retrieve call details.
        For each call, determine:
        1. PRIMARY INTENT — one of:
           - billing_dispute: Unauthorized charges, refund requests, billing errors
           - technical_issue: Service outages, connectivity problems, device malfunctions
           - cancellation: Customer wants to cancel or is threatening to leave
           - upsell_opportunity: Customer wants to add services, upgrade, or expand
           - account_support: General questions, app help, navigation issues
           - security_concern: Fraud, unauthorized access, suspicious activity
        2. PRIORITY — critical / high / medium / low
        3. SENTIMENT — frustrated / neutral / positive / anxious
        4. RETENTION RISK — high / medium / low (likelihood customer will churn)

        Format your response as a structured classification for each call.
        Use 🔴 for critical, ⚠️ for high, and ✅ for low-risk items.
        """

        self.agent = self.client.agents.create_version(
            agent_name="call-center-intent-classifier-agent",
            definition=PromptAgentDefinition(
                model=MODEL_DEPLOYMENT_NAME,
                instructions=system_prompt,
                tools=[LOOKUP_CUSTOMER_TOOL],
            ),
        )

        return self.agent

    def run(self, input_text: str) -> str:
        """Run the intent classification agent with the given input."""
        conversation = self.openai.conversations.create()

        response = self.openai.responses.create(
            input=input_text,
            conversation=conversation.id,
            extra_body={"agent_reference": {"name": self.agent.name, "type": "agent_reference"}},
        )

        # Handle function call loops
        while True:
            function_calls = [item for item in response.output if item.type == "function_call"]
            if not function_calls:
                break

            input_list = []
            for item in function_calls:
                if item.name == "lookup_customer":
                    args = json.loads(item.arguments)
                    result = lookup_customer(args["call_id"])
                else:
                    result = json.dumps({"error": f"Unknown tool '{item.name}'"})

                input_list.append(
                    FunctionCallOutput(
                        type="function_call_output",
                        call_id=item.call_id,
                        output=result,
                    )
                )

            response = self.openai.responses.create(
                input=input_list,
                conversation=conversation.id,
                extra_body={"agent_reference": {"name": self.agent.name, "type": "agent_reference"}},
            )

        self.openai.conversations.delete(conversation_id=conversation.id)
        return response.output_text

    def cleanup(self):
        """Delete the agent version and close connections."""
        if self.agent:
            self.client.agents.delete_version(
                agent_name=self.agent.name,
                agent_version=self.agent.version,
            )
        if self.client:
            self.client.close()


# =============================================================================
# Resolution Advisor Agent
# =============================================================================

class ResolutionAdvisorAgent:
    def __init__(self):
        self.agent = None
        self.client = None
        self.openai = None

    def create(self):
        """Create the resolution advisor agent in Foundry."""
        self.client = AIProjectClient(
            endpoint=PROJECT_CONNECTION_STRING,
            credential=DefaultAzureCredential(),
        )
        self.openai = self.client.get_openai_client()

        system_prompt = """
        You are a resolution strategy expert for NovaTel Communications call center.
        Given a classified call intent and customer context, recommend the optimal resolution path.

        Your recommendations must consider:
        - Account tier (premium/business get priority handling and more flexibility)
        - Customer tenure (long-term customers get retention offers)
        - Open tickets (existing issues indicate repeat contact — escalate)
        - Sentiment and retention risk

        For each call, provide:
        1. RECOMMENDED ACTION — specific steps for the agent to take
        2. SCRIPT SUGGESTION — what to say to the customer (1-2 sentences)
        3. ESCALATION — Yes/No and reason
        4. OFFERS AVAILABLE — any credits, discounts, or retention offers to extend
        5. FOLLOW-UP — any post-call tasks (ticket creation, callback scheduling, etc.)

        Resolution guidelines by intent:
        - billing_dispute: Verify charge, offer immediate credit if under $100, escalate if over
        - technical_issue: Check known outages first, dispatch technician if persistent
        - cancellation: Offer retention package (discount/free month), escalate if business account
        - upsell_opportunity: Calculate savings, offer bundle discount, schedule follow-up
        - account_support: Walk through solution, offer callback if complex
        - security_concern: ALWAYS escalate to security team, lock account immediately

        Be concise and actionable. Format clearly with headers.
        """

        self.agent = self.client.agents.create_version(
            agent_name="call-center-advisor-agent",
            definition=PromptAgentDefinition(
                model=MODEL_DEPLOYMENT_NAME,
                instructions=system_prompt,
            ),
        )

        return self.agent

    def run(self, input_text: str) -> str:
        """Run the resolution advisor agent with the given input."""
        conversation = self.openai.conversations.create()

        response = self.openai.responses.create(
            input=input_text,
            conversation=conversation.id,
            extra_body={"agent_reference": {"name": self.agent.name, "type": "agent_reference"}},
        )

        self.openai.conversations.delete(conversation_id=conversation.id)
        return response.output_text

    def cleanup(self):
        """Delete the agent version and close connections."""
        if self.agent:
            self.client.agents.delete_version(
                agent_name=self.agent.name,
                agent_version=self.agent.version,
            )
        if self.client:
            self.client.close()


# =============================================================================
# Main — Test both agents
# =============================================================================

def main():
    if not PROJECT_CONNECTION_STRING:
        print("❌ PROJECT_CONNECTION_STRING not set. Run challenge 0 first!")
        sys.exit(1)

    print("=== Intent Classification Agent ===")
    print("Creating agent...")

    intent_agent = IntentClassificationAgent()
    intent_agent.create()
    print(f"✅ Created: {intent_agent.agent.name} (version {intent_agent.agent.version})")

    print("\nClassifying all incoming calls...")
    call_batch = _load_call_batch()
    call_ids = [call["call_id"] for call in call_batch]
    intent_result = intent_agent.run(
        "You are receiving a batch payload of calls for classification in one run. "
        "Use lookup_customer for each call_id in the payload, then provide the classification output.\n\n"
        f"BATCH_CALL_IDS: {json.dumps(call_ids)}\n"
        "BATCH_CALL_DATA:\n"
        f"{json.dumps(call_batch, indent=2)}"
    )
    print(intent_result)

    print("\n=== Resolution Advisor Agent ===")
    print("Creating agent...")

    resolution_agent = ResolutionAdvisorAgent()
    resolution_agent.create()
    print(f"✅ Created: {resolution_agent.agent.name} (version {resolution_agent.agent.version})")

    print("\nAdvising on high-priority batch of calls...")
    high_priority_batch = [
        call for call in call_batch if call["call_id"] in {"CALL-001", "CALL-006", "CALL-007"}
    ]
    resolution_result = resolution_agent.run(
        "You are receiving a batch payload of high-priority calls. For each call, provide: "
        "recommended action, script suggestion, escalation decision, available offers, and follow-up steps.\n\n"
        "HIGH_PRIORITY_CALL_BATCH:\n"
        f"{json.dumps(high_priority_batch, indent=2)}"
    )
    print(resolution_result)

    # Cleanup — comment out to keep agents visible in the Foundry portal
    # print("\nCleaning up agents...")
    # intent_agent.cleanup()
    # resolution_agent.cleanup()
    # print("✅ Done!")


if __name__ == "__main__":
    main()
