# Codex Atlas Design System

## War Inc: Rising Wiki — UI System

A production-ready UI system for a content-heavy information platform covering structured stats, wiki articles, guides, and data dashboards. Fantasy medieval aesthetic applied as a skin over a serious, content-first information system.

---

## Core Philosophy

| Principle | Application |
|---|---|
| **Content-first** | Readability > decoration. Text is primary. |
| **Fantasy skin** | Depth + gold accents + serif headings over a clean information layout. Not a game UI. |
| **Information-dense** | Dense layouts are correct. Tables, stats, and data are expected. |
| **Scalable** | Token-based. One stylesheet serves 1,127+ pages. |

## Design Tokens

All tokens are CSS custom properties defined in `src/styles/tokens.css`.

### Surfaces
```
--surface-base       #1a1a2e   Deep navy-slate (dark topbar/footer)
--surface-raised     #232342   Elevated panel surface
--surface-overlay    #2a2a4a   Modal/dropdown
--surface-paper      #f5f0e8   Parchment (page background)
--surface-card       #ffffff   Card surface
--surface-inset      #e8e3d8   Inset/disabled
--surface-muted      #f0ede5   Subtle background
```

### Gold Accent
```
--gold-500           #d4a017   Primary accent (buttons, active states)
--gold-300           #fcd34d   Highlights, hover states
--gold-700           #926d0e   Deep accent, heading color
--gold-50            #fef7e0   Light tint (hover backgrounds)
```

### Rarity Colors
```
--rarity-common      #9ca3af   Gray
--rarity-rare        #34d399   Green
--rarity-epic        #60a5fa   Blue
--rarity-legendary   #a78bfa   Purple
--rarity-mythic      #fb923c   Orange
```

### Typography
```
--font-display       Cinzel (serif)     H1-H3, nav items, entity names
--font-body          Inter (sans)       Body text, table cells, tooltips
--font-mono          JetBrains Mono     Code, numbers
```

Scale: 0.75rem → 2.25rem (12px → 36px)

### Shadows (depth hierarchy)
```
--shadow-xs   to --shadow-xl    0-20px blur, 0-25px spread
--shadow-inner                  Inset shadow for pressed states
```

### Bevel System
```
--bevel-inset     inset highlight + shadow (surfaces)
--bevel-outset    outset highlight + shadow (cards, buttons)
```

### Spacing: 8px base
```
--space-1   4px    --space-6   24px
--space-2   8px    --space-8   32px
--space-3   12px   --space-10  40px
--space-4   16px   --space-12  48px
--space-5   20px   --space-16  64px
```

### Layout
```
--content-max    768px   Article body width
--content-wide   960px   Entity page content
--sidebar-width  280px   Right sidebar
--nav-width      240px   Left navigation
--topbar-height  56px    Sticky header
```

## Component System

### Location: `src/components/`

```
ui/
├── Button.astro       Primary/secondary/danger/ghost
├── Card.astro         Content/stat/entity variants
├── Badge.astro        Rarity/profession/status/tag
├── Tabs.astro         Tab bar with optional badge count
├── Table.astro        Data tables with sortable headers
├── Tooltip.astro      Hover tooltip (CSS-only)
└── Modal.astro        Overlay modal with focus

content/
├── ArticleHeader.astro   Title + metadata row
├── EntityHeader.astro    Image + name + badges + stat chips
├── StatGrid.astro        Label/value grid
├── CalloutBox.astro      Info/warning/lore/critical
└── SectionNav.astro      Anchor link navigation
```

### Button
| Prop | Values |
|---|---|
| variant | `primary` (gold), `secondary` (outline), `danger` (red), `ghost` (borderless) |
| size | `sm`, `md`, `lg` |
| href | Renders as `<a>` instead of `<button>` |
| loading | Shows spinner |
| disabled | Prevents interaction |

States: hover (lift 1px), active (press), focus (gold ring)

### Card
| Prop | Values |
|---|---|
| variant | `content` (default), `stat` (colored left border), `entity` (flex row) |
| padding | `sm`, `md`, `lg` |
| hoverable | Enables 2px lift on hover |
| rarity | Sets border color for stat variant |

### Badge
| Variant | Use |
|---|---|
| `rarity` | Colored background by level 1-5 |
| `profession` | Muted background with border |
| `status` | Dot indicator + label |
| `tag` | Pill shape, muted |

### Table
- `wiki-table` class for standard styling
- Dark raised header with gold underline
- Alternating row backgrounds
- Gold tint on hover
- Right-aligned numbers with `data-type="number"`
- Sortable columns via `data-align="right"`
- Wrapped in `.table-wrap` for horizontal scroll

