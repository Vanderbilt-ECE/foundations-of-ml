---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Presentation Title'
info: |
  ## Presentation Title
  Brief description of the presentation.
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
glowSeed: 229
---

# Presentation Title

### Subtitle or Tagline

<div class="pt-6 opacity-80 text-lg">
A brief description from <strong>Your Organization</strong>
</div>

<div class="pt-10 text-sm opacity-60">
Conference Name · Session Name · Date
</div>

<!--
Speaker notes go here. ~15 sec per slide is a rough guide.
-->

---
glowSeed: 100
---

# 3-Column Card Grid

Intro sentence framing the slide topic.

<div class="grid grid-cols-3 gap-4 mt-8">

<div v-click border="2 solid teal-700" bg="teal-800/20" rounded-lg overflow-hidden>
<div bg="teal-800/40" px-4 py-2 flex items-center gap-2>
<span text-xl>📈</span>
<span font-bold>Card Title</span>
</div>
<div px-4 py-4 text-sm>
<div class="text-3xl font-bold text-teal-400 mb-2">Key Stat</div>
Supporting explanation text goes here.
</div>
</div>

<div v-click border="2 solid blue-700" bg="blue-800/20" rounded-lg overflow-hidden>
<div bg="blue-800/40" px-4 py-2 flex items-center gap-2>
<span text-xl>🏗️</span>
<span font-bold>Card Title</span>
</div>
<div px-4 py-3 text-sm>
Supporting explanation text with <strong>emphasis</strong> where needed.
</div>
</div>

<div v-click border="2 solid orange-700" bg="orange-800/20" rounded-lg overflow-hidden>
<div bg="orange-800/40" px-4 py-2 flex items-center gap-2>
<span text-xl>🔧</span>
<span font-bold>Card Title</span>
</div>
<div px-4 py-3 text-sm>
Supporting explanation text with <em>emphasis</em> where needed.
</div>
</div>

</div>

<!-- Available accent colors: teal, blue, orange, red, amber, violet, green -->

<!--
Speaker notes.
-->

---
glowSeed: 175
---

# 3-Column Cards + Bottom Banner

<div class="grid grid-cols-3 gap-4 mt-8">

<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg overflow-hidden>
<div bg="red-800/40" px-4 py-2 flex items-center gap-2>
<span text-xl>🖥️</span>
<span font-bold>Card Title</span>
</div>
<div px-4 py-3 text-sm>
Card content with <strong>bold text</strong> for emphasis.
</div>
</div>

<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg overflow-hidden>
<div bg="amber-800/40" px-4 py-2 flex items-center gap-2>
<span text-xl>📦</span>
<span font-bold>Card Title</span>
</div>
<div px-4 py-3 text-sm>
Card content with <strong>bold text</strong> and <strong>more emphasis</strong>.
</div>
</div>

<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg overflow-hidden>
<div bg="violet-800/40" px-4 py-2 flex items-center gap-2>
<span text-xl>🤖</span>
<span font-bold>Card Title</span>
</div>
<div px-4 py-3 text-sm>
Card content with a key <strong>conclusion</strong> or takeaway.
</div>
</div>

</div>

<!-- Bottom summary banner — appears after all cards -->
<div v-click class="mt-10 flex justify-center">
<div border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg px-6 py-3 text-lg>
Punchline or summary: <strong>key action</strong> or <strong>conclusion</strong>.
</div>
</div>

<!--
Speaker notes.
-->

---
glowSeed: 123
---

# Numbered List (Research Questions / Key Points)

<div class="text-sm opacity-70 mb-6">Optional subheading or framing sentence.</div>

<v-clicks>

<div border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg flex items-start gap-4 px-5 py-4 mb-4>
<div class="text-4xl font-bold text-teal-400">1</div>
<div class="text-xl pt-1">First key question or point with <strong>emphasis</strong> on important terms.</div>
</div>

<div border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg flex items-start gap-4 px-5 py-4 mb-4>
<div class="text-4xl font-bold text-teal-400">2</div>
<div class="text-xl pt-1">Second key question or point with <strong>emphasis</strong> on important terms.</div>
</div>

<div border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg flex items-start gap-4 px-5 py-4 mb-4>
<div class="text-4xl font-bold text-teal-400">3</div>
<div class="text-xl pt-1">Third key question or point with <strong>emphasis</strong> on important terms.</div>
</div>

</v-clicks>

<!--
Speaker notes.
-->

---
layout: two-cols
layoutClass: gap-8
glowSeed: 180
---

# Two-Column Layout

Left column content. Bullet lists work well here:

<v-clicks>

- **Point one** — description
- **Point two** — description
- **Point three** — description

Supporting sentence or context.

</v-clicks>

::right::

<!-- Right column: a single framed info box -->
<div v-click class="mt-8" border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg overflow-hidden>
<div bg="white/10" backdrop-blur px-4 py-2 flex items-center gap-2>
<div i-carbon:group text-teal-300 text-xl />
<span font-bold>Box Title</span>
</div>
<div px-5 py-4>

<div class="grid grid-cols-2 gap-4 text-center">
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="text-4xl font-bold">42</div>
<div class="text-sm opacity-80">Label A</div>
</div>
<div border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="text-4xl font-bold">18</div>
<div class="text-sm opacity-80">Label B</div>
</div>
</div>

<div class="mt-6 text-sm opacity-80">
Supporting note that pays off in a later slide.
</div>

</div>
</div>

<!--
Speaker notes.
-->

---
glowSeed: 350
---

# Two-Column Content Cards

<div class="grid grid-cols-2 gap-8 mt-6">

<div v-click border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg overflow-hidden>
<div bg="white/10" backdrop-blur px-4 py-2 flex items-center gap-2>
<div i-carbon:flow text-blue-300 text-xl />
<span font-bold>How it works</span>
</div>
<div px-5 py-4>

