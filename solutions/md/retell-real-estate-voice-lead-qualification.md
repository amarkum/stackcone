# Conversational AI Voice System for Real Estate Lead Qualification

**By Amar Kumar**

This brief proposes a **real estate voice AI lead qualification** platform built on **Retell AI** and **Twilio**: a low-latency conversational stack that would handle inbound seller screening, outbound follow-up and nurturing calls, appointment setting, voicemail detection, and warm transfer to human agents — with structured lead records synced to the brokerage CRM.

**Proposed outcome:** A production voice pipeline where every call captures seller intent, property context, and timeline in CRM-ready JSON, routes hot leads to available agents within seconds, and leaves compliant voicemails or nurture callbacks when humans are unavailable — with sub-800 ms turn latency on live PSTN calls.

---

## Scenario

**Proposed solution** for a US real estate team or investor operation scaling seller outreach without hiring a full inside-sales floor.

- **Business model:** Residential brokerage, wholesaler, or iBuyer-style acquisition team qualifying motivated sellers
- **Call types:** Inbound from ads/yard signs/portal leads; outbound to aged CRM lists and form abandoners
- **Human team:** 2–8 licensed agents or acquisition reps; AI handles first touch and scheduling
- **CRM:** Follow Up Boss, kvCORE, HubSpot, or Salesforce with custom lead stages
- **Compliance:** TCPA consent tracking for outbound; call recording disclosure per state; DNC list checks before dial
- **POC gate:** Paid proof-of-concept demonstrating live voice, seller qualification script, and transfer logic before full build

## Problem

- **Missed inbound leads** — portal and ad leads call after hours; voicemail yields 5–10× lower contact rate than live answer
- **Rep time on unqualified sellers** — agents spend 15–20 minutes per call on curiosity callers with no timeline or equity
- **Outbound scale ceiling** — manual dialers cannot nurture 500+ aged leads without burnout or TCPA mistakes
- **Fragmented call notes** — transcripts live in Retell dashboard or rep memory, not CRM fields reps actually filter on
- **Latency kills trust** — >1.2 s response gaps feel robotic; sellers hang up before qualification completes
- **Transfer friction** — cold transfers drop context; agents re-ask address and motivation already captured
- **Voicemail inconsistency** — reps leave ad-hoc messages; no structured callback scheduling or CRM task creation

## Requirements

### Functional

- **Inbound qualification:** Retell agent on Twilio DID answers 24/7; captures address, condition, timeline, motivation, price expectation
- **Outbound follow-up:** Campaign dialer triggers Retell outbound calls from CRM segments with consent flags
- **Appointment setting:** Calendar tool books listing consultation or acquisition call with agent availability
- **Lead nurturing:** Multi-touch voice sequences (day 1, 3, 7) with script variants by lead temperature
- **Warm transfer:** `transfer_call` to agent ring group with whisper summary (address + motivation + timeline)
- **Voicemail handling:** AMD detects machine; leave compliant 25–30 s message; create CRM task for callback
- **Escalation rules:** High equity + 30-day timeline → immediate transfer; low intent → nurture queue
- **CRM write-back:** Post-call webhook pushes structured lead JSON and recording URL

### Non-functional

- **End-to-end turn latency:** Target 600–900 ms median (STT + LLM + TTS + telephony buffer)
- **Interruption handling:** Barge-in enabled; agent stops TTS when caller speaks
- **Availability:** 99.5% on Retell + Twilio managed services; orchestrator on redundant host
- **Audit:** Every call logged with `call_id`, lead_id, disposition, transfer outcome
- **Security:** PII encrypted at rest; webhook HMAC verification; secrets in vault
- **Testability:** Staging Retell agent + Twilio test numbers; recorded golden-path regression calls

## Architecture

Published HTML includes Mermaid diagrams (voice pipeline architecture, warm transfer sequence), pipeline strip, and four Chart.js charts.

```
Inbound/outbound PSTN → Twilio → Retell voice agent (STT/LLM/TTS)
Retell webhooks → Orchestrator (Node/FastAPI) → CRM + calendar + dialer queue
Hot lead → warm transfer → agent ring group
Voicemail → AMD branch → message + CRM task
```

## Recommended stack

| Layer | Tech | Why |
|-------|------|-----|
| Voice platform | Retell AI | Native telephony, interruption, transfer, AMD; lower integration tax than DIY STT/LLM/TTS |
| Telephony | Twilio Voice + SIP | US local DIDs, ring groups, recording, compliance APIs, mature AMD |
| LLM | OpenAI GPT-4o mini (live) / GPT-4o (complex) | Fast structured extraction; function calling for CRM and calendar |
| TTS | ElevenLabs `eleven_turbo_v2_5` (American voice) | Most natural US English prosody at low latency; Retell native integration |
| STT | Deepgram nova-2 (via Retell) | Strong telephony accuracy; barge-in friendly |
| Orchestration | Node.js Fastify or Python FastAPI | Retell webhooks, CRM adapters, campaign scheduler, idempotent writes |
| Memory | Redis (session) + PostgreSQL (leads) | Per-call dynamic variables; durable lead state and nurture cadence |
| CRM | Follow Up Boss API (or HubSpot) | Real-estate-native stages, tags, call logging |
| Calendar | Cal.com or Google Calendar API | Agent availability for appointment tool |
| Observability | Retell dashboard + custom Grafana/Looker | Latency, transfer rate, qualification completion |
| Dialer queue | BullMQ / Temporal | Outbound campaign pacing, TCPA window enforcement |

