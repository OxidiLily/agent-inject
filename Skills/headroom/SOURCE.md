# Provenance

Vendored from https://github.com/headroomlabs-ai/headroom
Commit: e27f0d96cc3032d5f2c510ac97545553b867a697 (2026-11-20)
Path upstream: skills/headroom/SKILL.md
License: Apache-2.0 (upstream repo; NOTICE file applies)

Only the skill file is vendored. The tool itself (Python lib + Rust crates, ~108 MB
repo) is installed separately, e.g. `uv tool install headroom-ai` / `pipx install headroom-ai`.
Do not vendor the whole repo into a small-device install.

Update: re-fetch skills/headroom/SKILL.md at the pinned commit.