- **Item one:** description
- **Item two:** description
- **Item three:** description
- **Item four:** description

</div>
</div>

<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg overflow-hidden>
<div bg="teal-800/40" px-4 py-2 flex items-center gap-2>
<div i-carbon:idea text-teal-300 text-xl />
<span font-bold>Key insight</span>
</div>
<div px-5 py-4>

Key insight or takeaway paragraph. Keep it short and punchy.

<div class="mt-4 text-sm opacity-80">
Secondary supporting note in smaller text.
</div>

</div>
</div>

</div>

<!--
Speaker notes.
-->

---
glowSeed: 182
---

# Two Cards with Icon Headers

<div class="grid grid-cols-2 gap-8 mt-4">

<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg overflow-hidden>
<div bg="blue-800/40" px-4 py-2 flex items-center gap-2>
<div i-carbon:user-speaker text-blue-300 text-xl />
<span font-bold>Card One</span>
</div>
<div px-5 py-4>

Main content paragraph. Can include a list:

- **Sub-point one** — explanation
- **Sub-point two** — explanation
- **Sub-point three** — explanation

<div class="mt-3 text-sm opacity-80">Footer note in smaller, dimmer text.</div>

</div>
</div>

<div v-click border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg overflow-hidden>
<div bg="white/10" backdrop-blur px-4 py-2 flex items-center gap-2>
<div i-carbon:time text-amber-300 text-xl />
<span font-bold>Card Two</span>
</div>
<div px-5 py-4>

Main content paragraph.

<div class="mt-4" border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-3>
⚠️ <strong>Nested warning or callout box</strong><br/>
Detail text explaining the callout.
</div>

<div class="mt-3 text-sm opacity-80">Follow-up note after the callout.</div>

</div>
</div>

</div>

<!--
Speaker notes.
-->

---
layout: center
class: text-center
glowSeed: 205
---

# Centered Highlight Slide

<div v-click class="text-2xl mt-4 mb-8">
Surprising or important finding: <span class="text-teal-400 font-bold">highlighted result</span>.
</div>

<div class="grid grid-cols-2 gap-8 max-w-4xl mx-auto text-left">

<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg overflow-hidden>
<div bg="amber-800/40" px-4 py-2 flex items-center gap-2>
<span text-xl>📦</span>
<span font-bold>Group A</span>
</div>
<div px-4 py-3>
Description of Group A's behavior or result.
</div>
</div>

<div v-click border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg overflow-hidden>
<div bg="white/10" backdrop-blur px-4 py-2 flex items-center gap-2>
<span text-xl>🎓</span>
<span font-bold>Group B</span>
</div>
<div px-4 py-3>
Description of Group B's behavior or result.
</div>
</div>

</div>

<div v-click class="mt-8 text-lg">
Additional finding or implication that reinforces the headline above.
</div>

<!--
Speaker notes.
-->

---
glowSeed: 310
---

# 2×3 Icon Card Grid (Future Work / Features)

<div class="text-sm opacity-70 mb-6">Optional framing subheading.</div>

<div class="grid grid-cols-2 gap-4">

<div v-click border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg flex gap-3 items-start px-4 py-3>
<div class="text-2xl">🤖</div>
<div>Item one — <strong>short bold label</strong> followed by one-sentence description.</div>
</div>

<div v-click border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg flex gap-3 items-start px-4 py-3>
<div class="text-2xl">📋</div>
<div>Item two — <strong>short bold label</strong> followed by one-sentence description.</div>
</div>

<div v-click border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg flex gap-3 items-start px-4 py-3>
<div class="text-2xl">📊</div>
<div>Item three — <strong>short bold label</strong> followed by one-sentence description.</div>
</div>

<div v-click border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg flex gap-3 items-start px-4 py-3>
<div class="text-2xl">🔍</div>
<div>Item four — <strong>short bold label</strong> followed by one-sentence description.</div>
</div>

<div v-click border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg flex gap-3 items-start px-4 py-3 min-h-20>
<div class="text-2xl">✅</div>
<div>Item five — <strong>short bold label</strong> followed by one-sentence description.</div>
</div>

<div v-click border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg flex gap-3 items-start px-4 py-3 min-h-20>
<div class="text-2xl">🧑‍🏫</div>
<div>Item six — <strong>short bold label</strong> followed by one-sentence description.</div>
</div>

</div>

<!--
Speaker notes.
-->

---
layout: center
class: text-center
glowSeed: 150
---

# Conclusion — 3-Column Takeaways

<div class="grid grid-cols-3 gap-6 max-w-5xl mx-auto mt-8 text-left">

<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-6 py-5>
<div class="text-3xl mb-2">⚖️</div>
<div class="font-bold mb-2">Takeaway One</div>
One sentence explaining the first takeaway.
</div>

<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg px-6 py-5>
<div class="text-3xl mb-2">📦</div>
<div class="font-bold mb-2">Takeaway Two</div>
One sentence explaining the second takeaway.
</div>

<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg px-6 py-5>
<div class="text-3xl mb-2">🗣️</div>
<div class="font-bold mb-2">Takeaway Three</div>
One sentence explaining the third takeaway.
</div>

</div>

<div v-click class="mt-10 text-lg opacity-90">
Closing sentence that positions the work or points to next steps.
</div>

<!--
Speaker notes.
-->

---
layout: center
class: text-center
glowSeed: 229
---

# Thank You

### Questions & Discussion

<div class="pt-6 opacity-80">
Your Name · Your Organization
</div>

<div class="pt-8 text-sm opacity-60">
Backup slides follow if applicable
</div>

<!--
Contact info here if needed.
-->