**Why Retell over raw Twilio + OpenAI Realtime?** Retell bundles turn-taking, interruption, AMD, and transfer primitives that would take weeks to reproduce reliably on PSTN.

**Why ElevenLabs over Cartesia/PlayHT?** ElevenLabs turbo models deliver the most convincing American conversational tone at Retell-compatible latency; Cartesia is a strong fallback if cost-at-scale dominates.

**Why custom orchestrator over Zapier?** Warm transfer context injection, TCPA gating, and idempotent CRM writes need code-level control and tests.

## Agent & component design

1. **Retell inbound qualification agent** — seller script, dynamic variables from CRM lookup by caller ID, tools: `update_lead`, `book_appointment`, `transfer_to_agent`, `schedule_callback`
2. **Retell outbound nurture agent** — variant prompts by `lead_temperature`; respects max attempts and local-time dial windows
3. **Orchestrator webhook service** — handles `call_started`, `call_ended`, `call_analyzed`; HMAC verify; maps Retell analysis to CRM fields
4. **Transfer router** — checks agent availability via calendar/CRM; whisper payload to receiving agent; fallback to voicemail + task if no answer in 25 s
5. **Voicemail branch** — AMD=true path; TTS message with callback number; creates CRM task due +4 business hours
6. **Campaign scheduler** — pulls CRM segments; enforces consent + DNC; rate-limits outbound Retell `create-phone-call` API
7. **QA harness** — 15 recorded seller personas; assert JSON schema fields populated; transfer triggered on hot-lead fixtures

## Implementation plan

1. **Phase 1 — Paid POC (week 1–2):** Staging Retell agent, one Twilio number, seller qualification script, live transfer to test mobile, demo recording
2. **Phase 2 — Inbound production (week 3–4):** Production DID, CRM webhook write-back, dynamic caller lookup, disclosure prompts
3. **Phase 3 — Outbound + nurture (week 5–6):** Campaign queue, TCPA consent checks, 3-touch cadence, disposition routing
4. **Phase 4 — Transfer + voicemail (week 7):** Ring group warm transfer, AMD voicemail script, agent whisper, no-answer fallback
5. **Phase 5 — Reporting + ops (week 8):** Dashboards, alert rules, runbooks, latency tuning (model + voice selection)
6. **Phase 6 — Hardening (week 9–10):** Load test outbound pacing, prompt regression suite, credential rotation, on-call playbook

## Reporting & ops

| Signal | Source | Cadence |
|--------|--------|---------|
| Median turn latency | Retell analytics + orchestrator spans | Daily during first month |
| Qualification completion rate | Calls with all required fields / total | Weekly |
| Warm transfer connect rate | Transfers answered / transfers attempted | Weekly |
| Hot-lead SLA | Time from hot disposition to agent connect | Real-time alert > 45 s |
| Outbound contact rate | Human/machine/no-answer | Per campaign |
| Voicemail callback completion | Tasks closed within 24 h | Weekly |
| CRM sync failures | Webhook error log | Immediate PagerDuty/Slack |

## Proposed deliverables

- Retell production agents (inbound + outbound) with ElevenLabs voice and tool definitions
- Twilio number pool, ring group, recording, and AMD configuration
- Orchestrator service with CRM adapter, webhook handlers, and nurture scheduler
- Seller qualification prompt pack + JSON schema for CRM field mapping
- Warm transfer runbook with whisper script and agent training one-pager
- Voicemail message templates per state disclosure rules
- Paid POC recording + live demo environment for stakeholder sign-off
- Grafana/Looker dashboard: latency, dispositions, transfer funnel
- Regression test suite (15 persona recordings + expected extractions)
- Operator runbook: pause campaigns, rotate API keys, handle CRM outage

## Effort estimate

| Scope | Hours (range) |
|-------|---------------|
| Phases 1–6 (POC through production hardening) | 180–280 hrs |
| Additional CRM (if Salesforce custom objects) | +30–50 hrs |
| Ongoing prompt tuning + new nurture scripts | 4–8 hrs/month |
| Platform costs (indicative monthly at moderate volume) | Retell minutes, Twilio, ElevenLabs, OpenAI — typically USD 800–2,500 at 2–5 k call minutes |

## Glossary

| Term | Meaning |
|------|---------|
| **Retell AI** | Voice-agent platform integrating telephony, STT, LLM, and TTS with transfer and AMD |
| **Warm transfer** | Handoff to human agent with AI-provided context whisper before caller is connected |
| **AMD** | Answering Machine Detection — Twilio/Retell signal distinguishing live human from voicemail |
| **Turn latency** | Time from caller stop-speaking to agent audio start — critical for natural dialog |
| **Barge-in** | Caller interruption while agent speaks; TTS stops immediately |
| **TCPA** | US Telephone Consumer Protection Act — governs outbound call/text consent |
| **Disposition** | Call outcome label: qualified, nurture, not interested, wrong number, transferred |
| **Dynamic variables** | Per-call Retell context (lead name, address, prior notes) injected into prompt |
| **Whisper** | Short agent-only audio summary played before bridging the seller |
