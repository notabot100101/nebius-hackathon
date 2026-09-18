# (working title) Proof-First Personal Agent

> Status: work in progress for the **Nebius × NVIDIA Global AI Hackathon** (Personal AI track).

An always-on personal assistant whose signature feature is that it **verifies its own work**:
after every action it checks that the world actually changed (file written, command succeeded,
expected output present) and refuses to report success it cannot prove.

- Reasoning: an **NVIDIA Nemotron** open model served by **Nebius Token Factory**
- Memory: plain files the user owns and can read or edit
- Safety: capability whitelist plus a human gate on irreversible actions

## Quick start (Phase 0: stack check)

```bash
export NEBIUS_API_KEY=...        # from https://tokenfactory.nebius.com
python3 scripts/hello_nemotron.py
```

Standard library only. Prints which Nemotron models are available, runs one chat completion and
one tool-calling probe, and writes a key-free summary to `phase0-result.json`.

## License

Apache-2.0 (see `LICENSE`).
