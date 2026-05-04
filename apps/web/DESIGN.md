# Web UI Design

## Overall Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Photograph Workflow                              [EN|中文] │ ← Header
├─────────────────────────────────────────────────────────────┤
│  Directory: [Select a workspace... ▾]  [/custom/path     ]  │ ← Workspace Bar
├─────────────────────────────────────────────────────────────┤
│  [Scan] [Rename] [Rollback] [Archive] [Workspaces]          │ ← Tab Bar
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─ Panel Content ───────────────────────────────────────┐ │
│  │                                                        │ │
│  │  h2: Page Title                                        │ │
│  │                                                        │ │
│  │  [input: path  ] [input: option] [checkbox]            │ │ ← Form Row
│  │  [btn: Primary ] [btn: Danger (conditional)]           │ │ ← Action Row
│  │                                                        │ │
│  │  ⚠ Warning / Error alerts                              │ │ ← Alerts
│  │                                                        │ │
│  │  ┌─ Summary Cards ──────────────────────────────────┐ │ │
│  │  │  42          12             3                    │ │ │
│  │  │  TOTAL       RAW/DNG       SIDECARS             │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  │                                                        │ │
│  │  ┌─ Data Table ─────────────────────────────────────┐ │ │
│  │  │  Source          │ Target          │ Role │ Stat │ │ │
│  │  │  ─────────────── │ ─────────────── │ ──── │ ──── │ │ │
│  │  │  /photos/001.ARW │ /p/2026-001.ARW │ raw  │ pend │ │ │
│  │  │  /photos/001.XMP │ /p/2026-001.XMP │ side │ pend │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Design Tokens

### Colors

| Token | Value | Usage |
|-------|-------|-------|
| `--bg` | `#f5f5f5` | Page background |
| `--surface` | `#ffffff` | Card / panel / table background |
| `--border` | `#e0e0e0` | Borders, secondary buttons |
| `--text` | `#333333` | Primary text |
| `--text-secondary` | `#666666` | Labels, hints, muted text |
| `--primary` | `#2563eb` | Primary buttons, active tabs, focus rings |
| `--primary-hover` | `#1d4ed8` | Primary button hover |
| `--danger` | `#dc2626` | Danger / execute buttons |
| `--danger-hover` | `#b91c1c` | Danger button hover |
| `--warning-bg` | `#fef3c7` | Warning alert background |
| `--warning-text` | `#92400e` | Warning alert text |
| `--error-bg` | `#fee2e2` | Error alert background |
| `--error-text` | `#991b1b` | Error alert text |
| `--success-bg` | `#d1fae5` | Success badge background |
| `--success-text` | `#065f46` | Success badge text |
| `--radius` | `6px` | Border radius for inputs, buttons, panels |

### Typography

| Token | Size | Weight | Usage |
|-------|------|--------|-------|
| `h1` | `1.5rem / 24px` | 600 | Header title |
| `h2` | `1.125rem / 18px` | 600 | Panel title |
| `body` | `inherit / 16px` | 400 | Body text |
| `.ws-label` | `0.8125rem / 13px` | 600 | Workspace bar label |
| `.btn` | `0.875rem / 14px` | 500 | Button text |
| `.summary-value` | `1.5rem / 24px` | 700 | Summary numbers |
| `.summary-label` | `0.75rem / 12px` | 400 | Summary labels (uppercase) |
| `.badge` | `0.75rem / 12px` | 500 | Badge text |
| `.mono` | `0.8125rem / 13px` | 400 | File paths (SF Mono / Menlo) |

### Spacing

| Token | Value | Usage |
|-------|-------|-------|
| Page padding | `0 16px 48px` | App container |
| Header padding | `24px 0 12px` | Title area |
| Tab bar | `8px 20px` per tab, `4px` gap | Navigation |
| Panel padding | `24px` | Content area inside border |
| Form row gap | `12px` | Between form fields |
| Section margin | `16px` (top) `20px` (bottom) | Result sections |
| Alert padding | `12px 16px` | Warning / error boxes |

### Badge Colors by Role / Status

| Role | Background | Text |
|------|-----------|------|
| `raw` | `#dbeafe` | `#1e40af` |
| `sidecar` | `#e0e7ff` | `#3730a3` |
| `other` | `#f3f4f6` | `#6b7280` |
| `pending` | `#fef3c7` | `#92400e` |
| `renamed` | `#d1fae5` | `#065f46` |
| `rolled_back` | `#f3f4f6` | `#6b7280` |

## Component Specs

### 1. Header (`App.vue`)

