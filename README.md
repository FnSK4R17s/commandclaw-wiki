<p align="center">
  <img src="logo.png" alt="Command Claw Wiki" height="88">
</p>

<h1 align="center">Command Claw Wiki</h1>

<p align="center">
  <strong>The shared knowledge base for CommandClaw agents.</strong><br>
  <em>An LLM-maintained markdown wiki — sources, entities, concepts, syntheses — written through a disciplined service boundary.</em><br>
  <sub>One repo per deployment. Service-managed. Not for hand edits.</sub>
</p>

---

> [!WARNING]
> **🚧 Stub Repository** — This repo is scaffolded but not yet implemented. The schema, templates, and viewer stack will land per [PLAN.md](https://github.com/FnSK4R17s/commandclaw/blob/main/guiding_docs/PLAN.md) in the main `commandclaw` repo. Watch this space.
>
> 💬 **Have feedback or found a bug?** Reach out at [**@_Shikh4r_** on X](https://x.com/_Shikh4r_)

## What this is

`commandclaw-wiki` is a git repository that holds a structured, LLM-maintained knowledge base. It is **not** a per-agent vault — it is the cross-agent shared library. One wiki per CommandClaw deployment, written exclusively through the [commandclaw-memory](https://github.com/FnSK4R17s/commandclaw-memory) service.

The pattern follows Andrej Karpathy's [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) idea: instead of re-deriving knowledge from raw sources on every query, the LLM incrementally builds and maintains a persistent wiki of summaries, entity pages, concept pages, and syntheses. Cross-references are already there. Contradictions are already flagged. The wiki keeps getting richer with every source ingested.

CommandClaw adds enterprise discipline on top: every write to this repo goes through a schema-validated REST boundary in `commandclaw-memory`, so the wiki stays consistent regardless of which model is driving the agent.

## Repository layout

```
commandclaw-wiki/
├── README.md              # this file
├── AGENTS.md              # canonical schema reference (page types,
│                          # frontmatter, conventions, ingest workflow)
├── LICENSE                # MIT
├── index.md               # service-maintained content catalog
├── log.md                 # service-maintained append-only audit log
├── sources/               # one page per ingested raw source
├── entities/              # per-entity pages (people, projects, tools)
├── concepts/              # per-concept pages (abstract topics)
├── syntheses/             # cross-cutting LLM-generated analyses
└── _seed/                 # starter pages for fresh deployments
```

## How to read it

Three audiences, three viewers — see [PLAN.md §12](https://github.com/FnSK4R17s/commandclaw/blob/main/guiding_docs/PLAN.md) for the full spec.

| Audience | Viewer | How |
|---|---|---|
| **Operator / debug** | Obsidian | Open the repo as an Obsidian vault. Graph view, backlinks, search out of the box. |
| **Stakeholder / read-only** | Quartz static site | Built by GitHub Action on every push. Wikipedia-shaped browsable URL. |
| **CLI / scripts** | REST API or `cclaw wiki` | Direct HTTP to the memory service, or the CLI wrapper in `commandclaw`. |

None of the viewers writes to this repo. The only writer is `commandclaw-memory`.

## How to contribute

> **Do not edit pages in this repo by hand.** This repo is service-managed. Hand edits will conflict with the next service write and may be reverted.

To add content to the wiki, talk to the agent. Tell it:

> "Ingest this source into the wiki: \<URL or text\>"

The agent calls `wiki_ingest` on `commandclaw-memory`, which runs the source through the distillation pipeline and writes structured pages back to this repo.

To propose changes to the **schema** (page types, frontmatter, conventions), open a PR against [`AGENTS.md`](AGENTS.md). Schema changes are the one place hand edits are expected — they're the contract the service enforces.

## Related repos

| Repo | Purpose |
|------|---------|
| [commandclaw](https://github.com/FnSK4R17s/commandclaw) | Agent runtime, Telegram I/O, tracing |
| [commandclaw-mcp](https://github.com/FnSK4R17s/commandclaw-mcp) | MCP gateway — credential proxy with rotating keys |
| [commandclaw-memory](https://github.com/FnSK4R17s/commandclaw-memory) | Memory service — owns this wiki repo, validates writes, indexes, distills |
| [commandclaw-skills](https://github.com/FnSK4R17s/commandclaw-skills) | Skills library |
| [commandclaw-vault](https://github.com/FnSK4R17s/commandclaw-vault) | Per-agent vault template |
| [commandclaw-observe](https://github.com/FnSK4R17s/commandclaw-observe) | Observability stack |

## License

MIT
