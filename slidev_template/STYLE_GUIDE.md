# Slidev Presentation Style Guide

Use this guide for course presentations derived from `slidev_template`.

## Component System

- Keep the global dark background, seeded blue/cyan glow, DM Sans typography, slide numbers, and fade transitions.
- Use the template's flat colored cards or neutral glass cards. Do not use per-card glow effects.
- Use teal, blue, orange, amber, red, or violet for semantic accents.
- Prefer the existing two-column, three-column, numbered-list, icon-grid, banner, and centered-summary patterns.
- Use `v-click` for individual reveals and `<v-clicks>` for sequential lists.
- Leave enough whitespace for projection. Split an overcrowded slide instead of shrinking everything.

Colored card:

```html
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
Card content
</div>
```

Neutral glass card:

```html
<div border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg p-4>
Card content
</div>
```

## LaTeX Equations

- Use `$...$` for inline math and `$$...$$` for display math.
- Leave a blank line before and after display equations, especially inside HTML or Vue containers.
- Keep `mdc: true` in deck headmatter so Markdown and LaTeX render inside card layouts.
- Use `aligned` for short multi-line derivations:

```latex
$$
\begin{aligned}
L(\theta) &= \sum_i \ell_i(\theta) \\
\nabla L(\theta) &= \sum_i \nabla \ell_i(\theta)
\end{aligned}
$$
```

- Put important equations in a colored or neutral glass card.
- Keep display equations to one or two readable lines. Split long derivations across slides.
- Avoid custom LaTeX packages and macros unless the deck explicitly configures them.
- Keep slide titles plain text; place notation in the body where rendering is more predictable.

## Code Snippets

- Always specify the language on fenced code blocks, such as `python`, `ts`, or `bash`.
- Keep examples focused—roughly 8–15 lines per slide. Split longer examples into setup and result slides.
- Use the default code size. Use `text-xs` only when two short snippets must share a slide.
- Leave line numbers off unless the narration refers to specific lines.
- Highlight only the lines being discussed:

````markdown
```python {2,4}
x = np.array([1.0, 2.0])
y = model(x)
loss = mse(y, target)
loss.backward()
```
````

- For progressive walkthroughs, use click-based highlighting such as `{1|2-3|all}`.
- Use a standard slide for code-only examples and a two-column layout for code paired with an SVG, image, or explanation.
- Use a neutral glass card when code needs a labeled container. Avoid custom wrappers around code blocks.
- Preserve indentation and executable content when restyling a slide.

## SVGs and Diagrams

- Preserve the SVG `viewBox` so diagrams scale cleanly.
- Use `class="w-full"` and add a reasonable `max-w-*` constraint when centering a diagram.
- Keep SVG colors within the template accent palette.
- Pair dense diagrams with short explanatory text rather than another dense visual.

## Verification

- Run `npm run build` after editing a deck.
- Check equation width, code overflow, card height, and SVG scaling in the rendered presentation.
- Export to PDF or PNG before delivery when possible; valid Markdown can still overflow visually.
