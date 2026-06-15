# AI Voice, SMS, and Worker Dispatch System for Service Businesses

**By Amar Kumar**

This brief proposes an **AI voice and SMS dispatch system** for a one-person field-service operation moving to a remote model: local sub-contractors perform on-site work while the owner manages bookings from another time zone. The architecture would combine **Vapi.ai** for inbound voice, **Twilio** for SMS, **Make.com** as the orchestration layer, **OpenAI** for unstructured text interpretation, and a job-management CRM such as **ServiceM8** or Tradify.

**Proposed outcome:** A hands-free dispatch pipeline where callers receive a booking link mid-call, paid web forms create provisional job cards, Make.com texts real-estate agents for access, and sub-contractors accept jobs via Y/N SMS — with WhatsApp escalation only when automation cannot resolve the thread.

---

## Scenario

**Proposed solution** for a solo operator in trades or inspections transitioning to remote management.

- **Business model:** One-person service business in Sydney, Australia, owner relocating overseas
- **Workforce:** Preferred and backup sub-contractors mapped by postcode
- **Customer entry:** Inbound phone calls; website form with payment
- **Access coordination:** Real-estate agents via SMS for lockbox codes and time slots
- **CRM:** ServiceM8, Tradify, or Google Sheets during migration
- **Escalation:** Owner WhatsApp for ambiguous threads or all-decline scenarios

## Problem

- Always-on phone burden when owner is in another time zone
- Fragmented booking path — call notes, form email, CRM status never linked
- Agent SMS ambiguity requires structured parsing or constant owner attention
- Manual sub-contractor chase across primary and backup contacts
- CRM hygiene — malformed addresses, provisional vs dispatched state drift
- Australian Privacy Act and SMS identification requirements for customer numbers

## Requirements

### Functional

- **Workflow 1:** Vapi answers inbound calls; mid-call SMS fires booking link via Twilio
- **Workflow 2:** Form payment webhook → Make → OpenAI address clean → provisional CRM job
- **Workflow 3A:** Auto-text agent for property access on new booking
- **Workflow 3B:** Inbound agent SMS → GPT-4o structured parse → router (yes / reschedule / escalate)
- **Workflow 3C:** Postcode subbie lookup → Y/N offer → 30-min timeout → backup → WhatsApp alert
- Job state machine: `provisional` → `access_pending` → `access_confirmed` → `dispatch_pending` → `dispatched` → `escalated`

### Non-functional

- Booking SMS during call &lt; 5 s; agent outbound within 60 s of form submit
- Idempotent webhooks; Australia/Sydney timezone storage
- Make execution history + `dispatch_log` audit sheet
- Staging Twilio numbers for E2E rehearsal

## Architecture

Published HTML includes Mermaid diagrams (system architecture, agent SMS sequence), pipeline strip, and four Chart.js charts.

```
Inbound call → Vapi → Twilio SMS (booking link)
Form + payment → Make booking-intake → ServiceM8 provisional job
Make access-dispatch hub → agent SMS → GPT parse → subbie Y/N → CRM dispatched
Escalation → owner WhatsApp
```

## Recommended stack

| Layer | Tech | Why |
|-------|------|-----|
| Voice AI | Vapi.ai + Twilio | Mid-call `send_sms` tool; natural dialog |
| SMS | Twilio Messaging | Inbound webhooks; delivery receipts |
| Orchestration | Make.com (3 scenarios) | Routers, sleep modules, OpenAI JSON |
| LLM parsing | OpenAI GPT-4o | Agent intent classification |
| CRM | ServiceM8 / Tradify | AU field-service job statuses + API |
| Roster | Google Sheet | Postcode → primary/backup subbies |
| Alerts | WhatsApp Business API | High-priority owner escalation |
| Audit | `dispatch_log` sheet | SMS thread + state transitions |

**Why Make over custom code?** Routers map to YES/alternate/NO branches; owner can inspect scenarios.

**Why Vapi over Twilio Studio?** Tool calls during live audio for mid-call SMS UX.

## Agent & component design

1. **Vapi inbound assistant** — owner script, `send_booking_link` tool, caller ID → SMS destination; landline fallback asks for mobile
2. **Make `booking-intake`** — payment webhook, dedupe, OpenAI address JSON, ServiceM8 create, wake dispatch scenario
3. **Make `access-dispatch` hub** — 3A outbound access, 3B inbound parse + router, 3C subbie offer with 30-min sleep
4. **OpenAI classifier** — `{ intent, lockbox_code, proposed_datetime, confidence }`; auto-act ≥ 0.85
5. **Subbie roster sheet** — postcode prefix, primary/backup name + mobile

## Implementation plan

| Phase | Weeks | Focus |
|-------|-------|-------|
| 1 | 1 | Discovery, CRM API, Twilio/Vapi/Make accounts, job status enum |
| 2 | 2 | Workflow 1: Vapi voice + mid-call SMS |
| 3 | 2–3 | Workflow 2: form → provisional job |
| 4 | 3–4 | Workflow 3A–3B: agent SMS loop + GPT router |
| 5 | 4–5 | Workflow 3C: subbie dispatch + E2E rehearsal |
| 6 | 5–6 | Error handlers, runbook, Loom handover, prod monitoring |

## Reporting & ops

- Vapi call volume + SMS tool success — daily digest first 14 days
- Make failures — immediate WhatsApp on CRM write failure
- Agent response time, subbie accept rate, escalation rate — weekly
- Booking funnel: calls → SMS → paid form → dispatched — monthly

## Proposed deliverables

- Vapi assistant on production Twilio number
- Three Make.com scenarios with staging clones
- OpenAI classifier prompt + JSON schema runbook
- CRM job template with agent mobile, lockbox, automation status fields
- Sub-contractor postcode roster sheet
- `dispatch_log` audit sheet
- WhatsApp escalation templates
- Recorded E2E test (call → form → mock agent YES → mock subbie Y)
- Operator runbook

## Effort estimate

| Scope | Hours |
|-------|-------|
| Phases 1–6 (full build + E2E test) | 70–110 hrs |
| CRM migration from Sheets only | +12–20 hrs |
| Ongoing tuning | 2–4 hrs/month |
| Platform costs (low volume) | ~AUD 150–350/month |

## Glossary

| Term | Meaning |
|------|---------|
| **Vapi** | Voice AI platform with server-side tool calling during live calls |
| **Provisional job** | Paid booking not yet confirmed for dispatch |
| **Router module** | Make.com branch node — one path per filter match |
| **Thread ID** | Correlation key linking inbound SMS to open job |
| **Sleep module** | Make delay step for sub-contractor timeout |
| **ServiceM8** | Australian field-service CRM with REST API |
