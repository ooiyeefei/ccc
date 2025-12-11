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

| Shape Type | Edge | Formula | Reliability |
|------------|------|---------|-------------|
| Rectangle | Top | `(x + width/2, y)` | ✅ |
| Rectangle | Bottom | `(x + width/2, y + height)` | ✅ |
| Rectangle | Left | `(x, y + height/2)` | ✅ |
| Rectangle | Right | `(x + width, y + height/2)` | ✅ |
| Ellipse | Top | `(x + width/2, y)` | ✅ |
| Ellipse | Bottom | `(x + width/2, y + height)` | ✅ |

**🚫 NEVER USE DIAMOND SHAPES.** Diamond arrow connections are **unsolvable** in raw Excalidraw JSON due to how roundness rendering offsets the visual vertices from mathematical edge points. Use styled rectangles instead (coral color, thick borders).

**Arrow creation steps:**
1. Get source shape's edge point → this becomes arrow's `x, y`
2. Get target shape's edge point
3. Calculate relative offset: `target_edge - source_edge`
4. Build `points` array with elbow routing to reach the offset

### Universal Arrow Routing Algorithm

Use this algorithm for ANY arrow connection:

```
FUNCTION createArrow(source, target, sourceEdge, targetEdge):
  // Step 1: Get source edge point
  sourcePoint = getEdgePoint(source, sourceEdge)

  // Step 2: Get target edge point
  targetPoint = getEdgePoint(target, targetEdge)

  // Step 3: Calculate offsets
  dx = targetPoint.x - sourcePoint.x
  dy = targetPoint.y - sourcePoint.y

  // Step 4: Determine routing pattern
  IF sourceEdge == "bottom" AND targetEdge == "top":
    IF abs(dx) < 10:  // Nearly aligned vertically
      points = [[0, 0], [0, dy]]
    ELSE:  // Need L-shape
      points = [[0, 0], [dx, 0], [dx, dy]]

  ELSE IF sourceEdge == "right" AND targetEdge == "left":
    IF abs(dy) < 10:  // Nearly aligned horizontally
      points = [[0, 0], [dx, 0]]
    ELSE:  // Need L-shape
      points = [[0, 0], [0, dy], [dx, dy]]

  ELSE IF sourceEdge == targetEdge:  // U-turn (callback)
    clearance = 50
    IF sourceEdge == "right":
      points = [[0, 0], [clearance, 0], [clearance, dy], [dx, dy]]
    ELSE IF sourceEdge == "bottom":
      points = [[0, 0], [0, clearance], [dx, clearance], [dx, dy]]

  // Step 5: Calculate bounding box
  width = max(abs(p[0]) for p in points)
  height = max(abs(p[1]) for p in points)

  RETURN {x: sourcePoint.x, y: sourcePoint.y, points, width, height}

FUNCTION getEdgePoint(shape, edge):
  SWITCH edge:
    "top":    RETURN (shape.x + shape.width/2, shape.y)
    "bottom": RETURN (shape.x + shape.width/2, shape.y + shape.height)
    "left":   RETURN (shape.x, shape.y + shape.height/2)
    "right":  RETURN (shape.x + shape.width, shape.y + shape.height/2)
```

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

| Type | Use For | Arrow Reliability |
|------|---------|-------------------|
| `rectangle` | Services, components, databases, containers, orchestrators, decision points | ✅ Excellent |
| `ellipse` | Users, external systems, start/end points | ✅ Good |
| `text` | Labels inside shapes, titles, annotations | N/A |
| `arrow` | Data flow, connections, dependencies | N/A |
| `line` | Grouping boundaries, separators | N/A |

### 🚫 BANNED: Diamond Shapes

**NEVER use `type: "diamond"` in generated diagrams.**

Diamond arrow connections are **fundamentally broken** in raw Excalidraw JSON:
- Excalidraw applies `roundness` to diamond vertices during rendering
- The visual edges appear **offset** from the mathematical edge points
- No offset formula reliably compensates (varies by size, zoom, roundness settings)
- Arrows appear disconnected/floating even with "correct" calculations

**This is an Excalidraw rendering limitation, not a calculation error we can fix.**

### Visual Distinction Without Diamonds

Use styled rectangles to convey the same semantic meaning:

