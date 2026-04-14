<p align="center">
  <img src="logo.png" alt="Command Claw Wiki" height="88">
</p>

<h1 align="center">Command Claw Wiki</h1>

<p align="center">
  <strong>An LLM-maintained personal knowledge base.</strong><br>
  <em>You curate sources. The LLM builds the wiki. Knowledge compounds.</em>
</p>

---

## What is this?

A template for building personal knowledge bases using LLMs, based on Andrej Karpathy's [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern.

Instead of re-deriving knowledge from raw documents on every query (RAG), the LLM **incrementally builds and maintains a persistent wiki** — a structured, interlinked collection of markdown files. When you add a source, the LLM reads it, extracts key information, and integrates it into the wiki — updating entity pages, revising summaries, flagging contradictions, and strengthening the evolving synthesis.

The wiki is a **persistent, compounding artifact**. Cross-references are already there. Contradictions are already flagged. The synthesis reflects everything ingested so far.

## Architecture

```
raw/                        # Your sources — immutable, LLM reads only
  assets/                   # Images, attachments
  sessions/                 # Auto-captured Claude Code session transcripts

wiki/                       # LLM-generated — entities, concepts, syntheses
  index.md                  # Content catalog (LLM's entry point for queries)
  log.md                    # Append-only timeline of all operations
  overview.md               # High-level map of the wiki
  sources/                  # One page per ingested raw source
  entities/                 # People, orgs, products, places
  concepts/                 # Ideas, frameworks, terminology
  comparisons/              # Side-by-side analyses
  syntheses/                # Query answers worth keeping
  templates/                # Page templates (Obsidian Templater compatible)

CLAUDE.md                   # Schema — tells the LLM how to maintain the wiki
PRD.md                      # The original pattern document
```

**Three layers:** raw sources (you curate), wiki pages (LLM maintains), schema (you co-evolve with the LLM).

## Getting started

### 1. Use this template

Click **"Use this template"** on GitHub to create a private repo for your wiki.

### 2. Open in Obsidian

Open the cloned repo as an Obsidian vault. The config files are included, but you need to install the community plugins on first launch:

1. Go to **Settings → Community plugins → Turn on community plugins**
2. Click **Browse** and install each plugin below
3. Enable all of them

| Plugin | Purpose |
|--------|---------|
| obsidian-git | Auto git sync |
| templater-obsidian | Auto-fill frontmatter on new pages |
| metadata-menu | YAML frontmatter management |
| obsidian-linter | Markdown formatting |
| obsidian-web-clipper | Clip web articles as markdown sources |

> **Note:** Plugin config is tracked in git but plugin binaries are not. This is a one-time setup per clone.

### 3. Add a source

Drop a document into `raw/` — articles, papers, notes, transcripts. The [Obsidian Web Clipper](https://obsidian.md/clipper) browser extension is great for grabbing web articles.

### 4. Ingest

Open Claude Code in the repo and say:

```
Ingest raw/my-article.md into the wiki
```

The LLM will:
- Read the source and discuss key takeaways with you
- Create `wiki/sources/<slug>.md` with a summary and citations
- Create or update relevant entity and concept pages (typically 10-15 pages per source)
- Update `wiki/index.md` and append to `wiki/log.md`

### 5. Query

Ask questions against the wiki. The LLM searches `wiki/index.md`, drills into relevant pages, and answers with citations. Good answers get filed as syntheses so they compound.

### 6. Lint

Periodically ask the LLM to health-check the wiki — find orphan pages, contradictions, stale claims, missing cross-references, and gaps worth investigating.

## The workflow

```
You curate sources ──> LLM ingests & maintains wiki ──> You browse in Obsidian
       ^                                                         │
       └─────────── Ask questions, direct analysis ──────────────┘
```

You never write wiki pages yourself. The LLM handles all the bookkeeping — summarizing, cross-referencing, filing, and maintenance. Your job is sourcing, directing, and asking the right questions.

## Use cases

- **Personal** — goals, health, psychology, self-improvement. Journal entries, articles, podcast notes.
- **Research** — deep-dive a topic over weeks. Papers, articles, reports building toward an evolving thesis.
- **Reading** — chapter-by-chapter companion wiki for a book. Characters, themes, plot threads, connections.
- **Business** — internal wiki fed by meeting transcripts, project docs, customer calls. Always current because maintenance costs nothing.
- **Learning** — course notes, concept maps, spaced repetition fodder.

## Schema

The schema lives in [`CLAUDE.md`](CLAUDE.md) (also symlinked as [`AGENTS.md`](AGENTS.md)). It defines page types, frontmatter conventions, operations (ingest/query/lint), and guardrails. Co-evolve it with the LLM as your conventions settle.

## License

MIT