```
┌─────────────────────────────────────────────────────────────┐
│  Photograph Workflow                              [EN|中文] │
└─────────────────────────────────────────────────────────────┘
```

- Left: "Photograph Workflow" (h1, semi-bold)
- Right: Language toggle button (`EN` / `中文`)
- Toggle button: outlined, small (4px 12px), hover highlights border in `--primary`

### 2. Workspace Bar (`App.vue`)

```
┌─────────────────────────────────────────────────────────────┐
│  DIRECTORY: [Select a workspace... ▾]  [/custom/path...   ] │
│  /Users/example/Photograph-Raw                              │
└─────────────────────────────────────────────────────────────┘
```

- Left label: "DIRECTORY:" in uppercase, small, secondary color
- Select dropdown: 260–400px wide, lists all saved workspaces (format: `Name — /path`), plus a "— Custom path —" option
- When "Custom path" selected: text input appears for manual path entry (monospace, 300px+ fluid)
- Right area: shows the resolved path in monospace, or a hint message if none selected
- States: Loading (shows "Loading..."), Empty (shows "Add a workspace below or enter a path."), Filled (shows resolved path)

### 3. Tab Bar (`App.vue`)

```
┌─────────────────────────────────────────────────────────────┐
│  ═══Scan══  ──Rename──  ──Rollback──  ──Archive──  ──Wsp──│
└─────────────────────────────────────────────────────────────┘
```

- Horizontal row of 5 tab buttons
- Active tab: blue text + blue bottom border (2px), rests on the container border
- Inactive tab: gray text, transparent bottom border
- Hover: darkens to `--text` color

### 4. Panel (common wrapper)

Each tab renders into a white panel with border and 24px padding.

### 5. Scan Panel

```
┌─ Scan Directory ─────────────────────────────────────────┐
│                                                          │
│  Directory Path: [__________________________________   ] │
│  [Scan]                                                   │
│                                                          │
│  ┌─────────┬─────────┬──────────┬─────────┐             │
│  │   42    │   15    │    18    │    9    │             │
│  │  TOTAL  │ RAW/DNG │ SIDECARS │  OTHER  │             │
│  └─────────┴─────────┴──────────┴─────────┘             │
│                                                          │
│  ⚠ unsupported_dng_source: DNG source not confirmed...  │
│                                                          │
│  Path                         Role        Extension      │
│  ──────────────────────────── ─────────── ──────────     │
│  /p/2026/DSC00001.ARW         raw          .arw          │
│  /p/2026/DSC00001.XMP         sidecar      .xmp          │
│  /p/2026/notes.txt            other        .txt          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

- One form row: path input (pre-filled from workspace) + Scan button
- Summary cards: 4- KPI cards in a row, large number + uppercase label
- Warnings / Errors: colored alert boxes before the table
- Table: all scanned files with path (mono), role (colored badge), extension

### 6. Rename Panel

```
┌─ Rename Files ───────────────────────────────────────────┐
│                                                          │
│  Directory Path: [__________________________________   ] │
│  Template:      [__________________________________   ] │
│  ☐ Strict mode                                           │
│  [Dry Run]  [Execute Rename]                             │
│                                                          │
│  ┌──────────────┬──────────────┐                         │
│  │      12      │      3       │                         │
│  │  FILES TO    │  METADATA    │                         │
│  │   RENAME     │    DIRS      │                         │
│  └──────────────┴──────────────┘                         │
│                                                          │
│  ⚠ exiftool_missing: ExifTool not found                  │
│  ✕ target_conflict: Multiple files target same path      │
│                                                          │
│  Source              Target              Role    Status   │
│  ──────────────────  ──────────────────  ──────  ───────  │
│  /p/Shanghai/001.ARW /p/Shanghai/20...  raw     pending  │
│  /p/Shanghai/001.XMP /p/Shanghai/20...  sidecar pending  │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

- Form row: path input + template input + strict checkbox
- Action row: Dry Run (primary blue) + Execute Rename (danger red, conditional)
- Execute button only appears when dry-run has items and no errors
- Confirmation: browser `confirm()` dialog before executing
- Summary: 2 KPI cards
- Alerts: warnings (yellow) and errors (red)
- Table: source → target mapping with role and status badges

### 7. Rollback Panel

