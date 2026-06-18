#!/usr/bin/env bash
# Update GitHub repository descriptions and topics for amarkum/* repos.
# Prerequisite: gh auth login (one-time)
set -euo pipefail

if ! gh auth status >/dev/null 2>&1; then
  echo "Not logged in. Run: gh auth login"
  exit 1
fi

OWNER="${GITHUB_OWNER:-amarkum}"

repo_exists() {
  gh repo view "${OWNER}/$1" >/dev/null 2>&1
}

update_description() {
  local repo="$1"
  local desc="$2"
  echo "  description..."
  gh repo edit "${OWNER}/${repo}" --description "$desc"
}

update_topics() {
  local repo="$1"
  shift
  local args=()
  for topic in "$@"; do
    args+=(--add-topic "$topic")
  done
  echo "  topics: $*"
  gh repo edit "${OWNER}/${repo}" "${args[@]}"
}

update_repo() {
  local repo="$1"
  local desc="$2"
  shift 2
  if ! repo_exists "$repo"; then
    echo "Skipping ${OWNER}/${repo} (not found or no access)"
    return 2
  fi
  echo "Updating ${OWNER}/${repo}..."
  update_description "$repo" "$desc"
  if ((${#@} > 0)); then
    update_topics "$repo" "$@"
  fi
}

updated=0
skipped=0
failed=0

run() {
  if update_repo "$@"; then
    updated=$((updated + 1))
  else
    code=$?
    if [[ "$code" -eq 2 ]]; then
      skipped=$((skipped + 1))
    else
      failed=$((failed + 1))
    fi
  fi
}

run stackcone \
  "Official website for stackcone — custom software & AI development (RAG, web, mobile, cloud). Static site for stackcone.com." \
  static-site html custom-software ai rag llm web-development software-agency

run rag-llm-chatbot \
  "Instruction document for designing and building a production RAG (Retrieval-Augmented Generation) chatbot" \
  rag llm chatbot retrieval-augmented-generation ai documentation machine-learning

run money-world-trader-bot \
  "Unified web dashboard for automated trading — MT5 FX, Binance, and PancakeSwap bots with Markowitz portfolio optimization." \
  python flask trading-bot binance mt5 cryptocurrency algorithmic-trading fintech

run xenfile \
  "FastAPI app with a browser UI and API for converting Markdown to PDF, with live preview." \
  fastapi python markdown pdf converter web-app

run aadhaya-self-drive-mobile-app \
  "Flutter mobile app for Aadhya Self Drive — fleet browse, booking, coupons, invoices, and Supabase backend (iOS & Android)." \
  flutter dart mobile-app supabase car-rental ios android

run Overvue \
  "A modern personal finance & life overview app to track net worth, spending capacity, debts, loans, habits, and overall financial health." \
  flutter dart personal-finance firebase firestore mobile-app net-worth

run upwork-proposal-write \
  "Upwork proposal workspace — cover letters, job summaries, and HTML/PDF templates tied to verified work history." \
  upwork freelance proposals html pdf templates

run cursor-resume-creator \
  "HTML resume builder and export templates created with Cursor — structured sections for PDF/print output." \
  resume html cursor pdf career

run interview-preprations \
  "Interview prep notes, question banks, and practice materials for technical and system-design interviews." \
  interview-preparation system-design coding-interviews notes

run special-marriage-act \
  "Private checklist and document package for court marriage under the Special Marriage Act, 1954." \
  python legal-documents personal india

run government-paper-work \
  "Personal tracker for Bengaluru property paperwork, GST registration, and ongoing compliance (EC, Khata, returns)." \
  gst property personal india compliance

run singapore-visa \
  "Private checklist, forms, and document tracker for a Singapore visa application." \
  visa travel personal singapore

run apple-edaakhil-case \
  "Apple consumer complaint case files (e-Jagriti) plus a Cloud Run service for scheduled email escalations." \
  python fastapi google-cloud-run consumer-rights automation email

run health-tracker \
  "Personal lab report tracker — ingest PDFs/CSVs, trend charts, and a FastAPI dashboard for health metrics over time." \
  python fastapi health dashboard lab-reports data-visualization

run proposal \
  "Private interactive single-page web app — a playful marriage proposal experience with mobile-friendly UI." \
  html single-page-app personal javascript css

run amarkum \
  "GitHub profile README for Amar Kumar — software engineer, AI/cloud full-stack, Upwork Expert-Vetted." \
  profile-readme portfolio software-engineering full-stack ai cloud upwork

echo ""
echo "Done. Updated: ${updated}, skipped: ${skipped}, failed: ${failed}"
