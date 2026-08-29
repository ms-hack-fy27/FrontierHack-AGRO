# 📞 Scenario: Call Center Triage — NovaTel Communications

## Contexto

![scenario](./images/scenario.png)

**NovaTel Communications** is a telecommunications provider handling hundreds of customer calls every day through its support center. Today's queue has 7 active calls covering different types of issues:

- **CALL-001** — Maria Gonzalez (Premium, 3 years) — Unexpected charge dispute
- **CALL-002** — James Liu (Basic, 4 months) — Internet dropping repeatedly
- **CALL-003** — Priya Sharma (Premium, 18 months) — Wants to cancel (moving)
- **CALL-004** — Robert Chen (Business, 2 years) — Adding 7 phone lines
- **CALL-005** — Sarah Mitchell (Basic, 5 years) — Can't navigate new app
- **CALL-006** — David Park (Premium, 1 year) — Charged for returned device
- **CALL-007** — Emma Wilson (Basic, 8 months) — Suspected account hack



## Your mission

![agentic-orchestration](./images/agentic-orchestration.png)

Build an AI agent system that:

1. **Classifies intent** — Determines what each customer needs (billing, technical support, cancellation, upsell, account support, security)
2. **Recommends a resolution** — Recommends the best service strategy based on the customer's context
3. **Produces a shift report** — Consolidated triage with prioritized action items

## Challenges

| # | Challenge | What you'll do | Time |
|---|-----------|---------------|------|
| 0 | [Setup](./challenge-0-setup/README.md) | Deploy the Microsoft Foundry infrastructure | 20 min |
| 1 | [Build agents](./challenge-1-build/README.md) | Build Intent Classification and Resolution Advisory agents | 30 min |
| 2 | [Monitor](./challenge-2-monitor/README.md) | Enable GenAI tracing with Application Insights | 20 min |
| 3 | [Evaluate](./challenge-3-evaluate/README.md) | Run systematic quality evaluations | 30 min |
| 4 | [Production workflow](./challenge-4-workflow/README.md) | Multi-agent orchestration and portal workflow | 20 min |

## Why the challenges are in this order

**Build first.** Intent classification only works when the agent has precise instructions and real account context. An agent that cannot distinguish a cancellation risk from a billing dispute will route calls incorrectly — sending retention offers to customers who only have a billing question and putting high-value accounts in the wrong queue. The `lookup_customer` tool provides the Intent Agent with real account data: tier, tenure, and open cases. Without it, the agent is only guessing.

**Monitor next.** A call triage system runs all day, processing hundreds of calls. Application Insights traces let you see what the agent actually did for each one — whether it called `lookup_customer`, how long it took, and exactly what it recommended. When a supervisor says, "the system gave the wrong guidance on CALL-007," the traces show you why.

**Evaluate next.** The test dataset has known-correct answers. Running the agents against it — before and after every change — gives you a score showing whether classification is improving or silently degrading. A prompt change that looks good on five spot-checked answers can still hurt accuracy on edge cases you did not check.

**Deploy next.** The portal workflow produces a shift report supervisors can act on: a prioritized queue, recommended actions, customer context, and a complete trace history. That is the difference between a manually run Python script and something the operations team trusts at the start of every shift.



## Arquitetura

![architecture](./images/architecture.png)

## Next steps

After completing these challenges, you will have a working multi-agent system with observability and evaluation configured. Here are some directions for taking it further:

**Deploy as a hosted agent endpoint**
Microsoft Foundry can host your agents as persistent, scalable API endpoints — with no infrastructure to manage. Once hosted, your telephony platform (Twilio, Genesys, Azure Communication Services) can send live call transcripts directly to the Intent Classification Agent and receive real-time triage decisions, replacing manual queue review.

**Add more tools to your agents**
This lab's `lookup_customer` function uses local mock data. In production, you would replace it with tools that call real systems:
- A `fetch_crm_history` tool that queries Salesforce or Dynamics 365 for the customer's complete interaction history
- A `check_active_offers` tool that retrieves current retention promotions and eligibility rules from a pricing API
- A `create_case` tool that automatically opens a CRM ticket and assigns it to the correct queue based on the Resolution Advisor's recommendation

**Create a knowledge base**
Upload NovaTel's customer service policy manual, resolution scripts, and product documentation to a Microsoft Foundry knowledge base. Attach it to the Resolution Advisor Agent as a File Search tool so its scripts are grounded in the approved manual — rather than an invented version.

**Integrate evaluations into CI/CD**
Run your evaluation set automatically on every pull request or deployment. If the coherence or relevance score falls below a threshold (for example, 3.5 out of 5), block the release. This prevents a system prompt edit or model update from silently reducing classification accuracy during peak hours.

**Explore advanced agent patterns**
- **Parallelize** intent classification across all 7 calls simultaneously instead of sequentially
- **Add confidence thresholds** — if the Intent Agent is unsure whether a call is about cancellation or billing, flag it for human review instead of assigning it automatically
- **Human in the loop** — always route CALL-007 (security incidents) to a human supervisor, regardless of the agent's confidence level

**Tune for your domain**
Use evaluation results to identify systematic errors — intent types the agent consistently confuses or customer segments it serves poorly. Use these cases to refine system prompts, add targeted few-shot examples, or fine-tune the underlying model with NovaTel call transcripts.
