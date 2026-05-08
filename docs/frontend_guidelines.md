# Frontend Guidelines

---

## Design Philosophy

| Principle | Description |
|---|---|
| **Minimal** | Remove visual noise; every element serves a purpose |
| **Calm** | Neutral palette; no aggressive colors or animations |
| **Enterprise-focused** | Professional, trustworthy, information-dense |
| **Functional over decorative** | Prioritize usability over aesthetics |
| **Status-forward** | Pipeline status, worker health, errors — always visible |

---

## UI Inspiration

| Product | What to Learn |
|---|---|
| GitHub | Clean tables, status badges, action menus |
| Linear | Smooth transitions, keyboard shortcuts, density |
| Azure Data Studio | Query results, connection management, sidebar |
| JetBrains IDEs | Information density, tool windows, log panels |
| Vercel Dashboard | Pipeline progress, deployment status, clean cards |

---

## Design System

### Color Palette — Light Mode (Primary)

| Token | Hex | Usage |
|---|---|---|
| `--bg-primary` | `#F8FAFC` | Page background |
| `--bg-surface` | `#FFFFFF` | Card/panel background |
| `--bg-surface-hover` | `#F1F5F9` | Hover state for interactive surfaces |
| `--bg-muted` | `#F1F5F9` | Secondary backgrounds, code blocks |
| `--border-default` | `#E2E8F0` | Card borders, dividers |
| `--border-strong` | `#CBD5E1` | Active borders, focus rings |
| `--text-primary` | `#0F172A` | Headings, primary content |
| `--text-secondary` | `#475569` | Descriptions, metadata |
| `--text-muted` | `#94A3B8` | Placeholders, disabled text |
| `--accent-primary` | `#2563EB` | Primary buttons, links, active states |
| `--accent-primary-hover` | `#1D4ED8` | Button hover |
| `--status-success` | `#16A34A` | Completed, passed, healthy |
| `--status-warning` | `#CA8A04` | Paused, retrying, slow |
| `--status-error` | `#DC2626` | Failed, error, critical |
| `--status-info` | `#0EA5E9` | Running, processing, info |
| `--status-neutral` | `#64748B` | Queued, pending, idle |

### Color Palette — Dark Mode (Future)

| Token | Hex | Usage |
|---|---|---|
| `--bg-primary` | `#0F172A` | Page background |
| `--bg-surface` | `#1E293B` | Card/panel background |
| `--bg-surface-hover` | `#334155` | Hover state |
| `--border-default` | `#334155` | Borders |
| `--text-primary` | `#F1F5F9` | Primary text |
| `--text-secondary` | `#94A3B8` | Secondary text |
| `--accent-primary` | `#3B82F6` | Primary accent |

---

### Typography

| Element | Font | Weight | Size | Line Height |
|---|---|---|---|---|
| Page title | Inter | 600 (SemiBold) | 24px / 1.5rem | 32px |
| Section heading | Inter | 600 | 18px / 1.125rem | 28px |
| Card heading | Inter | 500 (Medium) | 16px / 1rem | 24px |
| Body text | Inter | 400 (Regular) | 14px / 0.875rem | 20px |
| Small text | Inter | 400 | 12px / 0.75rem | 16px |
| Code / SQL | JetBrains Mono | 400 | 13px / 0.8125rem | 20px |
| Badge text | Inter | 500 | 11px / 0.6875rem | 16px |

**Font Loading**:
```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

---

### Spacing Scale

| Token | Value | Usage |
|---|---|---|
| `--space-1` | 4px | Inline element gaps |
| `--space-2` | 8px | Tight padding (badges, tags) |
| `--space-3` | 12px | Button padding, small gaps |
| `--space-4` | 16px | Card padding, form gaps |
| `--space-5` | 20px | Section gaps |
| `--space-6` | 24px | Card content padding |
| `--space-8` | 32px | Page section spacing |
| `--space-10` | 40px | Major section dividers |

---

### Border Radius

| Token | Value | Usage |
|---|---|---|
| `--radius-sm` | 4px | Badges, small elements |
| `--radius-md` | 6px | Buttons, inputs |
| `--radius-lg` | 8px | Cards, panels |
| `--radius-xl` | 12px | Modals, large containers |

---

### Shadows

| Token | Value | Usage |
|---|---|---|
| `--shadow-sm` | `0 1px 2px rgba(0,0,0,0.05)` | Cards, subtle elevation |
| `--shadow-md` | `0 4px 6px rgba(0,0,0,0.07)` | Dropdowns, popovers |
| `--shadow-lg` | `0 10px 15px rgba(0,0,0,0.1)` | Modals, overlays |

---

## Layout Guidelines

### Page Structure
```
┌─────────────────────────────────────────────┐
│  Sidebar (240px fixed)  │  Content Area     │
│                         │                   │
│  ┌───────────────────┐  │  ┌─────────────┐ │
│  │ Logo              │  │  │ Page Header  │ │
│  │ Navigation        │  │  │ (Title +     │ │
│  │  - Dashboard      │  │  │  Actions)    │ │
│  │  - Projects       │  │  └─────────────┘ │
│  │  - Workers        │  │                   │
│  │  - Logs           │  │  ┌─────────────┐ │
│  │  - Settings       │  │  │ Page Content │ │
│  │                   │  │  │              │ │
│  │ User Menu         │  │  │              │ │
│  └───────────────────┘  │  └─────────────┘ │
└─────────────────────────────────────────────┘
```

### Table Design
- Dense but readable (row height: 40px)
- Alternating row backgrounds (subtle)
- Sticky headers
- Sortable columns with visual indicators
- Pagination at bottom (50 items default)
- Status badges for chunk/pipeline state

### Empty States
- Illustrative icon + text
- Clear call-to-action ("Create your first project")
- Never show empty tables without explanation

---

## UX Guidelines

### Progress Communication
- Show pipeline progress as **stage bars** (Parsing → Conversion → Validation)
- Show chunk progress as **percentage + count** ("142/200 chunks · 71%")
- Use **animated progress bars** for actively running pipelines
- Display **estimated time remaining** when enough data available

### Error Surfacing
- Validation errors shown **inline on chunk table** with expandable detail
- Failed chunks highlighted with **red status badge** + retry button
- System errors shown as **toast notifications** (top-right, auto-dismiss 5s)
- Critical errors shown as **persistent banner** (won't auto-dismiss)

### Real-time Updates
- Pipeline progress polled every **3 seconds** while pipeline is RUNNING
- Worker health polled every **10 seconds**
- Log viewer auto-scrolls when tailing (user can pause)

### Keyboard Shortcuts (Future)
| Shortcut | Action |
|---|---|
| `Ctrl+K` | Command palette |
| `Ctrl+/` | Toggle sidebar |
| `Esc` | Close modal / deselect |

---

## Accessibility Standards

- All interactive elements keyboard-accessible
- Proper focus management for modals
- ARIA labels on icon-only buttons
- Color contrast ratio ≥ 4.5:1 (WCAG AA)
- Status communicated via text + color (never color alone)
- Screen reader support for pipeline progress updates

---

## Animation Guidelines

- **Subtle transitions only** — 150ms ease-out for hover states
- **No decorative animations** — enterprise users find them distracting
- **Loading skeletons** — use for initial page load, not full-page spinners
- **Progress bars** — animate smoothly, don't jump between values
