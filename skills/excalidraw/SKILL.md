---
name: excalidraw
description: Generate architecture diagrams as .excalidraw files from codebase analysis. Use when the user asks to create architecture diagrams, system diagrams, visualize codebase structure, or generate excalidraw files.
---

# Excalidraw Diagram Generator

Generate architecture diagrams as `.excalidraw` files directly from codebase analysis.

---

## Quick Start

**User just needs to ask:**
```
"Generate an architecture diagram for this project"
"Create an excalidraw diagram of the system"
"Visualize this codebase as an excalidraw file"
```

**Claude Code will:**
1. Analyze the codebase (any language/framework)
2. Identify components, services, databases, APIs
3. Map relationships and data flows
4. Generate valid `.excalidraw` JSON file **with dynamic IDs and labels**

**No prerequisites:** Works without existing diagrams, Terraform, or specific file types.

**Important:** This skill teaches the Excalidraw JSON structure. All component names, IDs, labels, positions, and colors are **dynamically generated** based on what Claude discovers in each unique codebase. The examples in this document are templates, not hardcoded outputs.

---

## When to Use

Use this skill when the user asks to:
- Generate architecture diagrams from code
- Create system diagrams, flowcharts, or component diagrams
- Visualize codebase structure
- Create `.excalidraw` files for documentation

---

## Critical Rules (Read First!)

### Quick Reference: Arrow Edge Calculations

**Before creating any arrow, calculate the edge points:**

| Shape Type | Edge | Formula |
|------------|------|---------|
| Rectangle | Top | `(x + width/2, y)` |
| Rectangle | Bottom | `(x + width/2, y + height)` |
| Rectangle | Left | `(x, y + height/2)` |
| Rectangle | Right | `(x + width, y + height/2)` |
| Diamond | Top vertex | `(x + width/2, y)` |
| Diamond | Bottom vertex | `(x + width/2, y + height)` |
| Diamond | Left vertex | `(x, y + height/2)` |
| Diamond | Right vertex | `(x + width, y + height/2)` |
| Ellipse | Top | `(x + width/2, y)` |
| Ellipse | Bottom | `(x + width/2, y + height)` |

**Arrow creation steps:**
1. Get source shape's edge point → this becomes arrow's `x, y`
2. Get target shape's edge point
3. Calculate relative offset: `target_edge - source_edge`
4. Build `points` array with elbow routing to reach the offset

---

### DO NOT use the `label` property!

The `label` property shown in some Excalidraw documentation is for the **JavaScript API** (`convertToExcalidrawElements`), NOT for raw `.excalidraw` JSON files!

**WRONG (will show empty boxes):**
```json
{
  "id": "my-box",
  "type": "rectangle",
  "label": { "text": "My Label" }  // ❌ DOES NOT WORK in raw JSON!
}
```

**CORRECT (requires TWO elements):**
```json
// 1. Shape with boundElements reference
{
  "id": "my-box",
  "type": "rectangle",
  "boundElements": [{ "type": "text", "id": "my-box-text" }]
},
// 2. Separate text element with containerId
{
  "id": "my-box-text",
  "type": "text",
  "containerId": "my-box",
  "text": "My Label"
}
```

### Use TRUE elbow arrows (90-degree corners), not curved arrows!

Excalidraw has THREE arrow types:
1. **Straight** - Direct line (2 points)
2. **Curved** - Smooth bends at corners (DEFAULT - what you get without `elbowed: true`)
3. **Elbow** - 90-degree sharp corners (requires `elbowed: true`)

**WRONG (creates CURVED arrows, not 90-degree elbows):**
```json
{
  "type": "arrow",
  "roughness": 1,
  "roundness": { "type": 2 },  // ❌ Creates curved/smooth corners
  "points": [[0, 0], [-280, 0], [-280, 125]]
}
```

**CORRECT (true 90-degree elbow arrows):**
```json
{
  "type": "arrow",
  "roughness": 0,           // ✅ Clean lines (no hand-drawn effect)
  "roundness": null,        // ✅ No rounding at corners
  "elbowed": true,          // ✅ CRITICAL: Enables 90-degree elbow mode
  "points": [[0, 0], [-280, 0], [-280, 125]]
}
```

**Three required properties for elbow arrows:**
1. `"elbowed": true` - Enables elbow arrow mode
2. `"roundness": null` - Removes curve smoothing at corners
3. `"roughness": 0` - Clean lines (optional but recommended)

---

## Excalidraw JSON Format Reference