| Semantic Meaning | Rectangle Style |
|------------------|-----------------|
| **Orchestrator / Hub** | Coral color (`#ffa8a8` / `#c92a2a`) + thick border (strokeWidth: 3) |
| **Decision Point** | Orange color (`#ffd8a8` / `#e8590c`) + dashed stroke |
| **Central Router** | Distinctive size (larger) + bold color |
| **Conditional Logic** | Yellow background (`#ffec99`) + icon in label |

**Standard orchestrator/hub pattern:**
```json
{
  "type": "rectangle",
  "strokeColor": "#c92a2a",      // Coral/red to stand out
  "backgroundColor": "#ffa8a8",
  "strokeWidth": 3,              // Thicker border for emphasis
  "roundness": { "type": 3 }     // Standard rounded corners
}
```

This provides visual distinction with **100% reliable arrow connections**.

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
  "type": "rectangle",              // or "ellipse" for users/external systems
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

#### Worked Example: Orchestrator/Hub to Multiple Services (Fan-out)

**Use styled rectangle for orchestrators** (coral color + thick border for visual distinction)

```
Orchestrator rectangle: x=570, y=400, width=140, height=80
  Style: backgroundColor=#ffa8a8, strokeColor=#c92a2a, strokeWidth=3
Target rectangle: x=120, y=550, width=160, height=80
Connection: Bottom of orchestrator → Top of target

Step 1: Calculate orchestrator bottom edge
  orchestrator_bottom = (570 + 140/2, 400 + 80) = (640, 480)

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
Source shape: x=570, y=400, width=140, height=80 (orchestrator rectangle)
Target shape: x=550, y=270, width=180, height=90 (rectangle above)
Connection: Right of source → Right of target (callback loop)

Step 1: Calculate source right edge
  source_right = (570 + 140, 400 + 80/2) = (710, 440)

Step 2: Calculate target right edge
  target_right = (550 + 180, 270 + 90/2) = (730, 315)

Step 3: Calculate U-turn path
  Arrow x = 710, y = 440
  Need to go: right (to clear shapes), up, then left to target

  Vertical distance = 315 - 440 = -125 (going up)
  Final x offset = 730 - 710 = 20 (target is slightly to the right)

  Points = [[0, 0], [50, 0], [50, -125], [20, -125]]
  // Right 50px (clearance), up 125px, left 30px to reach target edge
```

**Key principle for U-turns:**
- First segment: move AWAY from shapes (clearance of 40-60px)
- Second segment: travel the vertical/horizontal distance
- Third segment: approach the target edge

#### Multiple Arrows from Same Source - Staggering

When multiple arrows leave from the same shape edge, **stagger the start points** to prevent overlap:

```
Orchestrator rectangle at x=570, y=400, width=140, height=80
Bottom edge center = (640, 480)

For 5 arrows fanning out to different targets:
Arrow 1 (leftmost target):  x=598, y=480  // 20% across width
Arrow 2 (left target):      x=619, y=480  // 35% across width
Arrow 3 (center target):    x=640, y=480  // 50% (center)
Arrow 4 (right target):     x=661, y=480  // 65% across width
Arrow 5 (rightmost target): x=682, y=480  // 80% across width

Formula: arrow_x = shape.x + shape.width * percentage
  where percentage = 0.2, 0.35, 0.5, 0.65, 0.8 for 5 arrows
```

This creates a visual "fan" effect from the source shape, with arrows spreading naturally to their targets.

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

### Bidirectional Arrows

For two-way data flows (e.g., request/response, sync connections):

```json
{
  "type": "arrow",
  "startArrowhead": "arrow",    // ✅ Arrow on START end
  "endArrowhead": "arrow"       // ✅ Arrow on END end
}
```

**Arrowhead options:**
| Value | Description |
|-------|-------------|
| `null` | No arrowhead |
| `"arrow"` | Standard arrow (triangle) |
| `"bar"` | Vertical bar |
| `"dot"` | Circle/dot |
| `"triangle"` | Filled triangle |

### Arrow Labels (Annotations on Arrows)

To add text labels on arrows (e.g., "HTTP", "gRPC", "async"):

**Method: Use standalone text positioned near the arrow**

```json
// Arrow element
{
  "id": "arrow-api-db",
  "type": "arrow",
  "x": 300,
  "y": 200,
  "points": [[0, 0], [0, 100]],
  ...
},
// Label positioned at arrow midpoint
{
  "id": "arrow-api-db-label",
  "type": "text",
  "x": 305,                        // Arrow x + small offset
  "y": 245,                        // Arrow y + half of vertical distance
  "text": "SQL",
  "fontSize": 12,
  "containerId": null,             // NOT bound to arrow
  "backgroundColor": "#ffffff",    // White background for readability
  ...
}
```

