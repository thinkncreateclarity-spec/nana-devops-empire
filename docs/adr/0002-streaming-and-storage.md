# 0002 Streaming and Storage

## Context
Current reports are file-based and not replayable as a stream.

## Decision
Introduce a persistent event store before adding complex intelligence.

## Consequences
- Replay support.
- Historical learning.
- Better debugging.