### CalloutBox
| Type | Border | Background | Icon |
|---|---|---|---|
| `info` | Blue (#3b82f6) | Dark blue | ℹ |
| `warning` | Amber (#f59e0b) | Dark amber | ⚠ |
| `lore` | Purple (#a855f7) | Dark purple | ◆ |
| `critical` | Red (#ef4444) | Dark red | ✕ |

### StatGrid
- Auto-fill grid (min 140px columns)
- Uppercase gold labels, bold values
- Optional change indicator with direction (up/down arrows, colored)

## Page Layouts

### Article Layout (guides, blogs, prose)
```
Max-width: 768px
Single column
ArticleHeader → sections → related links
```

### Entity Layout (heroes, buildings, bosses)
```
Max-width: 960px
EntityHeader → SectionNav → stat sections → related
Tables are primary content vehicle
```

### Index Layout (listing pages)
```
Max-width: 960px
Breadcrumb → title → filter nav → listing
.listing-plain for simple lists
.quick-links for card-style link grids
```

## Visual System

### Fantasy Theme Rules
1. Theme is a **skin** over a serious information system, not a game UI
2. Depth comes from bevels and shadows, not texture images
3. Gold is diagnostic — it signals interactive elements and high-value data
4. All backgrounds are solid colors (no stone/wood pattern tiling)
5. Headings use Cinzel (serif), body uses Inter (sans)
6. Tables always have the dark header + gold underline treatment

### Element Styles (defined in `base.css`)
```
h1        Cinzel, bold, 1.875rem, gold-700
h2        Cinzel, bold, 1.25rem, gold-700, border-bottom
h3        Cinzel, bold, 1.125rem, gold-600
body      Inter, 1rem, 1.6 line-height
a         gold-600, underline on hover
code      JetBrains Mono, muted background
blockquote     3px gold left border
```

### Component Classes (defined in `components.css`)
All component classes use the `.component` naming pattern:
- `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-danger`, `.btn-ghost`
- `.card`, `.card-hoverable`, `.card-stat`, `.card-entity`
- `.badge`, `.badge-rarity`, `.badge-profession`
- `.tabs`, `.tab`
- `.table-wrap`, `.wiki-table`
- `.callout`, `.callout-icon`, `.callout-title`
- `.stat-grid`, `.stat-item`, `.stat-label`, `.stat-value`
- `.topbar`, `.topbar-logo`, `.topbar-nav`
- `.breadcrumb`, `.breadcrumb-sep`
- `.section-nav`
- `.quick-links`
- `.listing-plain`

## Interaction System

| Element | Hover | Active | Transition |
|---|---|---|---|
| Button | translateY(-1px) + shadow-md | translateY(0) + shadow-inner | 150ms |
| Card (hoverable) | translateY(-2px) + shadow-md | — | 200ms |
| Table row | Gold tint background | — | 100ms |
| Tab | Color to gold-600 | Gold underline | 150ms |
| Link | Underline + color shift | — | 150ms |
| Modal | — | Fade 200ms + scale 250ms | 200/250ms |
| Tooltip | Show after 300ms | — | 200ms |
| Quick link | translateY(-1px) + gold border | — | 150ms |

All animations disabled at `prefers-reduced-motion`.

## CSS Architecture

```css
src/styles/
├── tokens.css       /* Design tokens (CSS custom properties) */
├── base.css         /* Element resets, typography, utilities */
└── components.css   /* All component classes */
```

Imported in `BaseLayout.astro` via `<link>` tags. The Google Fonts link for Cinzel + Inter + JetBrains Mono is also in `BaseLayout.astro`.

## How to Add a New Component

1. Add component styles to `src/styles/components.css` using design tokens
2. Create `.astro` component in `src/components/ui/` or `src/components/content/`
3. Use CSS class names from `components.css`, not inline styles
4. Use design tokens (var(--space-*), var(--text-*), etc.) not hardcoded values

## Scaling

- One stylesheet serves all 1,127+ pages
- Page templates use semantic HTML + token-based classes
- No page-specific CSS exists
- To add new content types: create a new `[slug].astro` page that imports `<BaseLayout>` + component library
- To change the theme: swap token values in `tokens.css` (e.g., `--font-display`, `--surface-*`)
- To add dark mode: add `[data-theme="dark"]` overrides in `tokens.css`

## Multi-Theme Extension

```css
[data-theme="parchment"] {
  --surface-base:   #f5f0e8;
  --surface-card:   #ffffff;
  --surface-muted:  #f0ede5;
  --border-light:   #d4c9b0;
  --gold-500:       #b8860b;
}
```
