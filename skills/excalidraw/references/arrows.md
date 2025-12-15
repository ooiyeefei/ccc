# Arrow Routing Reference

Complete guide for creating elbow arrows with proper connections.

---

## Critical: Elbow Arrow Properties

Three required properties for 90-degree corners:

```json
{
  "type": "arrow",
  "roughness": 0,        // Clean lines
  "roundness": null,     // Sharp corners (not curved)
  "elbowed": true        // Enables elbow mode
}
```

**Without these, arrows will be curved, not 90-degree elbows.**

---

## Edge Calculation Formulas

| Shape Type | Edge | Formula |
|------------|------|---------|
| Rectangle | Top | `(x + width/2, y)` |
| Rectangle | Bottom | `(x + width/2, y + height)` |
| Rectangle | Left | `(x, y + height/2)` |
| Rectangle | Right | `(x + width, y + height/2)` |
| Ellipse | Top | `(x + width/2, y)` |
| Ellipse | Bottom | `(x + width/2, y + height)` |

---

## Universal Arrow Routing Algorithm

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
    IF abs(dx) < 10:  // Nearly aligned
      points = [[0, 0], [0, dy]]
    ELSE:  // Need L-shape
      points = [[0, 0], [dx, 0], [dx, dy]]

  ELSE IF sourceEdge == "right" AND targetEdge == "left":
    IF abs(dy) < 10:
      points = [[0, 0], [dx, 0]]
    ELSE:
      points = [[0, 0], [0, dy], [dx, dy]]

  ELSE IF sourceEdge == targetEdge:  // U-turn
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

## Arrow Patterns Reference

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

---

## Worked Examples

### Vertical Connection (Bottom to Top)

```
Source: x=500, y=200, width=180, height=90
Target: x=500, y=400, width=180, height=90

source_bottom = (500 + 180/2, 200 + 90) = (590, 290)
target_top = (500 + 180/2, 400) = (590, 400)

Arrow x = 590, y = 290
Distance = 400 - 290 = 110
Points = [[0, 0], [0, 110]]
```

### Fan-out (One to Many)

```
Orchestrator: x=570, y=400, width=140, height=80
Target: x=120, y=550, width=160, height=80

orchestrator_bottom = (570 + 140/2, 400 + 80) = (640, 480)
target_top = (120 + 160/2, 550) = (200, 550)

Arrow x = 640, y = 480
Horizontal offset = 200 - 640 = -440
Vertical offset = 550 - 480 = 70

Points = [[0, 0], [-440, 0], [-440, 70]]  // Left first, then down
```

### U-turn (Callback)

```
Source: x=570, y=400, width=140, height=80
Target: x=550, y=270, width=180, height=90
Connection: Right of source -> Right of target

source_right = (570 + 140, 400 + 80/2) = (710, 440)
target_right = (550 + 180, 270 + 90/2) = (730, 315)

Arrow x = 710, y = 440
Vertical distance = 315 - 440 = -125
Final x offset = 730 - 710 = 20

Points = [[0, 0], [50, 0], [50, -125], [20, -125]]
// Right 50px (clearance), up 125px, left 30px
```

---

## Staggering Multiple Arrows

When N arrows leave from same edge, spread evenly:

```
FUNCTION getStaggeredPositions(shape, edge, numArrows):
  positions = []
  FOR i FROM 0 TO numArrows-1:
    percentage = 0.2 + (0.6 * i / (numArrows - 1))

    IF edge == "bottom" OR edge == "top":
      x = shape.x + shape.width * percentage
      y = (edge == "bottom") ? shape.y + shape.height : shape.y
    ELSE:
      x = (edge == "right") ? shape.x + shape.width : shape.x
      y = shape.y + shape.height * percentage

    positions.append({x, y})
  RETURN positions

// Examples:
// 2 arrows: 20%, 80%
// 3 arrows: 20%, 50%, 80%
// 5 arrows: 20%, 35%, 50%, 65%, 80%
```

---

## Arrow Bindings

For better visual attachment, use `startBinding` and `endBinding`:

```json
{
  "id": "arrow-workflow-convert",
  "type": "arrow",
  "x": 525,
  "y": 420,
  "width": 325,
  "height": 125,
  "points": [[0, 0], [-325, 0], [-325, 125]],
  "roughness": 0,
  "roundness": null,
  "elbowed": true,
  "startBinding": {
    "elementId": "cloud-workflows",
    "focus": 0,
    "gap": 1,
    "fixedPoint": [0.5, 1]
  },
  "endBinding": {
    "elementId": "convert-pdf-service",
    "focus": 0,
    "gap": 1,
    "fixedPoint": [0.5, 0]
  },
  "startArrowhead": null,
  "endArrowhead": "arrow"
}
```

### fixedPoint Values

- Top center: `[0.5, 0]`
- Bottom center: `[0.5, 1]`
- Left center: `[0, 0.5]`
- Right center: `[1, 0.5]`

### Update Shape boundElements

```json
{
  "id": "cloud-workflows",
  "boundElements": [
    { "type": "text", "id": "cloud-workflows-text" },
    { "type": "arrow", "id": "arrow-workflow-convert" }
  ]
}
```

---

## Bidirectional Arrows

For two-way data flows:

```json
{
  "type": "arrow",
  "startArrowhead": "arrow",
  "endArrowhead": "arrow"
}
```

Arrowhead options: `null`, `"arrow"`, `"bar"`, `"dot"`, `"triangle"`

---

## Arrow Labels

Position standalone text near arrow midpoint:

```json
{
  "id": "arrow-api-db-label",
  "type": "text",
  "x": 305,                        // Arrow x + offset
  "y": 245,                        // Arrow midpoint
  "text": "SQL",
  "fontSize": 12,
  "containerId": null,
  "backgroundColor": "#ffffff"
}
```

**Positioning formula:**
- Vertical: `label.y = arrow.y + (total_height / 2)`
- Horizontal: `label.x = arrow.x + (total_width / 2)`
- L-shaped: Position at corner or longest segment midpoint

---

## Width/Height Calculation

Arrow `width` and `height` = bounding box of path:

```
points = [[0, 0], [-440, 0], [-440, 70]]
width = abs(-440) = 440
height = abs(70) = 70

points = [[0, 0], [50, 0], [50, -125], [20, -125]]
width = max(abs(50), abs(20)) = 50
height = abs(-125) = 125
```
