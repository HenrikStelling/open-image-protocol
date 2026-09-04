# Reference protocol 1: Model Context Protocol (MCP)

> Purpose of this note: dissect *how MCP was developed* and *how it makes foreign
> programs accessible to LLMs*, so we can copy the parts that transfer to imaging
> and avoid the parts that don't.

## 1. What problem it solved

- Before MCP, every AI application needed a bespoke connector for every data source
  or tool: the **N×M integration problem** (N assistants × M systems).
- Models were "trapped behind information silos and legacy systems" (Anthropic
  announcement, 25 Nov 2024). The reasoning got better, the *context* did not.
- MCP's framing: "a USB-C port for AI applications" — one plug, any device.

## 2. How it was developed (timeline and process)

| Date | Event | What we learn |
|---|---|---|
| 2024-11-05 | First spec version (`2024-11-05`). No mandatory auth for remote servers. | Ship a minimal, working core first. |
| 2024-11-25 | Public announcement + open source: spec, SDKs, Claude Desktop support, a repo of pre-built servers (Google Drive, Slack, GitHub, Postgres, Puppeteer). Early adopters: Block, Apollo; tool vendors Zed, Replit, Codeium, Sourcegraph. | Launch with **spec + SDKs + reference servers + a host that speaks it**, and with named adopters. |
| 2025-03-26 | OAuth 2.1 made mandatory for HTTP transports; Streamable HTTP transport. | Security arrives once remote use is real. |
| 2025-06-18 | Elicitation, structured tool output; batching removed (added only 3 months earlier). | Quarterly date-based releases caused churn and even feature removals. |
| 2025 | Governance formalised (SEP-001); project moved under Linux Foundation stewardship; SEP = "Specification Enhancement Proposal", reviewed by core maintainers every two weeks, requires a prototype implementation and community consensus. | Copy the SEP process: every change needs a prototype and consensus. |
| 2026 | SEP-1400 proposes semantic versioning to replace `YYYY-MM-DD`. | Date versions signal "breaking every quarter"; semver signals stability. |
| 2026-07-28 | Largest release: **stateless core** (every request carries protocol version + capabilities in `_meta`), mandatory `server/discover`, `subscriptions/listen` replaces ad-hoc notifications, feature lifecycle + deprecation policy, extensions (Tasks, Apps). Sampling and logging deprecated. | After ~20 months the protocol *simplified*: statelessness, discovery, explicit lifecycle. Design for this from day one. |

Creators: David Soria Parra and Justin Spahr-Summers (Anthropic).

## 3. Architecture (how an LLM reaches a foreign system)

```
Host (Claude, VS Code, ChatGPT)
 └── MCP Client  ── JSON-RPC 2.0 ──►  MCP Server (wraps the foreign system)
        (one client per server)          exposes: tools / resources / prompts
```

- **Two layers.** *Data layer* = JSON-RPC 2.0 messages, discovery, primitives.
  *Transport layer* = stdio (local) or Streamable HTTP (remote, OAuth).
  Same messages on every transport.
- **Discovery.** `server/discover` returns `supportedVersions`, `capabilities`
  (e.g. `tools.listChanged`), identity, and cache hints (`ttlMs`, `cacheScope`).
- **Server primitives** (what the foreign system offers):
  - `tools` — model-controlled functions with a **JSON Schema `inputSchema`**,
    a `name`, `title`, `description`. Results are a `content[]` array of typed parts
    (`text`, `image` (base64 + mimeType), embedded resource) and optionally
    `structuredContent` validated by an `outputSchema`.
  - `resources` — application-controlled, read-only data with a **URI** and
    **MIME type**; resource *templates* (`weather://forecast/{city}/{date}`) make
    them parametric and self-documenting.
  - `prompts` — user-controlled templates that show how to use the server.
- **Client primitives**: `elicitation` (ask the user), plus deprecated sampling/logging.
- **Notifications** via `subscriptions/listen` (opt-in, best-effort).

### The key mechanism: schema + description is the "translation"

MCP does not teach the model the foreign system's language. It forces the
foreign system to describe itself in a language the model already reads:
**JSON Schema + natural-language descriptions**. The host concatenates all
tools from all servers into one registry the model sees. Everything else
(auth, transport, state) is hidden from the model.

This is the single most transferable idea for OIP: *the image must describe
itself in JSON Schema-validated metadata plus natural-language descriptions,
and offer a small set of typed operations.*

## 4. What MCP deliberately does **not** standardise

- How the host uses the LLM or manages context ("MCP focuses solely on the
  protocol for context exchange").
- UI patterns.
- Domain semantics: a tool called `weather_current` means whatever its
  description says. MCP is domain-agnostic; **OIP must be domain-specific**
  (units, orientation, physics) — that is the gap OIP fills.

## 5. Lessons for OIP

1. **Ship spec + SDK + reference implementation + a host that consumes it, together.**
   For OIP: spec + Python SDK + `oip` CLI + an MCP server so any MCP host can consume OIP packages on day one.
2. **Self-description via JSON Schema + prose.** Every OIP field gets a schema *and* a description written for a model.
3. **Discovery / capability negotiation.** An OIP producer must declare which layers it filled (conformance profile), so consumers never guess.
4. **Semver + explicit deprecation** from the start (learn from the batching removal and SEP-1400).
5. **Stateless documents.** An OIP package must be interpretable on its own (no session state), exactly like the stateless 2026-07-28 MCP core.
6. **A governance process (SEP-style)** once there is more than one contributor: prototype + consensus before acceptance.
7. **Typed content parts.** MCP tool results already carry `image` + `text` + `structuredContent`; an OIP MCP server can return the canonical render, the context text, and the manifest in one result.

Sources: see `docs/04-sources.md` §MCP.
