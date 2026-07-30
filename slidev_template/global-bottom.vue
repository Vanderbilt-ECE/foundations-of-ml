<script setup lang="ts">
import { useSlideContext } from '@slidev/client'
import seedrandom from 'seedrandom'
/**
 * Animated glow background — blurred polygon shapes per slide.
 * Control per slide via frontmatter:
 *   glowSeed: 229         — integer seed (different number = different shape)
 *   glowOpacity: 0.4      — default 0.4
 *   glowHue: 0            — hue rotation in degrees
 *   glow: 'full'          — distribution: full|top|bottom|left|right|center|top-left|etc.
 */
import { computed, ref, unref, watch } from 'vue'

const { $nav } = useSlideContext()
const nav = computed(() => unref($nav))
const route = computed(() => unref(nav.value.currentSlideRoute))
const page = computed(() => unref(nav.value.currentPage))
const total = computed(() => unref(nav.value.total))

export type Range = [number, number]

export type Distribution =
  | 'full'
  | 'top'
  | 'bottom'
  | 'left'
  | 'right'
  | 'top-left'
  | 'top-right'
  | 'bottom-left'
  | 'bottom-right'
  | 'center'
  | 'topmost'

const formatter = computed(() => route.value.meta?.slide?.frontmatter || {})
const distribution = computed(() => (formatter.value.glow || 'full') as Distribution)
const opacity = computed<number>(() => +(formatter.value.glowOpacity ?? 0.4))
const hue = computed<number>(() => +(formatter.value.glowHue || 0))
const seed = computed<string>(() => (formatter.value.glowSeed === 'false' || formatter.value.glowSeed === false)
  ? Date.now().toString()
  : formatter.value.glowSeed || 'default',
)
const overflow = 0.3
const disturb = 0.3
const disturbChance = 0.3

function distributionToLimits(distribution: Distribution) {
  const min = -0.2
  const max = 1.2
  let x: Range = [min, max]
  let y: Range = [min, max]

  function intersection(a: Range, b: Range): Range {
    return [Math.max(a[0], b[0]), Math.min(a[1], b[1])]
  }

  const limits = distribution.split('-')

  for (const limit of limits) {
    switch (limit) {
      case 'topmost':
        y = intersection(y, [-0.5, 0])
        break
      case 'top':
        y = intersection(y, [min, 0.6])
        break
      case 'bottom':
        y = intersection(y, [0.4, max])
        break
      case 'left':
        x = intersection(x, [min, 0.6])
        break
      case 'right':
        x = intersection(x, [0.4, max])
        break
      case 'xcenter':
        x = intersection(x, [0.25, 0.75])
        break
      case 'ycenter':
        y = intersection(y, [0.25, 0.75])
        break
      case 'center':
        x = intersection(x, [0.25, 0.75])
        y = intersection(y, [0.25, 0.75])
        break
      case 'full':
        x = intersection(x, [0, 1])
        y = intersection(y, [0, 1])
        break
      default:
        break
    }
  }

  return { x, y }
}

function distance2([x1, y1]: Range, [x2, y2]: Range) {
  return (x2 - x1) ** 2 + (y2 - y1) ** 2
}

function usePloy(number = 16) {
  function getPoints(): Range[] {
    const limits = distributionToLimits(distribution.value)
    const rng = seedrandom(`${seed.value}-${page.value}`)
    function randomBetween([a, b]: Range) {
      return rng() * (b - a) + a
    }
    function applyOverflow(random: number, overflow: number) {
      random = random * (1 + overflow * 2) - overflow
      return rng() < disturbChance ? random + (rng() - 0.5) * disturb : random
    }
    return Array.from({ length: number })
      .fill(0)
      .map(() => [
        applyOverflow(randomBetween(limits.x), overflow),
        applyOverflow(randomBetween(limits.y), overflow),
      ])
  }

  const points = ref(getPoints())
  const poly = computed(() => points.value.map(([x, y]) => `${x * 100}% ${y * 100}%`).join(', '))

  function jumpPoints() {
    const newPoints = new Set(getPoints())
    points.value = points.value.map((o) => {
      let minDistance = Number.POSITIVE_INFINITY
      let closest: Range | undefined
      for (const n of newPoints) {
        const d = distance2(o, n)
        if (d < minDistance) {
          minDistance = d
          closest = n
        }
      }
      newPoints.delete(closest)
      return closest
    })
  }

  watch(route, () => {
    jumpPoints()
  })

  return poly
}

const poly1 = usePloy(10)
const poly2 = usePloy(6)
const poly3 = usePloy(3)
</script>

<template>
  <div>
    <div class="slide-number">{{ page }} / {{ total }}</div>
    <div
      class="bg transform-gpu overflow-hidden pointer-events-none"
      :style="{ filter: `blur(70px) hue-rotate(${hue}deg)` }"
      aria-hidden="true"
    >
      <div
        class="clip bg-gradient-to-r from-[#18549a] to-[#12238b]"
        :style="{ 'clip-path': `polygon(${poly1})`, 'opacity': opacity }"
      />
      <div
        class="clip bg-gradient-to-l from-[#18549a] to-[#12238b]"
        :style="{ 'clip-path': `polygon(${poly2})`, 'opacity': opacity }"
      />
      <div
        class="clip bg-gradient-to-t from-[#01b6d1] to-[#aaf7ff]"
        :style="{ 'clip-path': `polygon(${poly3})`, 'opacity': 0.2 }"
      />
    </div>
  </div>
</template>

<style scoped>
.bg,
.clip {
  transition: all 2.5s ease;
}

.bg {
  position: absolute;
  inset: 0;
  z-index: -10;
}

.clip {
  clip-path: circle(75%);
  aspect-ratio: 16 / 9;
  position: absolute;
  inset: 0;
}

.light .clip {
  opacity: 1 !important;
}

.slide-number {
  position: absolute;
  bottom: 10px;
  right: 14px;
  font-size: 0.75rem;
  opacity: 0.6;
  color: white;
  z-index: 10;
  pointer-events: none;
}
</style>
