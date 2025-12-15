# Excalidraw JSON Format Reference

Complete reference for Excalidraw JSON structure and element types.

---

## File Structure

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "claude-code-excalidraw-skill",
  "elements": [],
  "appState": {
    "gridSize": 20,
    "viewBackgroundColor": "#ffffff"
  },
  "files": {}
}
```

---

## Element Types

| Type | Use For | Arrow Reliability |
|------|---------|-------------------|
| `rectangle` | Services, components, databases, containers, orchestrators, decision points | Excellent |
| `ellipse` | Users, external systems, start/end points | Good |
| `text` | Labels inside shapes, titles, annotations | N/A |
| `arrow` | Data flow, connections, dependencies | N/A |
| `line` | Grouping boundaries, separators | N/A |

### BANNED: Diamond Shapes

**NEVER use `type: "diamond"` in generated diagrams.**

Diamond arrow connections are fundamentally broken in raw Excalidraw JSON:
- Excalidraw applies `roundness` to diamond vertices during rendering
- Visual edges appear offset from mathematical edge points
- No offset formula reliably compensates
- Arrows appear disconnected/floating

**Use styled rectangles instead** for visual distinction:

| Semantic Meaning | Rectangle Style |
|------------------|-----------------|
| Orchestrator/Hub | Coral (`#ffa8a8`/`#c92a2a`) + strokeWidth: 3 |
| Decision Point | Orange (`#ffd8a8`/`#e8590c`) + dashed stroke |
| Central Router | Larger size + bold color |

---

## Required Element Properties

Every element MUST have these properties:

```json
{
  "id": "unique-id-string",
  "type": "rectangle",
  "x": 100,
  "y": 100,
  "width": 200,
  "height": 80,
  "angle": 0,
  "strokeColor": "#1971c2",
  "backgroundColor": "#a5d8ff",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 1,
  "opacity": 100,
  "groupIds": [],
  "frameId": null,
  "roundness": { "type": 3 },
  "seed": 1,
  "version": 1,
  "versionNonce": 1,
  "isDeleted": false,
  "boundElements": null,
  "updated": 1,
  "link": null,
  "locked": false
}
```

---

## Text Inside Shapes (Labels)

**Every labeled shape requires TWO elements:**

### Shape with boundElements

```json
{
  "id": "{component-id}",
  "type": "rectangle",
  "x": 500,
  "y": 200,
  "width": 200,
  "height": 90,
  "strokeColor": "#1971c2",
  "backgroundColor": "#a5d8ff",
  "boundElements": [{ "type": "text", "id": "{component-id}-text" }],
  // ... other required properties
}
```

### Text with containerId

```json
{
  "id": "{component-id}-text",
  "type": "text",
  "x": 505,                          // shape.x + 5
  "y": 220,                          // shape.y + (shape.height - text.height) / 2
  "width": 190,                      // shape.width - 10
  "height": 50,
  "text": "{Component Name}\n{Subtitle}",
  "fontSize": 16,
  "fontFamily": 1,
  "textAlign": "center",
  "verticalAlign": "middle",
  "containerId": "{component-id}",
  "originalText": "{Component Name}\n{Subtitle}",
  "lineHeight": 1.25,
  // ... other required properties
}
```

### DO NOT Use the `label` Property

The `label` property is for the JavaScript API, NOT raw JSON files:

```json
// WRONG - will show empty boxes
{ "type": "rectangle", "label": { "text": "My Label" } }

// CORRECT - requires TWO elements
// 1. Shape with boundElements reference
// 2. Separate text element with containerId
```

### Text Positioning

- Text `x` = shape `x` + 5
- Text `y` = shape `y` + (shape.height - text.height) / 2
- Text `width` = shape `width` - 10
- Use `\n` for multi-line labels
- Always use `textAlign: "center"` and `verticalAlign: "middle"`

### ID Naming Convention

Always use pattern: `{shape-id}-text` for text element IDs.

---

## Dynamic ID Generation

IDs and labels are generated from codebase analysis:

| Discovered Component | Generated ID | Generated Label |
|---------------------|--------------|-----------------|
| Express API server | `express-api` | `"API Server\nExpress.js"` |
| PostgreSQL database | `postgres-db` | `"PostgreSQL\nDatabase"` |
| Redis cache | `redis-cache` | `"Redis\nCache Layer"` |
| S3 bucket for uploads | `s3-uploads` | `"S3 Bucket\nuploads/"` |
| Lambda function | `lambda-processor` | `"Lambda\nProcessor"` |
| React frontend | `react-frontend` | `"React App\nFrontend"` |

---

## Grouping with Dashed Rectangles

For logical groupings (namespaces, VPCs, pipelines):

```json
{
  "id": "group-ai-pipeline",
  "type": "rectangle",
  "x": 100,
  "y": 500,
  "width": 1000,
  "height": 280,
  "strokeColor": "#9c36b5",
  "backgroundColor": "transparent",
  "strokeStyle": "dashed",
  "roughness": 0,
  "roundness": null,
  "boundElements": null
}
```

Group labels are standalone text (no containerId) at top-left:

```json
{
  "id": "group-ai-pipeline-label",
  "type": "text",
  "x": 120,
  "y": 510,
  "text": "AI Processing Pipeline (Cloud Run)",
  "textAlign": "left",
  "verticalAlign": "top",
  "containerId": null
}
```