**Label positioning formula:**
```
For vertical arrow (down):
  label.x = arrow.x + 5
  label.y = arrow.y + (total_height / 2) - (label.height / 2)

For horizontal arrow (right):
  label.x = arrow.x + (total_width / 2) - (label.width / 2)
  label.y = arrow.y - label.height - 5

For L-shaped arrow:
  Position label at the corner or midpoint of longest segment
```

---

## Color Palettes

### Default Palette (Platform-Agnostic)

| Component Type | Background | Stroke | Example |
|----------------|------------|--------|---------|
| Frontend/UI | `#a5d8ff` (blue) | `#1971c2` | Next.js, React apps |
| Backend/API | `#d0bfff` (purple) | `#7048e8` | API servers, processors |
| Database | `#b2f2bb` (green) | `#2f9e44` | PostgreSQL, MySQL, MongoDB |
| Storage | `#ffec99` (yellow) | `#f08c00` | Object storage, file systems |
| AI/ML Services | `#e599f7` (magenta) | `#9c36b5` | ML models, AI APIs |
| External APIs | `#ffc9c9` (red) | `#e03131` | Third-party services |
| Orchestration | `#ffa8a8` (coral) | `#c92a2a` | Workflows, schedulers |
| Validation | `#ffd8a8` (orange) | `#e8590c` | Validators, checkers |
| Network/Security | `#dee2e6` (gray) | `#495057` | VPC, IAM, firewalls |
| Classification | `#99e9f2` (cyan) | `#0c8599` | Routers, classifiers |
| Users/Actors | `#e7f5ff` (light blue) | `#1971c2` | User ellipses |
| Message Queue | `#fff3bf` (light yellow) | `#fab005` | Kafka, RabbitMQ, SQS |
| Cache | `#ffe8cc` (peach) | `#fd7e14` | Redis, Memcached |
| Monitoring | `#d3f9d8` (mint) | `#40c057` | Prometheus, Grafana |

### AWS Palette

| Service Category | Background | Stroke |
|-----------------|------------|--------|
| Compute (EC2, Lambda, ECS) | `#ff9900` bg | `#cc7a00` |
| Storage (S3, EBS) | `#3f8624` bg | `#2d6119` |
| Database (RDS, DynamoDB) | `#3b48cc` bg | `#2d3899` |
| Networking (VPC, Route53) | `#8c4fff` bg | `#6b3dcc` |
| Security (IAM, KMS) | `#dd344c` bg | `#b12a3d` |
| Analytics (Kinesis, Athena) | `#8c4fff` bg | `#6b3dcc` |
| ML (SageMaker, Bedrock) | `#01a88d` bg | `#017d69` |

### Azure Palette

| Service Category | Background | Stroke |
|-----------------|------------|--------|
| Compute | `#0078d4` bg | `#005a9e` |
| Storage | `#50e6ff` bg | `#3cb5cc` |
| Database | `#0078d4` bg | `#005a9e` |
| Networking | `#773adc` bg | `#5a2ca8` |
| Security | `#ff8c00` bg | `#cc7000` |
| AI/ML | `#50e6ff` bg | `#3cb5cc` |

### Kubernetes Palette

| Component | Background | Stroke |
|-----------|------------|--------|
| Pod | `#326ce5` bg | `#2756b8` |
| Service | `#326ce5` bg | `#2756b8` |
| Deployment | `#326ce5` bg | `#2756b8` |
| ConfigMap/Secret | `#7f8c8d` bg | `#626d6e` |
| Ingress | `#00d4aa` bg | `#00a888` |
| Node | `#303030` bg | `#1a1a1a` |
| Namespace | `#f0f0f0` bg | `#c0c0c0` (dashed) |

### Diagram Type Suggestions

| Diagram Type | Recommended Layout | Key Elements |
|--------------|-------------------|--------------|
| **Microservices** | Vertical flow | Services, databases, message queues, API gateway |
| **Data Pipeline** | Horizontal flow | Sources, transformers, sinks, storage |
| **Event-Driven** | Hub-and-spoke | Event bus center, producers/consumers around |
| **Kubernetes** | Layered groups | Namespace boxes, pods inside deployments |
| **CI/CD** | Horizontal flow | Source → Build → Test → Deploy → Monitor |
| **Network** | Hierarchical | Internet → LB → VPC → Subnets → Instances |
| **User Flow** | Swimlanes | User actions, system responses, external calls |

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

