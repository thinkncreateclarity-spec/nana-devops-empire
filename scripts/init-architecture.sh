#!/usr/bin/env bash
set -euo pipefail

mkdir -p docs/adr docs/diagrams data/events data/features data/models

cat > docs/architecture.md <<'MD'
# Nana-Devops Architecture

## Purpose
A CI-driven operational intelligence system that turns workflow and subsystem events into health signals, artifacts, and decisions.

## Current State
- GitHub Actions runs the test matrix.
- Reports are generated in `reports/`.
- Health is summarized by `bin/test-decider`.

## System Layers
1. Event generation.
2. Event storage.
3. Analysis and scoring.
4. Control and decisioning.
5. Security and governance.
6. Documentation and traceability.

## Current Gaps
- No persistent event store yet.
- No adaptive learning loop yet.
- No formal security policy docs yet.
MD

cat > docs/security.md <<'MD'
# Security Posture

## Baseline
- SSH-only Git transport.
- No stale submodules in repo metadata.
- CI workflow uses guarded paths.
- GitHub Actions uses latest compatible runtime settings.

## Next Controls
- Threat model.
- Secrets inventory.
- Dependency review.
- Access control notes.
- Alerting for anomalous events.
MD

cat > docs/runbook.md <<'MD'
# Runbook

## Common Operations
- Run matrix locally.
- Inspect reports.
- Review failed workflow logs.
- Rerun CI.

## Failure Modes
- Missing directory paths.
- Stale submodule metadata.
- Analyzer returns no new reports.
- Artifact upload issues.
MD

cat > docs/adr/0001-event-model.md <<'MD'
# 0001 Event Model

## Context
The system emits test runs, analyzer output, warnings, and health decisions.

## Decision
Use a canonical event model for all operational signals.

## Consequences
- Easier ingestion.
- Better analytics.
- Shared schema across components.
MD

cat > docs/adr/0002-streaming-and-storage.md <<'MD'
# 0002 Streaming and Storage

## Context
Current reports are file-based and not replayable as a stream.

## Decision
Introduce a persistent event store before adding complex intelligence.

## Consequences
- Replay support.
- Historical learning.
- Better debugging.
MD

cat > docs/adr/0003-adaptive-learning.md <<'MD'
# 0003 Adaptive Learning

## Context
Static thresholds become brittle as the system evolves.

## Decision
Use feedback-driven adaptive scoring with supervised refinement.

## Consequences
- More resilient decisions.
- Requires labeled outcomes.
- Needs drift monitoring.
MD

cat > docs/adr/0004-fuzzy-control.md <<'MD'
# 0004 Fuzzy Control

## Context
Some states are ambiguous and should not be forced into binary logic.

## Decision
Use fuzzy supervisory rules for uncertain or partial-failure states.

## Consequences
- More explainable decisions.
- Less brittle automation.
- Requires rule tuning.
MD

cat > docs/adr/0005-security-posture.md <<'MD'
# 0005 Security Posture

## Context
The repo and workflow previously had stale metadata and fragile cleanup.

## Decision
Treat security and workflow hygiene as mandatory system controls.

## Consequences
- Safer CI behavior.
- Less operational drift.
- More documentation burden.
MD

cat > docs/diagrams/context.mmd <<'MD'
flowchart LR
  User[Developer] --> CI[GitHub Actions CI]
  CI --> Reports[reports/]
  CI --> Analyzer[bin/nana-analyze]
  Analyzer --> Health[bin/test-decider]
  Health --> Decision[Health Status]
MD

cat > docs/diagrams/architecture.mmd <<'MD'
flowchart TB
  E[Event Sources] --> I[Ingestion]
  I --> S[Storage]
  S --> A[Analysis]
  A --> C[Adaptive Control]
  C --> O[Operations]
  A --> D[Documentation/Reports]
  C --> Sec[Security Controls]
MD

cat > docs/diagrams/flow.mmd <<'MD'
sequenceDiagram
  participant GH as GitHub Actions
  participant TM as Test Matrix
  participant AN as Analyzer
  participant DC as Decider

  GH->>TM: run tests
  TM->>AN: write reports
  AN->>DC: summarize health
  DC-->>GH: GREEN / AMBER / RED
MD

echo "Architecture scaffold created."
