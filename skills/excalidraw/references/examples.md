# Complete Examples Reference

Full JSON examples showing proper element structure.

---

## 3-Tier Architecture Example

This is a REFERENCE showing JSON structure. Replace IDs, labels, positions, and colors based on discovered components.

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "claude-code-excalidraw-skill",
  "elements": [
    {
      "id": "user",
      "type": "ellipse",
      "x": 150,
      "y": 50,
      "width": 100,
      "height": 60,
      "angle": 0,
      "strokeColor": "#1971c2",
      "backgroundColor": "#e7f5ff",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": { "type": 2 },
      "seed": 1,
      "version": 1,
      "versionNonce": 1,
      "isDeleted": false,
      "boundElements": [{ "type": "text", "id": "user-text" }],
      "updated": 1,
      "link": null,
      "locked": false
    },
    {
      "id": "user-text",
      "type": "text",
      "x": 175,
      "y": 67,
      "width": 50,
      "height": 25,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 2,
      "version": 1,
      "versionNonce": 2,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "User",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 14,
      "containerId": "user",
      "originalText": "User",
      "lineHeight": 1.25
    },
    {
      "id": "frontend",
      "type": "rectangle",
      "x": 100,
      "y": 180,
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
      "seed": 3,
      "version": 1,
      "versionNonce": 3,
      "isDeleted": false,
      "boundElements": [{ "type": "text", "id": "frontend-text" }],
      "updated": 1,
      "link": null,
      "locked": false
    },
    {
      "id": "frontend-text",
      "type": "text",
      "x": 105,
      "y": 195,
      "width": 190,
      "height": 50,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 4,
      "version": 1,
      "versionNonce": 4,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "Frontend\nNext.js",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 14,
      "containerId": "frontend",
      "originalText": "Frontend\nNext.js",
      "lineHeight": 1.25
    },
    {
      "id": "database",
      "type": "rectangle",
      "x": 100,
      "y": 330,
      "width": 200,
      "height": 80,
      "angle": 0,
      "strokeColor": "#2f9e44",
      "backgroundColor": "#b2f2bb",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": { "type": 3 },
      "seed": 5,
      "version": 1,
      "versionNonce": 5,
      "isDeleted": false,
      "boundElements": [{ "type": "text", "id": "database-text" }],
      "updated": 1,
      "link": null,
      "locked": false
    },
    {
      "id": "database-text",
      "type": "text",
      "x": 105,
      "y": 345,
      "width": 190,
      "height": 50,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 6,
      "version": 1,
      "versionNonce": 6,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "Database\nPostgreSQL",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "baseline": 14,
      "containerId": "database",
      "originalText": "Database\nPostgreSQL",
      "lineHeight": 1.25
    },
    {
      "id": "arrow-user-frontend",
      "type": "arrow",
      "x": 200,
      "y": 115,
      "width": 0,
      "height": 60,
      "angle": 0,
      "strokeColor": "#1971c2",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 7,
      "version": 1,
      "versionNonce": 7,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1,
      "link": null,
      "locked": false,
      "points": [[0, 0], [0, 60]],
      "lastCommittedPoint": null,
      "startBinding": null,
      "endBinding": null,
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": true
    },
    {
      "id": "arrow-frontend-database",
      "type": "arrow",
      "x": 200,
      "y": 265,
      "width": 0,
      "height": 60,
      "angle": 0,
      "strokeColor": "#2f9e44",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": null,
      "seed": 8,
      "version": 1,
      "versionNonce": 8,
      "isDeleted": false,
      "boundElements": null,
      "updated": 1,
      "link": null,
      "locked": false,
      "points": [[0, 0], [0, 60]],
      "lastCommittedPoint": null,
      "startBinding": null,
      "endBinding": null,
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "elbowed": true
    }
  ],
  "appState": {
    "gridSize": 20,
    "viewBackgroundColor": "#ffffff"
  },
  "files": {}
}
```

---

## Layout Patterns

### Vertical Flow (Most Common)

```
Grid positioning:
- Column width: 200-250px
- Row height: 130-150px
- Element size: 160-200px x 80-90px
- Spacing: 40-50px between elements

Row positions (y):
  Row 0: 20   (title)
  Row 1: 100  (users/entry points)
  Row 2: 230  (frontend/gateway)
  Row 3: 380  (orchestration)
  Row 4: 530  (services)
  Row 5: 680  (data layer)
  Row 6: 830  (external services)

Column positions (x):
  Col 0: 100
  Col 1: 300
  Col 2: 500
  Col 3: 700
  Col 4: 900
```

### Horizontal Flow (Pipelines)

```
Stage positions (x):
  Stage 0: 100  (input/source)
  Stage 1: 350  (transform 1)
  Stage 2: 600  (transform 2)
  Stage 3: 850  (transform 3)
  Stage 4: 1100 (output/sink)

All stages at same y: 200
Arrows: "right" -> "left" connections
```

### Hub-and-Spoke

```
Center hub: x=500, y=350
8 positions at 45° increments:
  N:  (500, 150)
  NE: (640, 210)
  E:  (700, 350)
  SE: (640, 490)
  S:  (500, 550)
  SW: (360, 490)
  W:  (300, 350)
  NW: (360, 210)
```

---

## Complex Architecture Layout

```
Row 0: Title/Header (y: 20)
Row 1: Users/Clients (y: 80)
Row 2: Frontend/Gateway (y: 200)
Row 3: Orchestration (y: 350)
Row 4: Processing Services (y: 550)
Row 5: Data Layer (y: 680)
Row 6: External Services (y: 830)

Columns (x):
  Col 0: 120
  Col 1: 320
  Col 2: 520
  Col 3: 720
  Col 4: 920
```

---

## Diagram Complexity Guidelines

| Complexity | Max Elements | Max Arrows | Approach |
|------------|-------------|------------|----------|
| Simple | 5-10 | 5-10 | Single file, no groups |
| Medium | 10-25 | 15-30 | Use grouping rectangles |
| Complex | 25-50 | 30-60 | Split into multiple diagrams |
| Very Complex | 50+ | 60+ | Multiple focused diagrams |

**When to split:**
- More than 50 elements
- Create: `architecture-overview.excalidraw`, `architecture-data-layer.excalidraw`

**When to use groups:**
- 3+ related services
- Same deployment unit
- Logical boundaries (VPC, Security Zone)
