# CommandClaw Wiki — Schema

This repo is an **LLM-maintained wiki** following the pattern in [PRD.md](PRD.md).
You (the LLM) own the `wiki/` layer. The human curates `raw/` and asks questions.
Automation may also append machine-generated session transcripts into `raw/`.

## Layers

- `raw/` — immutable source documents (articles, papers, transcripts, notes). Read-only for the LLM. Images go in `raw/assets/`. Automated Claude session captures live in `raw/sessions/`.
- `wiki/` — LLM-generated markdown. Entities, concepts, summaries, syntheses. You create, update, and cross-link these freely.
- `CLAUDE.md` (this file) — the schema. Co-evolve it with the human as conventions settle.

## Wiki structure

```
wiki/
  index.md           # catalog of all pages (content-oriented)
  log.md             # append-only timeline (chronological)
  sources/           # one page per ingested raw source
  entities/          # people, orgs, products, places
  concepts/          # ideas, frameworks, terminology
  comparisons/       # side-by-side analyses
  syntheses/         # comparisons, analyses, query answers worth keeping
  overview.md        # high-level map of the wiki
  templates/         # authoritative page templates (copy when creating pages)
```

All new pages must be created in the correct subdirectory and must be based on
the matching template in `wiki/templates/`.

## Page conventions

- Filenames: `kebab-case.md`.
- Every page starts with YAML frontmatter:
  ```yaml
  ---
  title: Page Title
  type: source | entity | concept | synthesis | comparison | overview
  created: YYYY-MM-DD
  updated: YYYY-MM-DD
  sources: [source-slug-1, source-slug-2]
  tags: [tag1, tag2]
  ---
  ```
- Use Obsidian-style `[[wiki-links]]` for cross-references. Link aggressively — a page with no inbound links is a lint smell.
- Source pages cite the file in `raw/` they came from.
- When a claim is contradicted by a newer source, don't silently overwrite — note the contradiction and date it.

## Templates (authoritative)

When creating a new page, copy the matching template file, then fill it in:

- `wiki/templates/source.md` -> `wiki/sources/<slug>.md`
- `wiki/templates/entity.md` -> `wiki/entities/<slug>.md`
- `wiki/templates/concept.md` -> `wiki/concepts/<slug>.md`
- `wiki/templates/synthesis.md` -> `wiki/syntheses/<slug>.md`
- `wiki/templates/comparison.md` -> `wiki/comparisons/<slug>.md`
- `wiki/templates/overview.md` -> `wiki/overview.md` (keep updated)
- `wiki/templates/log-entry.md` -> append to `wiki/log.md`

## Operations

### Ingest
When the human drops a file in `raw/` and asks to ingest:
1. Read the source fully.
2. Discuss key takeaways with the human before writing.
3. Create `wiki/sources/<slug>.md` summarizing it with citations.
4. Update or create relevant `entities/` and `concepts/` pages. A single ingest commonly touches 10–15 pages.
5. Update or create `wiki/overview.md` if the high-level map should change.
6. Update `wiki/index.md` with any new pages using the normalized format below.
7. Append an entry to `wiki/log.md` using `wiki/templates/log-entry.md`.

### Session Capture
- Claude Code hooks may append raw transcripts and metadata to `raw/sessions/YYYY-MM-DD.md`.
- Treat these session files as raw sources: never hand-edit them, but they are valid inputs for later compilation into `wiki/`.
- Session capture is allowed to write under `raw/sessions/` even though the LLM otherwise treats `raw/` as immutable.

### Query
1. Read `wiki/index.md` first to locate relevant pages.
2. Drill into those pages; follow `[[links]]` as needed.
3. Answer with citations to wiki pages (and through them, `raw/` sources).
4. If the answer is a novel synthesis worth keeping, file it under `wiki/syntheses/` (or `wiki/comparisons/` for side-by-side analyses) and update the index + log.

### Lint
When asked to health-check:
- Contradictions between pages
- Stale claims superseded by newer sources
- Orphan pages (no inbound links)
- Concepts mentioned but lacking their own page
- Missing cross-references
- Gaps worth a web search

## Logging

`wiki/log.md` is append-only. Every entry starts with a consistent prefix so it's greppable:

```
## [YYYY-MM-DD] ingest | <source title>
## [YYYY-MM-DD] query  | <question>
## [YYYY-MM-DD] lint   | <summary>
```

Always append using the structure in `wiki/templates/log-entry.md`.

Quick recent-activity check: `grep "^## \[" wiki/log.md | tail -10`.

## Index format

`wiki/index.md` is content-oriented. It must be updated on every ingest or
new synthesis, and each entry must be:

- `- [[path-or-slug]] — One-line summary. (Optional metadata)`

Maintain the existing top-level sections: Overview, Sources, Entities, Concepts,
Syntheses, Comparisons. The Overview section must always include `[[overview]]`.

## Guardrails

- Never modify files in `raw/`.
- Never hand-edit `wiki/` content on behalf of the human without discussing — but do maintain it aggressively on your own initiative during ingests and queries.
- Prefer many small, well-linked pages over few long ones. The graph is the value.
- When uncertain about where a fact belongs, ask before writing.
