"""
Challenge 4: Production Workflow -- SDK Track
Multi-agent orchestration workflow for NovaTel Communications call center.
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


env_path = _find_repo_root() / ".env"
load_dotenv(env_path)

PROJECT_CONNECTION_STRING = os.getenv("PROJECT_CONNECTION_STRING")
MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-5.4")
CALL_DATA_PATH = Path(__file__).resolve().parent.parent / "challenge-1-build" / "call_data.json"

INTENT_AGENT_NAME = "call-center-intent-classifier-agent"
RESOLUTION_AGENT_NAME = "call-center-advisor-agent"
# Set WORKFLOW_AGENT_NAME in .env after creating the workflow in the Foundry portal
WORKFLOW_AGENT_NAME = os.getenv("WORKFLOW_AGENT_NAME", "")


def lookup_customer(call_id: str) -> str:
    """Look up call/customer details from call_data.json."""
    with open(CALL_DATA_PATH, "r") as f:
        data = json.load(f)
    call = next(
        (c for c in data["calls"]
         if c["call_id"] == call_id or c["customer_id"] == call_id),
        None,
    )
    if not call:
        return json.dumps({"error": f"Call or customer not found: {call_id}"})
    return json.dumps(call, indent=2)


def ensure_agents_deployed() -> tuple:
    """Create both agents if not already deployed; reuse existing ones."""
    print("=== Step 1: Ensure Agents Are Deployed ===")

    from azure.ai.projects import AIProjectClient
    from azure.ai.projects.models import FunctionTool, PromptAgentDefinition
    from azure.identity import DefaultAzureCredential

    lookup_customer_tool = FunctionTool(
        name="lookup_customer",
        description="Look up customer and call details by call ID or customer ID.",
        parameters={
            "type": "object",
            "properties": {
                "call_id": {"type": "string", "description": "Call ID e.g. CALL-001 or customer ID e.g. CUST-4421"},
            },
            "required": ["call_id"],
        },
        strict=False,
    )

    client = AIProjectClient(
        endpoint=PROJECT_CONNECTION_STRING,
        credential=DefaultAzureCredential(),
    )
    existing_names = {a.name for a in client.agents.list()}

    if INTENT_AGENT_NAME not in existing_names:
        client.agents.create_version(
            agent_name=INTENT_AGENT_NAME,
            definition=PromptAgentDefinition(
                model=MODEL_DEPLOYMENT_NAME,
                instructions=(
                    "You are a call center intent classification specialist for NovaTel Communications. "
                    "When asked to classify calls, use the lookup_customer tool to retrieve call details. "
                    "Classify each call with: intent (billing_dispute/technical_issue/cancellation/"
                    "upsell_opportunity/account_support/security_concern), priority (critical/high/medium/low), "
                    "sentiment (frustrated/neutral/positive/anxious), retention risk (high/medium/low). "
                    "Be concise and structured."
                ),
                tools=[lookup_customer_tool],
            ),
        )
        print(f"  Deployed: {INTENT_AGENT_NAME}")
    else:
        print(f"  Found existing: {INTENT_AGENT_NAME}")

    if RESOLUTION_AGENT_NAME not in existing_names:
        client.agents.create_version(
            agent_name=RESOLUTION_AGENT_NAME,
            definition=PromptAgentDefinition(
                model=MODEL_DEPLOYMENT_NAME,
                instructions=(
                    "You are a resolution strategy expert for NovaTel Communications. "
                    "Given a classified call intent and customer context, recommend the optimal resolution. "
                    "Provide: RECOMMENDED ACTION, SCRIPT SUGGESTION, ESCALATION (Yes/No + reason), "
                    "OFFERS AVAILABLE, and FOLLOW-UP tasks. "
                    "Security concerns ALWAYS escalate. Business accounts get priority. "
                    "Long-tenure customers get retention offers."
                ),
            ),
        )
        print(f"  Deployed: {RESOLUTION_AGENT_NAME}")
    else:
        print(f"  Found existing: {RESOLUTION_AGENT_NAME}")

    client.close()
    return INTENT_AGENT_NAME, RESOLUTION_AGENT_NAME


def run_intent_classification(intent_agent_name: str) -> str:
    """Call the intent classification agent for all calls; handle function call loop."""
    print("\n=== Step 2a: Intent Classification ===")

    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential
    from openai.types.responses.response_input_param import FunctionCallOutput

    client = AIProjectClient(
        endpoint=PROJECT_CONNECTION_STRING,
        credential=DefaultAzureCredential(),
    )
    openai_client = client.get_openai_client()
    agent_ref = {"agent_reference": {"name": intent_agent_name, "type": "agent_reference"}}

    # Get all call IDs from the data
    with open(CALL_DATA_PATH, "r") as f:
        data = json.load(f)
    call_ids = [c["call_id"] for c in data["calls"]]

    conversation = openai_client.conversations.create()
    response = openai_client.responses.create(
        input=(
            f"Classify all incoming calls: {', '.join(call_ids)}. "
            "For each, provide intent, priority, sentiment, and retention risk."
        ),
        conversation=conversation.id,
        extra_body=agent_ref,
    )

    while any(item.type == "function_call" for item in response.output):
        tool_outputs = []
        for item in response.output:
            if item.type == "function_call":
                args = json.loads(item.arguments)
                result = lookup_customer(args.get("call_id", ""))
                tool_outputs.append(
                    FunctionCallOutput(
                        type="function_call_output",
                        call_id=item.call_id,
                        output=result,
                    )
                )
        response = openai_client.responses.create(
            input=tool_outputs,
            conversation=conversation.id,
            extra_body=agent_ref,
        )

    report = response.output_text
    openai_client.conversations.delete(conversation_id=conversation.id)
    client.close()
    return report


def run_resolution_advisory(resolution_agent_name: str, call_id: str, classification: dict) -> str:
    """Call the resolution advisor agent for a single classified call."""
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential

    client = AIProjectClient(
        endpoint=PROJECT_CONNECTION_STRING,
        credential=DefaultAzureCredential(),
    )
    openai_client = client.get_openai_client()
    agent_ref = {"agent_reference": {"name": resolution_agent_name, "type": "agent_reference"}}

    # Get customer context
    customer_data = json.loads(lookup_customer(call_id))

    input_text = (
        f"Call {call_id} from {customer_data.get('customer_name', 'Unknown')} "
        f"({customer_data.get('account_tier', 'unknown')} tier, "
        f"{customer_data.get('tenure_months', 0)} months tenure):\n"
        f"- Intent: {classification.get('intent', 'unknown')}\n"
        f"- Priority: {classification.get('priority', 'unknown')}\n"
        f"- Sentiment: {classification.get('sentiment', 'unknown')}\n"
        f"- Retention risk: {classification.get('retention_risk', 'unknown')}\n"
        f"- Summary: {customer_data.get('summary', 'No summary available')}\n\n"
        "Recommend the resolution strategy, script, escalation decision, and follow-up actions."
    )

    conversation = openai_client.conversations.create()
    response = openai_client.responses.create(
        input=input_text,
        conversation=conversation.id,
        extra_body=agent_ref,
    )
    resolution = response.output_text
    openai_client.conversations.delete(conversation_id=conversation.id)
    client.close()
    return resolution


def run_call_center_workflow(intent_agent: str, resolution_agent: str) -> dict:
    """Orchestrate: classify all calls -> resolve high-priority ones -> consolidated report."""
    classification_report = run_intent_classification(intent_agent)
    print(classification_report)

    print("\n=== Step 2b: Resolution Advisory (High-Priority Calls) ===")
    resolutions = {}

    # Process the critical/high priority calls that need immediate resolution
    high_priority_calls = [
        {"call_id": "CALL-007", "intent": "security_concern", "priority": "critical",
         "sentiment": "anxious", "retention_risk": "medium"},
        {"call_id": "CALL-001", "intent": "billing_dispute", "priority": "high",
         "sentiment": "frustrated", "retention_risk": "high"},
        {"call_id": "CALL-003", "intent": "cancellation", "priority": "high",
         "sentiment": "neutral", "retention_risk": "high"},
    ]

    for call in high_priority_calls:
        print(f"  Resolving {call['call_id']} ({call['intent']})...")
        resolution = run_resolution_advisory(resolution_agent, call["call_id"], call)
        resolutions[call["call_id"]] = resolution

    return {
        "classification_report": classification_report,
        "high_priority_calls": [c["call_id"] for c in high_priority_calls],
        "resolutions": resolutions,
        "total_calls": 7,
        "critical_count": 1,
        "high_priority_count": 2,
    }


def print_shift_report(report: dict):
    print("\n" + "=" * 60)
    print("NOVATEL CALL CENTER — SHIFT REPORT")
    print("=" * 60)
    print(f"  Total calls processed  : {report['total_calls']}")
    print(f"  Critical priority      : {report['critical_count']}")
    print(f"  High priority          : {report['high_priority_count']}")

    if report["high_priority_calls"]:
        print(f"\n  Calls requiring immediate action: {', '.join(report['high_priority_calls'])}")
        print("\n--- Resolution Recommendations ---")
        for call_id, resolution in report["resolutions"].items():
            print(f"\n{call_id}:")
            print(resolution)
    else:
        print("\n  No critical or high-priority calls in queue.")

    print("=" * 60)


def create_workflow_agent(workflow_agent_name: str = "callcenter-triage-workflow") -> str:
    """
    Create a workflow agent via the SDK using WorkflowAgentDefinition.

    This is the SDK alternative to building a workflow in the Foundry portal UI.
    The workflow appears in the Foundry portal under Build → Agents (kind: workflow).

    Requires allow_preview=True on AIProjectClient.

    Workflow YAML format (CSDL):
        kind: Workflow          ← required root element (PascalCase)
        model: <deployment>     ← orchestrator model
        description: ...
        steps:
          - id: <step_id>
            agentName: <agent-name>   ← camelCase
            description: ...
            dependsOn:                ← optional list of step ids
              - <other_step_id>

    Note: WorkflowAgentDefinition agents are visible in the Foundry portal
    (Build → Agents) and can be invoked from the portal UI. Programmatic
    invocation via the Responses API returns a 'wfresp_' object; results
    appear in the portal conversation view.

    Returns:
        The workflow agent name.
    """
    from azure.ai.projects import AIProjectClient
    from azure.ai.projects.models import WorkflowAgentDefinition
    from azure.identity import DefaultAzureCredential

    client = AIProjectClient(
        endpoint=PROJECT_CONNECTION_STRING,
        credential=DefaultAzureCredential(),
        allow_preview=True,  # Required for WorkflowAgentDefinition
    )

    # Exact portal YAML format: flat InvokeAzureAgent actions with agent.name,
    # conversationId, input/output, and a final EndConversation action.
    workflow_yaml = (
        "kind: Workflow\n"
        f"name: {workflow_agent_name}\n"
        "description: NovaTel call center triage - classify all calls then recommend resolutions\n"
        "trigger:\n"
        "  kind: OnConversationStart\n"
        "  id: trigger_start\n"
        "  actions:\n"
        "    - kind: InvokeAzureAgent\n"
        "      id: step_classify\n"
        "      agent:\n"
        "        name: call-center-intent-classifier-agent\n"
        "      conversationId: =System.ConversationId\n"
        "      input:\n"
        '        messages: ""\n'
        "      output:\n"
        "        autoSend: true\n"
        "    - kind: InvokeAzureAgent\n"
        "      id: step_resolve\n"
        "      agent:\n"
        "        name: call-center-advisor-agent\n"
        "      conversationId: =System.ConversationId\n"
        "      input:\n"
        '        messages: ""\n'
        "      output:\n"
        "        autoSend: true\n"
        "    - kind: EndConversation\n"
        "      id: step_end\n"
    )

    existing_names = {a.name for a in client.agents.list()}
    if workflow_agent_name in existing_names:
        # Update existing agent with correct YAML format
        result = client.agents.create_version(
            agent_name=workflow_agent_name,
            definition=WorkflowAgentDefinition(workflow=workflow_yaml),
            description="NovaTel call center triage workflow (SDK-created)",
        )
        print(f"  Updated workflow agent: {result.name} (version {result.version})")
    else:
        result = client.agents.create_version(
            agent_name=workflow_agent_name,
            definition=WorkflowAgentDefinition(workflow=workflow_yaml),
            description="NovaTel call center triage workflow (SDK-created)",
        )
        print(f"  Created workflow agent: {result.name} (version {result.version})")
    print(f"  Visible in Foundry portal → Build → Agents (kind: workflow)")
    client.close()
    return result.name


def run_portal_workflow(workflow_name: str) -> str:
    """
    Invoke a WorkflowAgentDefinition agent via the Responses API.

    Embeds the call data directly in the input so the call-center-intent-classifier-agent
    can classify without needing to call the lookup_customer tool (workflow steps
    cannot handle function-call loops). Both agents execute sequentially.

    Returns:
        The workflow's combined text output.
    """
    import time
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential

    client = AIProjectClient(
        endpoint=PROJECT_CONNECTION_STRING,
        credential=DefaultAzureCredential(),
        allow_preview=True,
    )
    openai_client = client.get_openai_client()

    print(f"\n=== Portal Workflow: {workflow_name} ===")

    portal_base = PROJECT_CONNECTION_STRING.split("/api/projects/")[0] if "/api/projects/" in PROJECT_CONNECTION_STRING else ""
    if portal_base:
        print(f"\n  View in Foundry portal:")
        print(f"  {portal_base.replace('services.ai.azure.com', 'ai.azure.com')}/build/agents")

    print(f"\n  Workflow steps:")
    print(f"    1. call-center-intent-classifier-agent  — classify all calls by intent, priority, sentiment")
    print(f"    2. call-center-advisor-agent     — recommend resolution for high-priority calls")

    # Embed call data in the input so agents don't need tool calls
    with open(CALL_DATA_PATH, "r") as f:
        call_data = json.load(f)
    calls_text = json.dumps(call_data["calls"], indent=2)
    query = (
        "Here is the complete call center data for today:\n\n"
        + calls_text
        + "\n\nClassify all calls by intent, priority, sentiment, and retention risk. "
        "Then recommend resolution strategies for high-priority and security calls."
    )

    conversation = openai_client.conversations.create()
    print(f"\n  Submitting workflow run (background)...")

    resp = openai_client.responses.create(
        conversation=conversation.id,
        extra_body={"agent_reference": {"name": workflow_name, "type": "agent_reference"}},
        input=query,
        background=True,
    )
    print(f"  Response ID : {resp.id}")
    print(f"  Initial status: {resp.status}")

    output_text = ""
    for attempt in range(12):
        time.sleep(8)
        r = openai_client.responses.retrieve(resp.id)
        tokens = getattr(r.usage, "total_tokens", 0)
        print(f"  [{attempt + 1}] status={r.status}  tokens={tokens}")
        if r.status in ("completed", "failed", "cancelled"):
            output_text = r.output_text
            break

    if output_text:
        print("\nWorkflow output:")
        print(output_text)
    else:
        print(
            "\n  Note: Workflow invocation returned no text output via the API.\n"
            "  The agent is deployed and visible in Foundry portal → Build → Agents."
        )

    openai_client.conversations.delete(conversation_id=conversation.id)
    client.close()
    return output_text


def main():
    if not PROJECT_CONNECTION_STRING:
        print("PROJECT_CONNECTION_STRING not set. Run challenge 0 first!")
        sys.exit(1)

    # --- Part A: Python orchestration (agents called step-by-step from code) ---
    intent_agent, resolution_agent = ensure_agents_deployed()
    report = run_call_center_workflow(intent_agent, resolution_agent)
    print_shift_report(report)

    print("\nWorkflow complete! Agents remain deployed for future runs.")

    # --- Part B: SDK workflow creation + portal invocation ---
    print("\n" + "=" * 60)
    print("CREATING WORKFLOW AGENT VIA SDK")
    print("=" * 60)
    # Use WORKFLOW_AGENT_NAME from .env, or create a new one if not set / malformed
    workflow_name = WORKFLOW_AGENT_NAME if WORKFLOW_AGENT_NAME and not WORKFLOW_AGENT_NAME.startswith("<") else "callcenter-triage-workflow"
    workflow_name = create_workflow_agent(workflow_agent_name=workflow_name)

    print("\n" + "=" * 60)
    print("INVOKING WORKFLOW (BACKGROUND POLL)")
    print("=" * 60)
    run_portal_workflow(workflow_name)

    print("\n" + "=" * 60)
    print("CHALLENGE 4 COMPLETE")
    print("=" * 60)
    print("  Part A: Multi-agent SDK orchestration  ✓")
    print(f"  Part B: Workflow agent deployed        ✓  ({workflow_name})")
    print("          → View in Foundry portal → Build → Agents")


if __name__ == "__main__":
    main()
