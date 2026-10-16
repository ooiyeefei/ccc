# Editable diagrams and local MCP (CLI 1.17.0+)

Check `htmldrop --version` before using these commands. In edit mode, open **Diagrams**, create a canvas or import native `.excalidraw` JSON, draw or move shapes, then **Save diagram**. Supported Mermaid can be imported as new shapes; this is one-way, with no lossless canvas-to-Mermaid guarantee. The editor and fonts are bundled locally and load when opened.

Saving changes the registered local HTML, not its published copy. Use the existing publication workflow when the owner wants to share the update. With `--feedback`, published readers can select a shape beside its SVG preview and comment. Anchors retain stable shape IDs through moves and text changes, record the referenced revision, and keep removed-shape threads visibly marked.

## Review and source hand-off

Private edit reviewers use **Propose changes**; accepted HTML stays unchanged until the local owner accepts. Owners can accept or reject proposals and export local accepted revisions as native JSON or their matching SVG. Reviewers see only the current accepted revision and proposals based on the current source, and cannot export earlier local revisions. A stale source or diagram revision produces a conflict; export the draft before reopening the current diagram.

Current accepted scenes, document/diagram/shape IDs and static SVG previews are embedded in the HTML and survive publication and `pull`. Private proposals and unpublished diagram revisions remain encrypted in the original local profile; publishing does not upload those archives. Preserve that profile when local history matters. Published document history is separate and can retain earlier published diagram source. `push --password` uses the existing encryption model for accepted source and published history.

## Connect a local MCP client

First register the artifact:

```bash
htmldrop edit start /absolute/path/report.html --no-open
```

Configure the client's stdio MCP server (reviewer is the default):

```json
{
  "mcpServers": {
    "htmldrop": {
      "command": "htmldrop",
      "args": ["mcp", "--artifact", "/absolute/path/report.html"]
    }
  }
}
```

For owner-authorized accepted writes, append `"--role", "owner"` to `args`, or launch `htmldrop mcp --artifact /absolute/path/report.html --role owner`. The command stays running and speaks JSON-RPC on stdio. Each connection binds one already-registered HTML session; tools cannot select arbitrary paths, URLs or other sessions. There is no public remote MCP endpoint; private browser review uses `edit share`. Neither MCP role publishes or exposes edit-server controls.

Call `diagram_list`, then `diagram_read` for the current IDs and source hash. Reviewer tools read the current scene, history scope and comments, propose, comment on shapes and export the current revision. Explicit owner mode additionally exposes `diagram_create`, `diagram_save`, `diagram_accept` and `diagram_reject`. Mutations require `baseRevisionId` and `baseSourceHash`; creation requires only the source hash. A 409 conflict means reread and reconcile before retrying, never blindly overwrite.

Accepted create/save/accept operations require a fresh, safe SVG rendered from the exact scene, normally with browser `exportToSvg`. MCP has no renderer and must not invent or reuse a stale preview. Proposals may omit SVG; the owner acceptance UI renders it. Native JSON export needs no browser, while SVG export returns the stored preview for that precise revision.

## File boundaries

Keep the full accepted HTML within the existing **2 MB** limit; reduce embedded images or scene size if a save is refused. Diagram images must be embedded PNG, JPEG, WebP or GIF data. Shape links and web embeds are disabled. Published current previews remain readable without the editor service. This release does not provide simultaneous multiplayer.