### File Structure

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

### Element Types

| Type | Use For |
|------|---------|
| `rectangle` | Services, components, databases, containers |
| `ellipse` | Users, external systems, start/end points |
| `diamond` | Decision points, orchestrators, conditionals |
| `text` | Labels inside shapes, titles, annotations |
| `arrow` | Data flow, connections, dependencies |
| `line` | Grouping boundaries, separators |

### Required Element Properties

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

## Text Inside Shapes (Labels) - CRITICAL

**Every labeled shape requires TWO elements:**

### Step 1: Create the shape with `boundElements`

```json
// TEMPLATE - Replace {component-id} and colors based on discovered components
{
  "id": "{component-id}",           // e.g., "api-gateway", "postgres-db", "auth-service"
  "type": "rectangle",              // or "ellipse", "diamond" based on component type
  "x": 500,                         // Calculate based on grid position
  "y": 200,
  "width": 200,
  "height": 90,
  "angle": 0,
  "strokeColor": "#1971c2",         // Choose from color palette based on component type
  "backgroundColor": "#a5d8ff",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 1,
  "opacity": 100,
  "groupIds": [],
  "frameId": null,
  "roundness": { "type": 3 },
  "seed": 1,                        // Increment for each element
  "version": 1,
  "versionNonce": 1,
  "isDeleted": false,
  "boundElements": [{ "type": "text", "id": "{component-id}-text" }],
  "updated": 1,
  "link": null,
  "locked": false
}
```

### Step 2: Create the text element with `containerId`

```json
// TEMPLATE - Replace placeholders with actual component names from codebase analysis
{
  "id": "{component-id}-text",       // Must match the boundElements reference
  "type": "text",
  "x": 505,                          // shape.x + 5
  "y": 220,                          // shape.y + (shape.height - text.height) / 2
  "width": 190,                      // shape.width - 10
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
  "seed": 2,
  "version": 1,
  "versionNonce": 2,
  "isDeleted": false,
  "boundElements": null,
  "updated": 1,
  "link": null,
  "locked": false,
  "text": "{Component Name}\n{Subtitle}",  // e.g., "API Gateway\nExpress.js" or "PostgreSQL\nCloud SQL"
  "fontSize": 16,
  "fontFamily": 1,
  "textAlign": "center",
  "verticalAlign": "middle",
  "baseline": 14,
  "containerId": "{component-id}",   // Must match the shape's id
  "originalText": "{Component Name}\n{Subtitle}",
  "lineHeight": 1.25
}
```

### Text Positioning Tips

- Text `x` = shape `x` + 5 (small padding)
- Text `y` = shape `y` + (shape.height - text.height) / 2 (centered)
- Text `width` = shape `width` - 10 (padding on both sides)
- Use `\n` for multi-line labels
- Set `textAlign: "center"` and `verticalAlign: "middle"` for centered text

### Naming Convention

Always use pattern: `{shape-id}-text` for text element IDs.

### Dynamic ID Generation

**IDs and labels are generated from codebase analysis, NOT hardcoded:**

| Discovered Component | Generated ID | Generated Label |
|---------------------|--------------|-----------------|
| Express API server | `express-api` | `"API Server\nExpress.js"` |
| PostgreSQL database | `postgres-db` | `"PostgreSQL\nDatabase"` |
| Redis cache | `redis-cache` | `"Redis\nCache Layer"` |
| S3 bucket for uploads | `s3-uploads` | `"S3 Bucket\nuploads/"` |
| Lambda function | `lambda-processor` | `"Lambda\nProcessor"` |
| React frontend | `react-frontend` | `"React App\nFrontend"` |

**The skill teaches the JSON structure. Claude Code fills in actual values based on what it discovers in each unique codebase.**

---

## Arrows with Elbow Routing - CRITICAL

### Why Elbow Arrows?

Diagonal arrows create visual clutter when multiple arrows cross. Use orthogonal (elbow) routing for clean, professional diagrams.

### Arrow Connection Points - MUST Calculate from Shape Edges

**CRITICAL**: Arrows must start and end at shape **edges**, not centers. Floating/disconnected arrows are the #1 visual bug in generated diagrams.

#### Shape Edge Calculation Formulas

For any shape at position `(x, y)` with dimensions `(width, height)`:

**Rectangle Edge Points:**
```
Top center:    (x + width/2, y)
Bottom center: (x + width/2, y + height)
Left center:   (x, y + height/2)
Right center:  (x + width, y + height/2)
```

