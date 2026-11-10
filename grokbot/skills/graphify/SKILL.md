---
name: graphify
description: >-
  When the user types /graphify or asks for a knowledge graph or relationship
  map of files, docs, code, or a Notion KB: build it with the Graphify CLI
  installed on the shared box.
---
# /graphify

Graphify (open source, https://github.com/Graphify-Labs/graphify, pip package graphifyy) is installed on the shared box, so every bot can use it.

1. Run `export PATH=/home/box/.local/bin:$PATH` before any `graphify` command. If missing, reinstall with `uv tool install graphifyy`.
2. Full upstream instructions: `/home/box/tools/graphify-skill/SKILL.md`, sidecars in `/home/box/tools/graphify-skill/references/`. Read the upstream SKILL.md and follow it for the requested subcommand (build, query, path, explain, update).
3. For a Notion KB: first export the rows and their relations to markdown files in a folder under /workspace, never including accounts, passwords, tokens, or codes, then run the pipeline on that folder.
4. Outputs land in graphify-out/: graph.html (interactive), GRAPH_REPORT.md, graph.json. Attach graph.html or an --svg export and summarise hub nodes and clusters in the user's language.
5. Heavy builds go to a background worker.