#### Layout Pattern: Vertical Flow (Most Common)

```
Grid positioning:
- Column width: 200-250px
- Row height: 130-150px
- Element width: 160-200px
- Element height: 80-90px
- Spacing: 40-50px between elements

Row positions (y):
  Row 0: 20   (title)
  Row 1: 100  (users/entry points)
  Row 2: 230  (frontend/gateway)
  Row 3: 380  (orchestration/middleware)
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

#### Layout Pattern: Horizontal Flow (Pipelines)

```
For data pipelines, ETL, CI/CD flows:

Stage positions (x):
  Stage 0: 100  (input/source)
  Stage 1: 350  (transform 1)
  Stage 2: 600  (transform 2)
  Stage 3: 850  (transform 3)
  Stage 4: 1100 (output/sink)

All stages at same y: 200 (or center of canvas)
Arrows flow left-to-right using "right" → "left" connections
```

#### Layout Pattern: Hub-and-Spoke (Central Orchestrator)

```
For event-driven, message bus, or orchestrator architectures:

Center hub: x=500, y=350
Surrounding services in a circle:
  Top:    x=500, y=150
  Right:  x=750, y=350
  Bottom: x=500, y=550
  Left:   x=250, y=350

For more services, use 8 positions (45° increments):
  N:  (cx, cy - r)
  NE: (cx + r*0.7, cy - r*0.7)
  E:  (cx + r, cy)
  SE: (cx + r*0.7, cy + r*0.7)
  S:  (cx, cy + r)
  SW: (cx - r*0.7, cy + r*0.7)
  W:  (cx - r, cy)
  NW: (cx - r*0.7, cy - r*0.7)

Where cx=500, cy=350, r=200 (radius)
```

#### Universal Staggering Formula

When N arrows leave from the same shape edge:

```
FUNCTION getStaggeredPositions(shape, edge, numArrows):
  positions = []

  FOR i FROM 0 TO numArrows-1:
    // Spread evenly between 20% and 80% of edge length
    percentage = 0.2 + (0.6 * i / (numArrows - 1))

    IF edge == "bottom" OR edge == "top":
      x = shape.x + shape.width * percentage
      y = (edge == "bottom") ? shape.y + shape.height : shape.y
    ELSE:  // left or right
      x = (edge == "right") ? shape.x + shape.width : shape.x
      y = shape.y + shape.height * percentage

    positions.append({x, y})

  RETURN positions

// Examples:
// 2 arrows: positions at 20%, 80%
// 3 arrows: positions at 20%, 50%, 80%
// 5 arrows: positions at 20%, 35%, 50%, 65%, 80%
```

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

## Pre-Flight Validation Algorithm

**Run this validation BEFORE writing the file:**

```
FUNCTION validateDiagram(elements):
  errors = []

  // 1. Validate shape-text bindings
  FOR each shape IN elements WHERE shape.boundElements != null:
    FOR each binding IN shape.boundElements:
      textElement = findById(elements, binding.id)
      IF textElement == null:
        errors.append("Shape {shape.id} references missing text {binding.id}")
      ELSE IF textElement.containerId != shape.id:
        errors.append("Text {textElement.id} containerId doesn't match shape {shape.id}")

  // 2. Validate arrow connections
  FOR each arrow IN elements WHERE arrow.type == "arrow":
    // Check arrow starts from valid edge position
    sourceShape = findShapeNear(elements, arrow.x, arrow.y)
    IF sourceShape == null:
      errors.append("Arrow {arrow.id} doesn't start from any shape edge")

    // Check arrow ends at valid position
    finalPoint = arrow.points[arrow.points.length - 1]
    endX = arrow.x + finalPoint[0]
    endY = arrow.y + finalPoint[1]
    targetShape = findShapeNear(elements, endX, endY)
    IF targetShape == null:
      errors.append("Arrow {arrow.id} doesn't end at any shape edge")

    // Check elbow properties
    IF arrow.points.length > 2:
      IF arrow.elbowed != true:
        errors.append("Arrow {arrow.id} has multiple points but missing elbowed:true")
      IF arrow.roundness != null:
        errors.append("Arrow {arrow.id} should have roundness:null for sharp corners")

  // 3. Validate unique IDs
  ids = [el.id for el in elements]
  duplicates = findDuplicates(ids)
  IF duplicates.length > 0:
    errors.append("Duplicate IDs found: {duplicates}")

  // 4. Validate bounding boxes
  FOR each arrow IN elements WHERE arrow.type == "arrow":
    maxX = max(abs(p[0]) for p in arrow.points)
    maxY = max(abs(p[1]) for p in arrow.points)
    IF arrow.width < maxX OR arrow.height < maxY:
      errors.append("Arrow {arrow.id} bounding box too small for points")

  RETURN errors

