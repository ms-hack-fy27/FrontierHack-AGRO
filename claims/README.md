# 📋 Scenario: AI Agents for Claims Processing

## Scenario

![scenario](./images/scenario.png)

You work at **ClaimSight Insurance**, a property and auto insurer that processes hundreds of claims every day. Each claim has associated metrics: document completeness, consistency between the damage and estimate, fraud risk score, and policy coverage match. Lately, fraudulent claims and processing delays have been costing the company millions.

Your mission: **build AI agents using Microsoft Foundry** that triage incoming claims and make intelligent processing decisions, flagging suspicious claims for investigation and speeding up legitimate ones.

![orchestration](./images/agentic-orchestration.png)

You will build two agents:

1. **Claims Triage Agent** — Assesses claim metrics against acceptable thresholds and flags anomalies
2. **Claims Decision Agent** — Receives flagged claims and recommends actions (approve, investigate, request documents, deny)

## The Claims

| Claim | Type | Claimant | Status |
|-------|------|----------|--------|
| CLM-001 | Auto Collision | Maria Torres | 🔴 Critical |
| CLM-002 | Property Water Damage | James Chen | ✅ Normal |
| CLM-003 | Auto Theft | Robert Kim | ⚠️ Warning |
| CLM-004 | Property Fire | Sarah Williams | ✅ Normal |
| CLM-005 | Auto Collision | David Okafor | ⚠️ Warning |

## Prerequisites

- **Azure subscription** with Contributor access
- **Python 3.10+** installed locally
- **Azure CLI** (`az`) installed and logged in (`az login`)
- A terminal (bash, PowerShell, or WSL)
- About 20 minutes to provision the infrastructure (run `azd provision` first from the `claims` folder!)

## Structure

All challenges use the Python SDK. Challenge 4 also walks you through the Foundry portal to visually create and test the multi-agent Workflow.

## Challenges

| # | Challenge | Duration | What you will do |
|---|-----------|----------|----------------|
| 0 | [Setup](./challenge-0-setup/README.md) | 20 min | Provision resources, verify authentication |
| 1 | [Build agents](./challenge-1-build/README.md) | 30 min | Build claims triage and decision agents |
| 2 | [Monitor](./challenge-2-monitor/README.md) | 20 min | Enable tracing, explore Application Insights |
| 3 | [Evaluate](./challenge-3-evaluate/README.md) | 30 min | Run evaluations, interpret quality metrics |
| 4 | [Workflow](./challenge-4-deploy/README.md) | 20 min | Create a multi-agent flow: triage → decision → claims report |

## Why the Challenges Are in This Order

**Build first.** Without precise instructions and real claims data, agents cannot make useful decisions. Without `assess_claim`, the Claims Triage Agent can only identify patterns in claim descriptions: there is no way to verify actual fraud scores, document completeness levels, or differences between damage and estimates. Ambiguous system prompts produce inconsistent decisions: the same risk profile might be approved one day and flagged the next.

**Monitor next.** Every decision made by the Claims Decision Agent must be traceable. For insurance claims, this is not optional: it is a business and regulatory requirement. Application Insights traces provide a complete record: what data the agent received, which tools it called, and exactly what it recommended. When an auditor asks why CLM-003 was sent for investigation, that trace is your answer.

**Evaluate next.** Two claims with the same fraud score and document completeness should receive the same recommendation. Evaluation provides a repeatable way to verify this and detects when a prompt update breaks that consistency before it affects real claims.

**Deploy next.** The portal workflow connects triage to decision-making, processes a complete batch of claims, and produces a report that compliance teams can approve. That is the difference between a demo and something you would put in front of a claims regulator.


## Arquitetura

![architecture](./images/architecture.png)


## Next Steps

After completing these challenges, you will have a functional multi-agent system with observability and evaluation configured. Here are some directions for taking it further:

**Deploy as a hosted agent endpoint**
Microsoft Foundry can host your agents as persistent, scalable API endpoints with no infrastructure for you to manage. Once hosted, your claims intake system can send new claims directly to the Triage Agent and receive a structured decision (approve / investigate / request documents / deny), without a manual triage step.

**Add more tools to your agents**
The `assess_claim` function in this lab uses local simulated data. In production, you would replace it with tools that call real systems:
- A `fetch_policy` tool that queries your policy management system for the exact coverage terms, exclusions, and limits that apply to a specific claim
- A `check_fraud_database` tool that queries a fraud intelligence service for known patterns matching the policyholder's history
- A `request_documents` tool that automatically triggers a document request workflow in your DMS when the agent makes that recommendation

**Create a knowledge base**
Upload ClaimSight's policy documents, regulatory compliance guidelines, and fraud pattern library to a Microsoft Foundry knowledge base. Attach it to the Claims Decision Agent as a File Search tool so its recommendations cite the actual policy language, producing decisions that are auditable and defensible before regulators.

**Integrate evaluations into CI/CD**
Run your evaluation dataset automatically on every pull request or deployment. If the coherence or relevance score falls below a threshold (for example, 3.5 out of 5), block the release. In a regulated industry, this is not just a best practice: it is the kind of quality gate that compliance and audit teams expect to see documented.

**Explore advanced agent patterns**
- **Parallelize** triage for all incoming claims instead of processing them sequentially
- **Add confidence thresholds**: if the Triage Agent's fraud risk assessment falls into an ambiguous range, route it to a senior claims reviewer instead of automatically passing it to the Decision Agent
- **Human in the loop**: for high-value claims (above a configurable threshold), always require approval from a human claims reviewer before executing the Decision Agent's recommendation

**Tune for your domain**
Use evaluation results to identify systematic errors, such as claim types the agent frequently judges incorrectly or fraud indicators it underweights. Use these cases to refine system prompts, add targeted few-shot examples, or fine-tune the underlying model using ClaimSight's historical claims decisions.
