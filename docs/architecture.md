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