**Diamond Edge Points (vertices):**
```
Top vertex:    (x + width/2, y)
Bottom vertex: (x + width/2, y + height)
Left vertex:   (x, y + height/2)
Right vertex:  (x + width, y + height/2)
```

**Ellipse Edge Points (approximate):**
```
Top:    (x + width/2, y)
Bottom: (x + width/2, y + height)
Left:   (x, y + height/2)
Right:  (x + width, y + height/2)
```

#### Arrow Positioning Rules

1. **Arrow `x,y` = source shape's edge point** (where arrow starts)
2. **Final point in `points` array = offset to target shape's edge**
3. **`width` and `height`** = bounding box of the arrow path (absolute values of max offsets)

#### Worked Example: Rectangle to Rectangle (Vertical)

```
Source rectangle: x=500, y=200, width=180, height=90
Target rectangle: x=500, y=400, width=180, height=90
Connection: Bottom of source → Top of target

Step 1: Calculate source bottom edge
  source_bottom = (500 + 180/2, 200 + 90) = (590, 290)

Step 2: Calculate target top edge
  target_top = (500 + 180/2, 400) = (590, 400)

Step 3: Calculate arrow
  Arrow x = 590 (source edge x)
  Arrow y = 290 (source edge y)
  Distance to target = 400 - 290 = 110
  Points = [[0, 0], [0, 110]]
```

#### Worked Example: Diamond to Rectangle (Fan-out)

```
Diamond (orchestrator): x=570, y=400, width=140, height=80
Target rectangle: x=120, y=550, width=160, height=80
Connection: Bottom of diamond → Top of rectangle

Step 1: Calculate diamond bottom vertex
  diamond_bottom = (570 + 140/2, 400 + 80) = (640, 480)

Step 2: Calculate target top center
  target_top = (120 + 160/2, 550) = (200, 550)

Step 3: Calculate elbow arrow path
  Arrow x = 640, y = 480
  Horizontal offset to target x = 200 - 640 = -440
  Vertical offset to target y = 550 - 480 = 70

  For L-shape (down then left, or left then down):
  Points = [[0, 0], [-440, 0], [-440, 70]]  // Left first, then down
  OR
  Points = [[0, 0], [0, 70], [-440, 70]]    // Down first, then left
```

#### Worked Example: Callback/Return Arrow (U-turn)

```
Source shape: x=570, y=400, width=140, height=80 (diamond)
Target shape: x=550, y=270, width=180, height=90 (rectangle above)
Connection: Right of diamond → Right of rectangle (callback loop)

Step 1: Calculate diamond right vertex
  diamond_right = (570 + 140, 400 + 80/2) = (710, 440)

Step 2: Calculate rectangle right edge
  rect_right = (550 + 180, 270 + 90/2) = (730, 315)

Step 3: Calculate U-turn path
  Arrow x = 710, y = 440
  Need to go: right (to clear shapes), up, then left to target

  Points = [[0, 0], [50, 0], [50, -125], [20, -125]]
  // Right 50px, up 125px, left 30px to reach target
```

#### Multiple Arrows from Same Source - Staggering

When multiple arrows leave from the same shape edge, **stagger the start points** to prevent overlap:

```
Diamond at x=570, y=400, width=140, height=80
Bottom vertex = (640, 480)

Arrow 1 (leftmost target):  x=635, y=480  // Slightly left of center
Arrow 2 (left target):      x=638, y=480
Arrow 3 (center target):    x=640, y=480  // True center
Arrow 4 (right target):     x=642, y=480
Arrow 5 (rightmost target): x=645, y=480  // Slightly right of center
```

This creates a visual "fan" effect from the source shape.

#### Arrow Width/Height Calculation

The `width` and `height` properties of an arrow element represent the **bounding box** of the arrow path:

```
For points = [[0, 0], [-440, 0], [-440, 70]]:
  width = abs(-440) = 440
  height = abs(70) = 70

For points = [[0, 0], [50, 0], [50, -125], [20, -125]]:
  width = max(abs(50), abs(20)) = 50
  height = abs(-125) = 125
```

### Arrow Points Array

All coordinates in `points` are **relative** to the arrow's `x,y` position.

**Straight arrows (2 points):**
```json
{
  "type": "arrow",
  "x": 600,
  "y": 145,
  "points": [[0, 0], [0, 50]],
  "endArrowhead": "arrow"
}
// Goes straight down 50px
```

