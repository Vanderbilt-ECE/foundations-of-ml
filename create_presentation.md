# Converting an Obsidian Subject Folder into Local Slidev Presentations

Use this workflow to mirror a subject folder from the Foundations of Machine Learning Obsidian vault into the local course directory and implement every presentation outline as a verified Slidev deck.

## Expected result

Given an Obsidian folder such as:

```text
Foundations of Machine Learning/<Subject>/
├── assignments/
└── Presentations/
    ├── <Presentation One>.md
    └── <Presentation Two>.md
```

create this local structure:

```text
<course root>/<Subject>/
├── assignments/
└── Presentations/
    ├── <Presentation One>/
    │   ├── slides.md
    │   ├── slides-export.pdf
    │   └── Slidev support files
    └── <Presentation Two>/
        ├── slides.md
        ├── slides-export.pdf
        └── Slidev support files
```

Preserve the subject and subfolder names exactly, including capitalization. Create one deck directory for every presentation outline in the vault.

## 1. Inspect the Obsidian subject folder

Use the Obsidian MCP server rather than reading or searching for vault files directly on disk.

1. List the target subject folder recursively.
2. Confirm that `assignments` and `Presentations` exist.
3. Record every file path under `Presentations`.
4. Read every presentation outline in full, including its frontmatter, slide descriptions, equations, code, figures, and speaker notes.
5. Read assignment files only when they need to be copied or implemented. Otherwise, create the local `assignments` folder and leave its contents unchanged.

Do not begin authoring until all presentation outlines have been read. Treat the vault outlines as the content specification, not as finished Slidev Markdown.

## 2. Create the local subject structure

From the local Foundations of Machine Learning course root, create:

```bash
mkdir -p '<Subject>/assignments' '<Subject>/Presentations'
```

Then create one directory per presentation outline:

```bash
mkdir -p '<Subject>/Presentations/<Presentation Title>/setup'
```

Use the vault note filename as the deck directory name unless it contains characters unsuitable for a local path. Do not create speculative folders or files.

## 3. Read the shared Slidev template and course style guide

Before creating any deck, read these files completely:

```text
slidev_template/STYLE_GUIDE.md
slidev_template/slides.md
slidev_template/style.css
slidev_template/global-bottom.vue
slidev_template/uno.config.ts
slidev_template/setup/main.ts
slidev_template/package.json
```

The shared template is authoritative. Preserve its:

- dark background and seeded blue/cyan glow;
- DM Sans typography;
- slide numbers and fade transitions;
- flat colored cards and neutral glass cards;
- teal, blue, orange, amber, red, and violet semantic accents;
- standard Slidev code highlighting and click animations.

Do not copy the entire template or install another dependency tree. Each deck should import the shared template files and use the existing `slidev_template/node_modules` installation.

## 4. Review existing course presentations

Inspect relevant decks in both locations before designing the new slides:

```text
Mathematical Foundations/Presentations/
Core ML Concepts/Presentations/
```

Choose examples related to the new subject. For regression content, useful references include:

- `Mathematical Foundations/Presentations/Linear Algebra` for matrices, rank, and vector diagrams;
- `Mathematical Foundations/Presentations/Calculus for Optimization` for gradients and optimization paths;
- `Core ML Concepts/Presentations/Bias-Variance Tradeoff` for underfit/overfit visuals;
- `Core ML Concepts/Presentations/Overfitting and Regularization` for ridge, lasso, and penalty geometry;
- `Core ML Concepts/Presentations/Train-Validation-Test Splits and Cross-Validation` for evaluation workflows.

Reuse established layout and visualization patterns, but do not copy irrelevant content.

## 5. Map each outline into a slide plan

For every vault outline:

1. Preserve every required concept, equation, example, figure, and speaker-note objective.
2. Use the outline's order unless a small reordering materially improves the explanation.
3. Split dense outline slides into two or three Slidev slides instead of shrinking the content.
4. Add supporting slides when needed for a derivation, implementation detail, worked example, or visualization.
5. End with the summary and next-topic transition specified by the outline.

Each slide should have one clear teaching purpose. Prefer readable whitespace over maximum information density.

## 6. Scaffold each deck from the shared template

Create these minimal support files in every deck directory.

`package.json`:

```json
{
  "name": "<lowercase-deck-name>",
  "type": "module",
  "private": true,
  "scripts": {
    "dev": "PATH=/opt/homebrew/opt/node@20/bin:$PATH ../../../slidev_template/node_modules/.bin/slidev --open",
    "build": "PATH=/opt/homebrew/opt/node@20/bin:$PATH ../../../slidev_template/node_modules/.bin/slidev build",
    "export": "PATH=/opt/homebrew/opt/node@20/bin:$PATH ../../../slidev_template/node_modules/.bin/slidev export"
  }
}
```

`global-bottom.vue`:

```vue
<script setup lang="ts">
import TemplateBottom from '../../../slidev_template/global-bottom.vue'
</script>

<template>
  <TemplateBottom />
</template>
```

`style.css`:

```css
@import '../../../slidev_template/style.css';
```

`uno.config.ts`:

```ts
export { default } from '../../../slidev_template/uno.config'
```

`setup/main.ts`:

```ts
export { default } from '../../../../slidev_template/setup/main'
```

`vite.config.ts`:

