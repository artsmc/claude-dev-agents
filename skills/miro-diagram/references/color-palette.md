# Color Palette — Miro Diagrams

Miro diagrams use a `palette` line in the DSL to define available colors. Nodes reference colors by **index** (0, 1, 2...), not by hex code directly.

## Miro's Approved Colors

These colors are optimized for Miro's rendering. Pick from this list:

| Color | Hex | Good For |
|-------|-----|----------|
| Red/Pink | `#ffc6c6` | Errors, danger, critical paths |
| Orange | `#f8d3af` | Warnings, external services |
| Yellow | `#fff6b6` | Default/general nodes, highlights |
| Lime | `#dbfaad` | Success, healthy, approved |
| Green | `#adf0c7` | Start/end points, entry/exit |
| Teal | `#c3faf5` | Data stores, databases |
| Light Blue | `#ccf4ff` | Infrastructure, supporting services |
| Blue | `#c6dcff` | Primary/core application nodes |
| Purple | `#dedaff` | AI/ML components, special processing |
| Pink | `#ffd8f4` | External/third-party services |
| Gray | `#e7e7e7` | Inactive, background, plumbing |

## Recommended Palettes

Pick one based on your diagram's purpose:

**Architecture diagram** (services + data):
```
palette #c6dcff #ccf4ff #adf0c7
```
- 0: Blue — application services
- 1: Light blue — data stores
- 2: Green — entry/exit points

**Process/workflow** (steps + decisions + outcomes):
```
palette #fff6b6 #c6dcff #adf0c7
```
- 0: Yellow — process steps
- 1: Blue — decision points
- 2: Green — start/end terminators

**Error handling flow**:
```
palette #c6dcff #adf0c7 #ffc6c6
```
- 0: Blue — normal path
- 1: Green — success outcomes
- 2: Red — error/failure paths

## Rules

1. **2-3 colors per diagram.** More creates visual noise without adding meaning.
2. **Each color = a meaning.** Decide upfront: "blue = services, green = data" and be consistent.
3. **Use the default palette** (`#fff6b6 #c6dcff #adf0c7`) when you don't have a strong reason to customize. It's Miro's default and looks polished.
