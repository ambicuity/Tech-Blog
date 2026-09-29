# Figures

How to draw diagrams for [blog.riteshrana.engineer](https://blog.riteshrana.engineer)
articles: hand-authored SVG, inlined into the page, styled by the site, and
optionally animated one step at a time. The reference is the outbox article's
[`outbox-flow.svg`](../content/posts/transactional-outbox-reliable-events-without-dual-writes/outbox-flow.svg).

The approach follows the best engineering blogs (PlanetScale's diagrams are a good
example): precise schematics of the real system, not decoration. The figure should
show the *state* the prose describes (the rows, the queue, the partitions) and how
it changes.

## When to draw a figure

- The idea is a flow, a sequence, a state change or a data layout.
- A reader would otherwise have to hold more than three moving parts in their head.
- About one figure per 400-600 words of explanation; never a figure that repeats a
  code block.

Use a Mermaid block instead for simple flowcharts, sequence diagrams and state
machines that need no custom layout (see [content-authoring.md](content-authoring.md)).
Draw an SVG figure when layout carries meaning: tables with rows, partitions, key
ranges, memory, before/after comparisons.

## Using a figure in an article

Put the SVG next to `index.md` and reference it with the `.figure` class:

```markdown
![What the figure shows, in one or two sentences for screen readers.](flow.svg "Caption shown under the figure."){: .figure}
```

- The alt text is the figure's accessible description: say what it shows and what
  happens, not "diagram of X".
- The title (in quotes) becomes the visible caption. Keep it to one sentence that
  states the point.
- The build inlines the SVG (so it follows the light/dark theme), prefixes its IDs,
  and strips anything unsafe. CI rejects figures that contain scripts, `<style>`,
  event handlers, `<foreignObject>` or references outside the file.

## Drawing rules

**Canvas.** `viewBox="0 0 720 H"`, where H fits the content (about 280-420). Do not
set `width` or `height`. The article column is about 690 px wide, so 1 unit is about
1 px: 13 px text stays 13 px. On phones the figure keeps a readable size and scrolls
sideways inside its box.

**No colors, fonts or sizes in the file.** Use only these classes; the site draws
them with its tokens in both themes:

| Class | Use |
| :--- | :--- |
| `f-title` | Section title above a frame (PostgreSQL, Kafka) |
| `f-label` | Small caps label (table names, component names) |
| `f-code` | Values, keys, identifiers inside the diagram |
| `f-small`, `f-end`, `f-middle` | Smaller text; right / centre alignment |
| `f-box` | A component or table: surface fill, hairline border |
| `f-frame` | A container (a database, a cluster); fill it with the hatch pattern |
| `f-hatch` | The lines inside the hatch pattern |
| `f-rule` | Dashed separators (table rows, legends) |
| `f-line`, `f-dashed`, `f-arrowhead` | Connectors, dashed connectors (replies, acks), arrowheads |
| `f-a1` … `f-a4` | Data that matters: soft fill + outline on shapes, colored text on `<text>` |
| `f-a1-solid` … `f-a4-solid` | A solid chip in that hue (a message, a tenant) |
| `f-a1-line` … `f-a4-line` | A connector or outline in that hue |

Structure is grey; color is reserved for the data the reader should follow. Use one
hue per actor (one order, one tenant, one request), and no more than four.

**Text.** Monospace, 11-14 px through the classes. Labels are nouns from the code
(`outbox`, `relay`, `p1`), so the figure and the prose use the same names. Keep
labels clear of lines and frames by at least 6 units.

**Legend.** Number the steps in the figure (small `f-a1` circles with the digit) and
list them under a dashed `f-rule` at the bottom. The figure must make sense as a still
image: that is what readers see without JavaScript, with reduced motion, in print and
in feed readers.

**Accessibility.** Start the file with `<title>`. The alt text in the article gives
the full description; the caption states the point.

## Animation (optional)

A figure animates when elements carry these attributes; `assets/js/figures.js` plays
it once when the figure is half in view, with Pause / Play / Replay controls, and never
autoplays for readers who prefer reduced motion.

| Attribute | Meaning |
| :--- | :--- |
| `data-step="N"` | Appears at step N (hidden before it while the animation runs) |
| `data-until="N"` | Disappears at step N (hidden in the final state) |
| both | Visible only from `data-step` until `data-until` (e.g. a lock highlight) |
| `style="--from-x: -110px"` / `--from-y` | Slides in from this offset when it appears |

Steps run about 1.3 s apart. The final state (all `data-step` shown, all
`data-until` hidden) must be the complete picture. Animate what changes in the
system (a row appears, a message moves, a status flips), never decoration.

## Skeleton

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 300">
  <title>What this figure shows</title>
  <defs>
    <pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <line x1="0" y1="0" x2="0" y2="7" class="f-hatch"/>
    </pattern>
    <marker id="arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0 0 L8 4 L0 8 z" class="f-arrowhead"/>
    </marker>
  </defs>

  <text x="8" y="20" class="f-title">Service</text>
  <rect x="8" y="30" width="300" height="160" fill="url(#hatch)" class="f-frame"/>
  <rect x="22" y="44" width="272" height="132" class="f-box"/>
  <text x="34" y="64" class="f-label">table</text>
  <line x1="22" y1="74" x2="294" y2="74" class="f-rule"/>

  <g data-step="1" style="--from-y: 8px">
    <rect x="26" y="80" width="264" height="30" rx="2" class="f-a1"/>
    <text x="34" y="100" class="f-code">row that appears</text>
  </g>
  <line x1="308" y1="95" x2="420" y2="95" class="f-line" marker-end="url(#arrow)" data-step="2"/>

  <line x1="8" y1="220" x2="712" y2="220" class="f-rule"/>
  <text x="8" y="244" class="f-small">1 what happens first   2 what happens next</text>
</svg>
```

Check a figure before opening a pull request: `bundle exec jekyll serve`, open the
article in light and dark mode, watch the animation once, and narrow the window to
phone width.