**L-shape left-then-down (3 points):**
```json
{
  "type": "arrow",
  "x": 525,
  "y": 420,
  "points": [[0, 0], [-325, 0], [-325, 125]],
  "endArrowhead": "arrow"
}
// Goes left 325px, then down 125px
```

**L-shape right-then-down (3 points):**
```json
{
  "type": "arrow",
  "x": 675,
  "y": 420,
  "points": [[0, 0], [325, 0], [325, 125]],
  "endArrowhead": "arrow"
}
// Goes right 325px, then down 125px
```

**S-shape for complex routing (4 points):**
```json
{
  "type": "arrow",
  "x": 340,
  "y": 295,
  "points": [[0, 0], [0, 400], [30, 400], [30, 530]],
  "endArrowhead": "arrow"
}
// Goes down 400px, right 30px, then down 130px more
```

### Elbow Arrow Patterns Reference

| Pattern | Points | Use Case |
|---------|--------|----------|
| Down | `[[0,0], [0,h]]` | Vertical connection |
| Right | `[[0,0], [w,0]]` | Horizontal connection |
| L-left-down | `[[0,0], [-w,0], [-w,h]]` | Go left, then down |
| L-right-down | `[[0,0], [w,0], [w,h]]` | Go right, then down |
| L-down-left | `[[0,0], [0,h], [-w,h]]` | Go down, then left |
| L-down-right | `[[0,0], [0,h], [w,h]]` | Go down, then right |
| S-shape | `[[0,0], [0,h1], [w,h1], [w,h2]]` | Navigate around obstacles |
| U-turn | `[[0,0], [w,0], [w,-h], [0,-h]]` | Callback/return arrows |

### Avoiding Arrow Overlaps

When multiple arrows leave from the same source:
1. **Stagger Y positions**: Start arrows at slightly different Y offsets (e.g., y: 420, y: 450, y: 455)
2. **Use different horizontal offsets**: First segment lengths should vary
3. **Color code by destination type**: Helps visual distinction

### Full Elbow Arrow Element Example

```json
{
  "id": "arrow-workflow-convert",
  "type": "arrow",
  "x": 525,
  "y": 420,
  "width": 325,
  "height": 125,
  "angle": 0,
  "strokeColor": "#7048e8",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "groupIds": [],
  "frameId": null,
  "roundness": null,
  "seed": 38,
  "version": 1,
  "versionNonce": 38,
  "isDeleted": false,
  "boundElements": null,
  "updated": 1,
  "link": null,
  "locked": false,
  "points": [[0, 0], [-325, 0], [-325, 125]],
  "lastCommittedPoint": null,
  "startBinding": null,
  "endBinding": null,
  "startArrowhead": null,
  "endArrowhead": "arrow",
  "elbowed": true
}
```

**Key elbow arrow properties (all three required for 90-degree corners):**
- `"roughness": 0` - Clean lines
- `"roundness": null` - Sharp corners (not curved)
- `"elbowed": true` - Enables true elbow arrow mode

---

## Color Palette (GCP-inspired)

| Component Type | Background | Stroke | Example |
|----------------|------------|--------|---------|
| Frontend/UI | `#a5d8ff` (blue) | `#1971c2` | Next.js, React apps |
| Backend/API | `#d0bfff` (purple) | `#7048e8` | API servers, processors |
| Database | `#b2f2bb` (green) | `#2f9e44` | PostgreSQL, Cloud SQL |
| Storage | `#ffec99` (yellow) | `#f08c00` | GCS, S3 buckets |
| AI/ML Services | `#e599f7` (magenta) | `#9c36b5` | Extractors, classifiers |
| External APIs | `#ffc9c9` (red) | `#e03131` | Gemini, OpenAI |
| Orchestration | `#ffa8a8` (coral) | `#c92a2a` | Workflows, schedulers |
| Validation | `#ffd8a8` (orange) | `#e8590c` | Validators, checkers |
| Network/Security | `#dee2e6` (gray) | `#495057` | VPC, IAM |
| Classification | `#99e9f2` (cyan) | `#0c8599` | Classifiers, routers |
| Users/Actors | `#e7f5ff` (light blue) | `#1971c2` | User ellipses |

---

## How to Use This Skill

### User Input Required

**Minimal input needed** - just ask Claude Code to generate an architecture diagram:

```
"Generate an architecture diagram for this project"
"Create an excalidraw diagram showing the system components"
"Visualize the codebase structure"
```

