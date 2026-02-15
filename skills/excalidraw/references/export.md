# Export to PNG/SVG

Export `.excalidraw` files to PNG and/or SVG using Playwright MCP tools and `@excalidraw/utils`.

## Prerequisites

- Playwright MCP tools available: `browser_navigate`, `browser_run_code`, `browser_close`
- Python 3 installed (for local HTTP server)

## Procedure

### 1. Start a Local HTTP Server

A browser origin is required for dynamic ESM imports. Start a temporary server on any available port:

```bash
python3 -m http.server 8765 &
SERVER_PID=$!
```

### 2. Navigate Playwright to the Server

```
browser_navigate → http://localhost:8765/
```

The 404 page is fine — we only need the HTTP origin for the dynamic import to work.

### 3. Read the .excalidraw File

Use the Read tool to get the `.excalidraw` file contents as a string. This JSON string will be passed into the browser context in the next steps.

### 4. Export SVG

Use `browser_run_code` with the following pattern. Replace `EXCALIDRAW_JSON_HERE` with the actual JSON string from Step 3:

```javascript
async (page) => {
  const excalidrawJson = `EXCALIDRAW_JSON_HERE`;

  const svgString = await page.evaluate(async (json) => {
    const utils = await import('https://esm.sh/@excalidraw/utils@0.1.2');
    const { exportToSvg } = utils.default;
    const data = JSON.parse(json);
    const svg = await exportToSvg({
      elements: data.elements,
      appState: { ...data.appState, exportBackground: true },
      files: data.files || {}
    });
    return svg.outerHTML;
  }, excalidrawJson);

  return svgString;
}
```

Write the returned SVG string directly to `<filename>.svg` using the Write tool.

### 5. Export PNG

Use `browser_run_code` with the following pattern:

```javascript
async (page) => {
  const excalidrawJson = `EXCALIDRAW_JSON_HERE`;

  const pngBase64 = await page.evaluate(async (json) => {
    const utils = await import('https://esm.sh/@excalidraw/utils@0.1.2');
    const { exportToBlob } = utils.default;
    const data = JSON.parse(json);
    const blob = await exportToBlob({
      elements: data.elements,
      appState: { ...data.appState, exportBackground: true },
      files: data.files || {},
      mimeType: 'image/png'
    });
    const reader = new FileReader();
    return new Promise((resolve) => {
      reader.onloadend = () => resolve(reader.result);
      reader.readAsDataURL(blob);
    });
  }, excalidrawJson);

  return pngBase64;
}
```

The result is a base64 data URL. Decode and write to `<filename>.png`:

```bash
echo "<base64_data_without_prefix>" | base64 -d > <filename>.png
```

Strip the `data:image/png;base64,` prefix before decoding.

### 6. Clean Up

Close the browser and kill the HTTP server:

```
browser_close
```

```bash
kill $SERVER_PID
```

## Key Details

- **Import path**: Export functions are on `utils.default`, not named exports — this is how `esm.sh` wraps the `@excalidraw/utils` package
- **Console errors**: `<text> attribute y: Expected length` warnings are cosmetic — exports are valid
- **Background**: `exportBackground: true` includes the white background in exports
- **Output location**: Save exported files alongside the `.excalidraw` file with matching filename (e.g., `system-architecture.excalidraw` → `system-architecture.svg`, `system-architecture.png`)
- **Visual fidelity**: Both exports produce the same visual output as opening in excalidraw.com

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Port already in use | Try a different port: `python3 -m http.server 9876 &` |
| Dynamic import fails | Check network connectivity; `esm.sh` CDN must be reachable |
| Playwright tools not available | Ensure Playwright MCP server is configured and running |
| PNG is blank/corrupted | Verify the base64 prefix was stripped before decoding |
| SVG missing text | Cosmetic only — text renders correctly when opened in a browser |
