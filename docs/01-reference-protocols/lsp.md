# Reference protocol 2: Language Server Protocol (LSP)

## 1. What problem it solved

- **M×N problem**: M editors × N languages, each pair needing its own
  implementation of completion, go-to-definition, hover, diagnostics.
- Microsoft built LSP for VS Code (originating with the TypeScript server),
  published it openly (June 2016, with Codenvy and Red Hat as first partners)
  and it became the de-facto standard. Today: hundreds of servers, all major editors.

## 2. How it works

- **JSON-RPC 2.0** over stdio/sockets, with a simple base protocol
  (`Content-Length` header + JSON body).
- **Lifecycle**: `initialize` exchanges *client capabilities* and *server
  capabilities*. A server may support `textDocument/definition` but not
  `workspace/symbol`; the client adapts.
- **Requests** (need a reply): `textDocument/hover`, `completion`, `definition`,
  `references`. **Notifications** (fire and forget): `textDocument/didOpen`,
  `didChange`, `didClose`, `publishDiagnostics`.
- **Language-neutral abstraction**: LSP never standardises an AST. It talks in
  **URIs + (line, character) positions + text ranges**. That is why one protocol
  fits Python and C++ alike.

## 3. Why it succeeded (design lessons)

1. **Pick the neutral abstraction level.** Text documents and positions, not
   language internals. Everything language-specific stays inside the server.
2. **Capabilities negotiation** lets partial implementations be useful.
3. **Asynchronous by default**: diagnostics are pushed, editors stay responsive.
4. **Extensible without breaking**: new methods and optional fields; a server that
   ignores an unknown capability still works.
5. **One reference client (VS Code) + one reference server (TypeScript) at launch.**

## 4. LSP and AI agents (from the video + opencode docs)

- Claude Code exposes language servers via plugins (`/plugin`); Serena is an MCP
  server that wraps language servers for any agent.
- Agents use LSP to replace lossy text search (grep) with **precise semantic
  queries**: find references, get signatures and docs, read diagnostics after an
  edit. opencode feeds LSP diagnostics back into the agent loop as a correction
  signal, while warning that servers can desync, cost memory and vary by version.
- Video timestamps: 00:00 grep limitations; 01:38 installing LSP plugins; 02:14
  find-references demo; 03:52 Serena MCP; 04:29 querying parameters of
  `chat.completions.create`.

**Transfer to OIP:** an LLM looking at a medical image is in the same position
as an agent looking at code with only grep. It can *see* pixels, but it cannot
resolve "how many millimetres is this", "which side is the patient's left", or
"is this signal counts or attenuation". OIP is the "language server for images":
it answers those questions precisely, so the model does not have to guess.

## 5. What we copy from LSP

| LSP concept | OIP equivalent |
|---|---|
| Text document + position (neutral abstraction) | Image + **physical coordinate frame** (mm, orientation) + intensity semantics (units), independent of modality |
| `initialize` capability exchange | Conformance profile in the manifest (`oip.profile`, `oip.layers`) |
| `textDocument/hover` | `oip.describe(region)` — what is at this location, in what units |
| `textDocument/definition` | `oip.locate(structure)` — where is the heart / left lung / striatum |
| `publishDiagnostics` | `quality.flags` — missing spacing, burned-in text, lossy compression, unusual extent |
| Language server per language | Modality adapter per modality (DX/CR, NM, later CT/MR) behind one interface |

Sources: `docs/04-sources.md` §LSP.