**Optional context** the user can provide:
- Focus area: "Focus on the API layer" or "Show the data pipeline"
- Output location: "Save to docs/architecture.excalidraw"
- Specific components: "Include the auth flow and database connections"

**NO prerequisites required:**
- Does NOT require existing Mermaid/D2 diagrams
- Does NOT require Terraform or specific IaC
- Works with any codebase (Node.js, Python, Java, etc.)

---

## Workflow

### Step 1: Analyze the Codebase

Before generating, understand:
1. What services/components exist?
2. How do they connect?
3. What is the data flow?
4. What external dependencies exist?

**Discovery patterns by codebase type:**

| Codebase Type | What to Look For |
|---------------|------------------|
| **Monorepo** | `packages/*/package.json`, workspace configs, shared libs |
| **Microservices** | `docker-compose.yml`, k8s manifests, service directories |
| **IaC (Terraform/Pulumi)** | Resource definitions, module structure, outputs |
| **Backend API** | Route definitions, controllers, middleware, DB models |
| **Frontend** | Component hierarchy, state management, API calls |
| **Full-stack** | Combination of above - identify frontend/backend split |

**Use tools to discover:**
- `Glob` → `**/package.json`, `**/Dockerfile`, `**/*.tf`, `**/docker-compose*.yml`
- `Grep` → `app.get`, `@Controller`, `def route`, `CREATE TABLE`, `createClient`
- `Read` → README, config files, entry points (`main.ts`, `index.js`, `app.py`)

### Step 2: Plan the Layout

Architecture diagrams typically flow:
- **Top-to-bottom**: Users → Frontend → Backend → Database
- **Left-to-right**: Input → Processing → Output

Grid positioning (recommended):
- Column width: 200-250px
- Row height: 130-150px
- Element width: 160-200px
- Element height: 80-90px
- Spacing: 40-50px between elements

### Step 3: Generate Elements

For each component:
1. Create the shape element with unique `id`
2. Add `boundElements` array referencing the text
3. Create matching text element with `containerId`
4. Position using grid coordinates
5. Choose appropriate color based on component type

### Step 4: Add Connections

For each relationship:
1. Calculate arrow start position (edge of source shape)
2. Plan elbow route to avoid overlaps
3. Create arrow with multi-point `points` array
4. Match stroke color to destination component type

### Step 5: Add Grouping (Optional)

For logical groupings:
1. Create large transparent rectangle
2. Use `strokeStyle: "dashed"`
3. Add standalone text label for group name

### Step 6: Write the File

Save as `.excalidraw` in the target location (usually `docs/` or alongside the code).

---

## Complete Example: 3-Tier Architecture

**This is a REFERENCE EXAMPLE showing JSON structure. When generating for a real codebase, replace all IDs, labels, positions, and colors based on discovered components.**

```json
// EXAMPLE OUTPUT - actual output will vary based on codebase analysis
{
  "type": "excalidraw",
  "version": 2,
  "source": "claude-code-excalidraw-skill",
  "elements": [
    {
      "id": "user",  // Generic "User" actor - present in most diagrams
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
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": { "type": 2 },
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
      "endArrowhead": "arrow"
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
      "roughness": 1,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": { "type": 2 },
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
      "endArrowhead": "arrow"
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

## Complex Architecture Pattern

For multi-service architectures (like microservices):

### Layout Strategy

```
Row 0: Title/Header (y: 20)
Row 1: Users/Clients (y: 80)
Row 2: Frontend/Gateway (y: 200)
Row 3: Orchestration (y: 350)
Row 4: Processing Services (y: 550)
Row 5: Data Layer (y: 680)
Row 6: External Services (y: 830)