FUNCTION findShapeNear(elements, x, y, tolerance=15):
  FOR each shape IN elements WHERE shape.type IN ["rectangle", "ellipse"]:
    edges = [
      (shape.x + shape.width/2, shape.y),              // top
      (shape.x + shape.width/2, shape.y + shape.height), // bottom
      (shape.x, shape.y + shape.height/2),             // left
      (shape.x + shape.width, shape.y + shape.height/2)  // right
    ]
    FOR each edge IN edges:
      IF abs(edge.x - x) < tolerance AND abs(edge.y - y) < tolerance:
        RETURN shape
  RETURN null
```

---

## Diagram Complexity Guidelines

| Complexity | Max Elements | Max Arrows | Recommended Approach |
|------------|-------------|------------|---------------------|
| **Simple** | 5-10 shapes | 5-10 arrows | Single file, no groups |
| **Medium** | 10-25 shapes | 15-30 arrows | Use grouping rectangles |
| **Complex** | 25-50 shapes | 30-60 arrows | Split into multiple diagrams OR use layers |
| **Very Complex** | 50+ shapes | 60+ arrows | Split into multiple focused diagrams |

**When to split diagrams:**
- More than 50 elements makes the diagram hard to read
- Create separate diagrams for: high-level overview, detailed subsystems, data flows
- Name them: `architecture-overview.excalidraw`, `architecture-data-layer.excalidraw`, etc.

**When to use groups:**
- 3+ related services that belong together (e.g., "AI Pipeline", "Data Layer")
- Services in the same deployment unit (e.g., Kubernetes namespace)
- Logical boundaries (e.g., "VPC", "Security Zone")

---

## Checklist

### Before Generating
- [ ] Identified all components/services from codebase analysis
- [ ] Mapped all connections/data flows
- [ ] Chose appropriate layout pattern (vertical, horizontal, hub-and-spoke)
- [ ] Selected color palette (default, AWS, Azure, K8s, or custom)
- [ ] Planned grid positions using row/column system
- [ ] Created unique ID naming scheme (e.g., `{type}-{name}`, `{service}-{component}`)

### During Generation
- [ ] Every shape with a label has BOTH shape element AND text element
- [ ] Shape has `boundElements: [{ "type": "text", "id": "{shape-id}-text" }]`
- [ ] Text has `containerId: "{shape-id}"`
- [ ] All multi-point arrows have `"elbowed": true`, `"roundness": null`, `"roughness": 0`
- [ ] Used Universal Arrow Routing Algorithm for all connections
- [ ] Applied Universal Staggering Formula for multiple arrows from same source
- [ ] No diamond shapes used (only rectangles and ellipses)

### Arrow Validation (Apply for EVERY arrow)
- [ ] Arrow `x,y` calculated using `getEdgePoint(sourceShape, edge)` formula
- [ ] Final point offset calculated as `targetEdge - sourceEdge`
- [ ] Arrow `width` = `max(abs(point[0]) for all points)`
- [ ] Arrow `height` = `max(abs(point[1]) for all points)`
- [ ] U-turn arrows have 40-60px clearance

### After Generation (Run Pre-Flight Validation)
- [ ] All `boundElements` IDs reference valid text elements
- [ ] All `containerId` values reference valid shape elements
- [ ] All arrows start within 15px of a shape edge
- [ ] All arrows end within 15px of a shape edge
- [ ] No duplicate IDs
- [ ] Arrow bounding boxes match points array
- [ ] File is valid JSON (parseable)

---

## Common Arrow Bugs and Fixes

### Bug: Arrow appears disconnected/floating

**Cause**: Arrow `x,y` not calculated from shape edge.

**Fix**: Use edge formulas:
```
Rectangle bottom: arrow_x = shape.x + shape.width/2, arrow_y = shape.y + shape.height
Ellipse bottom:   arrow_x = shape.x + shape.width/2, arrow_y = shape.y + shape.height
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