```
┌─ Rollback ───────────────────────────────────────────────┐
│                                                          │
│  Restore original file names using .metadata.json.       │
│                                                          │
│  Photo Directory Path: [____________________________   ] │
│  [Dry Run]  [Execute Rollback]                           │
│                                                          │
│  Current                    Restore To       Role Status │
│  ─────────────────────────  ───────────────  ──── ────── │
│  /p/Shanghai/2026-001.ARW  /p/Shanghai/DSC0  raw  pend  │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

- Description text below title
- One form input: photo directory path (must point to a specific photo dir with `.metadata.json`)
- Table: current → original path mapping

### 8. Archive Panel

```
┌─ Archive ────────────────────────────────────────────────┐
│                                                          │
│  Source Directory:  [_______________________________   ] │
│  Output Directory:  [_______________________________   ] │
│  ☐ Overwrite existing                                    │
│  [Preview Archive Name]  [Dry Run]  [Execute Archive]    │
│                                                          │
│  ── Recommended Archive Name ──                          │
│  Source          Archive Name         Archive Path       │
│  ──────────────  ───────────────────  ─────────────────  │
│  /p/Shanghai     Shanghai~2026.zip    /out/Shanghai~..   │
│                                                          │
│  ── Archive Plan ──                                      │
│  ┌────────┬─────────┬───────────┬────────┬────────┐     │
│  │   42   │    2    │ 1.2 GB    │   15   │   18   │     │
│  │ INCL.  │ EXCL.   │ TOT. SIZE │ RAW    │ SIDE   │     │
│  └────────┴─────────┴───────────┴────────┴────────┘     │
│                                                          │
│  Archive: /output/Shanghai~20260504120000.zip            │
│                                                          │
│  Source                Size       Included  Excl. Reason │
│  ────────────────────  ─────────  ────────  ───────────  │
│  /p/Shanghai/001.ARW   12.3 MB    Yes                   │
│  /p/Shanghai/.DS_Store  1.2 KB    No       .DS_Store     │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

- Two input rows: source + output directories
- Three action buttons (in order): Preview Name (secondary gray), Dry Run (primary blue), Execute (danger red)
- Sub-sections with h3 headings:
  - "Recommended Archive Name": single-row table showing the generated ZIP name
  - "Archive Plan": 5 KPI cards + archive path + file-level table

### 9. Workspaces Panel

```
┌─ Workspaces ─────────────────────────────────────────────┐
│                                                          │
│  Saved directories appear in the selector at the top.    │
│                                                          │
│  Directory Path: [__________________________________   ] │
│  Name:          [__________________________________   ] │
│  [Add Workspace]                                         │
│                                                          │
│  Name         Path                      Kind   Actions   │
│  ───────────  ────────────────────────  ─────  ────────  │
│  My Photos    /Users/x/Photograph-Raw   local  [Remove]  │
│  Travel       /Volumes/Drive/Travel     custom [Remove]  │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

- Hint text explaining purpose
- Form: path input + optional name input + Add button
- Table: name, path (mono), kind (badge), remove action (danger button)

## Interaction Patterns

### Workspace → Operation Flow

```
[Add workspace once]  ──→  [Select from dropdown]  ──→  [All tabs auto-filled]
```

1. User adds workspace with path (e.g., `/Users/x/Photograph-Raw`)
2. Selects it in the dropdown at the top
3. Every operation tab pre-fills its path input from the selected workspace
4. User can still override the path per-tab if needed

### Dry-Run → Execute Pattern

Every mutating operation (rename, rollback, archive) follows:

```
[Fill inputs]  →  [Dry Run]  →  Review plan  →  [Execute]  →  View result
```

- Dry Run button is always primary (blue), always visible
- Execute button is danger (red), only visible after a successful dry run (items > 0, errors = 0)
- Execute triggers a browser `confirm()` dialog before proceeding
- After execution, the plan updates to show the executed result

### Error Handling

- API errors: shown as red alert boxes with error code (bold) + message
- Warnings: shown as yellow alert boxes, non-blocking
- Network errors: shown as red alert with generic message
- Path validation: handled by backend, returned in plan errors

### Loading States

- Buttons disable during API calls, text changes to "...ing" form
  - "Scan" → "Scanning..."
  - "Dry Run" → "Generating..."
  - "Execute Rename" → "Executing..."

## Language Support

| Element | Switch | Behavior |
|---------|--------|----------|
| Header button | `EN` / `中文` | Toggles all UI text |
| Default language | `zh` (Chinese) | First visit default |
| Persistence | `localStorage` key `locale` | Survives page reload |
| Fallback | `en` (English) | If locale is invalid |

## Responsive Behavior

- App max-width: 1200px, centered with 16px side padding
- Form rows: `flex-wrap: wrap` for narrow screens
- Summary cards: `flex-wrap: wrap` for narrow screens
- Tables: horizontal scroll when content overflows
- Monospace font stack: `SF Mono, Menlo, Monaco, monospace`
- Body font stack: `-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif`