Columns (x positions):
Col 0: 120
Col 1: 320
Col 2: 520
Col 3: 720
Col 4: 920
```

### Grouping with Dashed Rectangles

```json
{
  "id": "group-ai-pipeline",
  "type": "rectangle",
  "x": 100,
  "y": 500,
  "width": 1000,
  "height": 280,
  "angle": 0,
  "strokeColor": "#9c36b5",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "dashed",
  "roughness": 0,
  "opacity": 100,
  "groupIds": [],
  "frameId": null,
  "roundness": null,
  "seed": 12,
  "version": 1,
  "versionNonce": 12,
  "isDeleted": false,
  "boundElements": null,
  "updated": 1,
  "link": null,
  "locked": false
},
{
  "id": "group-ai-pipeline-label",
  "type": "text",
  "x": 120,
  "y": 510,
  "width": 280,
  "height": 25,
  "angle": 0,
  "strokeColor": "#9c36b5",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "groupIds": [],
  "frameId": null,
  "roundness": null,
  "seed": 13,
  "version": 1,
  "versionNonce": 13,
  "isDeleted": false,
  "boundElements": null,
  "updated": 1,
  "link": null,
  "locked": false,
  "text": "AI Processing Pipeline (Cloud Run)",
  "fontSize": 16,
  "fontFamily": 1,
  "textAlign": "left",
  "verticalAlign": "top",
  "baseline": 14,
  "containerId": null,
  "originalText": "AI Processing Pipeline (Cloud Run)",
  "lineHeight": 1.25
}
```

Note: Group labels are standalone text elements (no containerId) positioned at the top-left of the group box.

---

## Output Instructions

1. **File Location**: Save to `docs/architecture/` or user-specified path
2. **File Name**: Use descriptive names like `system-architecture.excalidraw`
3. **Validation**: Ensure all `boundElements` IDs match corresponding text element IDs
4. **Testing**: User can open in https://excalidraw.com or VS Code Excalidraw extension

---

## Checklist

Before generating:
- [ ] Identified all components/services
- [ ] Mapped all connections/data flows
- [ ] Chose appropriate colors for component types
- [ ] Planned grid layout with row/column positions
- [ ] Created unique IDs for all elements

During generation:
- [ ] Every shape with a label has BOTH shape element AND text element
- [ ] Shape has `boundElements: [{ "type": "text", "id": "{shape-id}-text" }]`
- [ ] Text has `containerId: "{shape-id}"`
- [ ] All arrows use multi-point `points` arrays (no diagonal lines)
- [ ] **All arrows have `"elbowed": true`, `"roundness": null`, `"roughness": 0`** for 90-degree corners
- [ ] Arrows from same source use staggered start positions

**Arrow Connection Validation (CRITICAL):**
- [ ] Arrow `x,y` position calculated from source shape's **edge** (not center)
- [ ] For rectangles: used `(x + width/2, y + height)` for bottom edge, etc.
- [ ] For diamonds: used vertex formulas `(x + width/2, y + height)` for bottom vertex, etc.
- [ ] Final point in `points` array reaches target shape's edge
- [ ] Arrow `width` and `height` = bounding box of path (absolute values of max x/y offsets)
- [ ] Callback/return arrows use U-turn pattern with proper clearance

After generating:
- [ ] All `boundElements` IDs reference valid text elements
- [ ] All `containerId` values reference valid shape elements
- [ ] Labels are visible (test in Excalidraw!)
- [ ] Arrows render with 90-degree corners (not curved)
- [ ] **Arrows visually connect to shape edges** (not floating/disconnected)
- [ ] No overlapping arrows
- [ ] File is valid JSON

---

## Common Arrow Bugs and Fixes

### Bug: Arrow appears disconnected/floating

**Cause**: Arrow `x,y` not calculated from shape edge.

**Fix**: Use edge formulas:
```
Rectangle bottom: arrow_x = shape.x + shape.width/2, arrow_y = shape.y + shape.height
Diamond bottom:   arrow_x = shape.x + shape.width/2, arrow_y = shape.y + shape.height
```

### Bug: Arrow endpoint doesn't reach target

**Cause**: Final point offset calculated incorrectly.

**Fix**: Calculate target edge, then compute relative offset:
```
target_edge = (target.x + target.width/2, target.y)  // top of target
offset_x = target_edge.x - arrow.x
offset_y = target_edge.y - arrow.y
Final point = [offset_x, offset_y] or intermediate elbow points leading there
```

### Bug: Multiple arrows from same source overlap

**Cause**: All arrows start from identical `x,y` position.

**Fix**: Stagger start positions along the edge:
```
For 5 arrows from bottom edge, spread across width:
  arrow1.x = shape.x + shape.width * 0.2
  arrow2.x = shape.x + shape.width * 0.35
  arrow3.x = shape.x + shape.width * 0.5  // center
  arrow4.x = shape.x + shape.width * 0.65
  arrow5.x = shape.x + shape.width * 0.8
```

### Bug: Callback arrow doesn't loop back correctly

**Cause**: U-turn path doesn't have enough clearance or wrong direction.

**Fix**: Use 4-point path with clearance:
```
// From right edge going back to shape above
Points = [[0, 0], [clearance, 0], [clearance, -vertical_dist], [final_x_offset, -vertical_dist]]

// clearance = 40-60px typically (enough to visually clear the shapes)
```