```ts
import { fileURLToPath } from 'node:url'

const deckRoot = fileURLToPath(new URL('.', import.meta.url))
const templateRoot = fileURLToPath(new URL('../../../slidev_template', import.meta.url))

export default {
  server: {
    fs: {
      allow: [deckRoot, templateRoot],
    },
  },
}
```

These relative paths assume the deck is at `<Subject>/Presentations/<Deck>`. Adjust them only if the directory depth differs.

## 7. Author `slides.md`

Start with the shared headmatter pattern:

```yaml
---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: '<Presentation Title>'
info: |
  ## <Presentation Title>
  <One-sentence description>
class: text-center
transition: fade-out
lineNumbers: false
drawings:
  persist: false
mdc: true
vite:
  server:
    fs:
      strict: false
glowSeed: <integer>
---
```

### Equations

- Use LaTeX for mathematical notation.
- Use `$...$` for inline equations and `$$...$$` for display equations.
- Use `aligned` for short derivations.
- Put important equations in a colored or neutral glass card.
- Keep display equations to one or two readable lines; split long derivations across slides.
- Leave blank lines around Markdown or LaTeX placed inside raw HTML containers.
- Do not place Markdown backticks or `$...$` directly inside a one-line raw HTML element. Use `<code>...</code>`, Unicode notation, or a multiline container instead.

### Python and scikit-learn

- Use Python and scikit-learn for practical examples.
- Keep code snippets focused, normally 8–15 lines per slide.
- Use pipelines for preprocessing and modeling so cross-validation does not leak information.
- Use `PolynomialFeatures`, `StandardScaler`, `LinearRegression`, `Ridge`, `Lasso`, `RidgeCV`, and other scikit-learn tools where relevant.
- Prefer numerically stable APIs such as `np.linalg.lstsq` or `np.linalg.solve`; show an explicit inverse only when teaching the derivation.
- Make evaluation examples statistically valid. For example, do not compute $R^2$ from a test set containing only one observation.
- Run every nontrivial snippet or an equivalent combined check before delivery.

### SVG graphics and animation

- Prefer inline SVG for plots, matrices, flowcharts, geometry, optimization paths, and conceptual diagrams.
- Always preserve a `viewBox` and scale with `class="w-full"` plus a sensible maximum width.
- Use the template accent colors and readable labels.
- Use `v-click`, `<v-clicks>`, click-based code highlighting, SVG stroke animation, or `v-motion` when progressive explanation helps.
- Include accessible `role="img"` and `aria-label` attributes on instructional SVGs.
- If an essential visual cannot reasonably be created as SVG or with Matplotlib, add a clearly labeled image placeholder describing the required image. Do not silently omit it.

### Speaker notes

Convert the outline's speaker notes into Slidev presenter notes:

```markdown
<!--
Speaker notes for this slide.
-->
```

Preserve callbacks to earlier course units, derivation guidance, common misconceptions, live-demo instructions, and transitions to the next slide.

## 8. Build and run the teaching code

From each deck directory:

```bash
npm run build
```

The build must finish without errors. Then run a compact Python check covering the deck's nontrivial code paths and assertions. At minimum, verify that:

- arrays have the expected shapes;
- solvers return finite coefficients;
- metrics are defined and finite;
- cross-validation runs successfully;
- ridge/lasso pipelines converge for the shown parameters;
- outputs support the claims made on the slides.

Fix the root cause of any failing example rather than weakening the check.

## 9. Verify every slide with Playwright CLI

Start a local Slidev server on an unused port:

```bash
../../../slidev_template/node_modules/.bin/slidev --port <port>
```

Use `playwright-cli` to open the deck and set a presentation-sized viewport:

```bash
playwright-cli open 'http://127.0.0.1:<port>/1'
playwright-cli resize 1920 1080
```

For every slide route:

1. Open `/<slide-number>?clicks=99` so all staged content is visible.
2. Wait for `.slidev-page-<slide-number>` and `document.fonts.ready`.
3. Confirm no rendered element extends beyond the active slide canvas.
4. Confirm there are no `.katex-error` elements.
5. Check the browser console for errors.
6. Inspect representative screenshots containing equations, code, SVGs, and dense layouts.
7. Confirm click reveals work by pressing `ArrowRight` on at least one staged slide and verifying the hidden-element count decreases.

Pay particular attention to:

- title wrapping and font loading;
- long equations;
- code-block width and height;
- SVG scaling and labels;
- bottom banners and speaker-facing footnotes;
- content that appears only after clicks;
- literal Markdown accidentally displayed inside raw HTML.

If anything overflows, split or tighten the slide and rerun the full deck audit.

## 10. Export and deliver

After the final edit, rebuild and export each deck sequentially:

```bash
npm run build
npm run export
```

Confirm that `slides-export.pdf` exists and its page count equals the number of slides in `slides.md`. Stop local development servers and remove temporary screenshots or other verification artifacts.

The final handoff should report:

- each completed deck directory;
- links to `slides.md` and `slides-export.pdf`;
- the slide count for each deck;
- build, Python, Playwright, LaTeX, SVG, console, and overflow verification results;
- any intentionally retained image placeholders.

The process is complete only when every vault presentation outline has a corresponding local Slidev deck and every deck passes the full verification workflow.
