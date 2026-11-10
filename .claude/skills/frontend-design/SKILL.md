# Spendly UI

Spendly is a personal expense tracker: **Flask** routes in `app.py` render **Jinja2** templates that extend `templates/base.html`, styled by `static/css/style.css`, with small **vanilla JS** enhancements in `static/js/`. Data is SQLite via helper functions in `database/db.py`. Pages are server-rendered: forms POST to Flask routes and the route re-renders the template or redirects. There are no JSON APIs, no build step, no npm, no JS framework.

The repo's `CLAUDE.md` is the authority on architecture and conventions. Read it at the start of every task, because it may have changed since this skill was written, and where it disagrees with this skill, follow `CLAUDE.md`.

The goal is UI that feels like a calm, premium fintech product **and is visibly the same app** as the existing pages. Spendly has a distinctive look (warm paper background, ink-black buttons, deep green accent, serif display headings). A generic indigo SaaS component would clash with it, so consistency beats novelty every time.

## Step 1: Read the current design

Before designing, read:
- `CLAUDE.md`: conventions, route table, which steps are placeholders
- `static/css/style.css`: the `:root` tokens and the existing component patterns (cards, buttons, forms, notices)
- `templates/base.html`: navbar, footer, the `title` / `head` / `content` / `scripts` blocks
- the template closest to what you're building (e.g. `register.html` for forms, the landing page mock dashboard for stats and category bars)
- `database/db.py`: the schema and the `CATEGORIES` list, so the UI shows fields that really exist

If the request is vague about content (what the page should show, which actions it needs), ask one short question, or state your assumption and proceed if it's cheap to change. If the user has a screenshot or reference they want matched, use it.

When redesigning or improving an existing page, keep the element IDs, `data-` attributes, form field `name`s, form actions and anything the tests assert on (check `tests/`), unless the user asks to change them, and say what you kept.

## Step 2: Plan the structure (briefly)

Decide the layout before the code: what the user needs to see first, what they do most often, and what can be secondary. In an expense tracker, money figures and the primary action (add expense, filter, save) usually come first. Think through every state: empty (first-time user), validation error, success, and full of data (long descriptions, large amounts, many rows).

## The Spendly design system

These are the tokens in `style.css` at the time of writing. Re-check `:root` in case they changed, and always use the variables rather than the hex values:

| Role | Variable | Value |
|---|---|---|
| Page background | `--paper` | #f7f6f3 (warm off-white) |
| Section / track background | `--paper-warm` | #f0ede6 |
| Card surface | `--paper-card` | #ffffff |
| Primary text, primary buttons | `--ink` | #0f0f0f |
| Secondary text | `--ink-soft` | #2d2d2d |
| Muted text, labels | `--ink-muted` | #6b6b6b |
| Placeholders, faint icons | `--ink-faint` | #a0a0a0 |
| Brand accent (focus, links, hover, success) | `--accent` / `--accent-light` | #1a472a / #e8f0eb |
| Secondary accent (highlights, warnings) | `--accent-2` / `--accent-2-light` | #c17f24 / #fdf3e3 |
| Errors, destructive actions | `--danger` / `--danger-light` | #c0392b / #fdecea |
| Borders | `--border` / `--border-soft` | #e4e1da / #eeebe4 |
| Fonts | `--font-display` / `--font-body` | DM Serif Display / DM Sans |
| Radii | `--radius-sm` / `--radius-md` / `--radius-lg` | 6px / 12px / 20px |
| Widths | `--max-width` / `--auth-width` | 1200px / 440px |

How the existing UI uses them, which new UI should follow:
- **Typography**: page and card titles use `--font-display` (serif, normal weight, ~1.2–2rem). Body, labels, numbers and buttons use `--font-body`. Big money figures use the body font at weight 500 with `letter-spacing: -0.02em` (see `.mock-stat-value`).
- **Cards**: `background: var(--paper-card); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 2rem` (1.5rem on small screens). Depth comes from borders, not shadows. If something needs to float (dropdown, modal, hover lift), use a very soft shadow like `0 8px 40px rgba(0,0,0,0.05)` (the mock window's). Never use heavy or dark shadows.
- **Buttons**: primary actions use `.btn-primary` / `.btn-submit` (ink background that turns `--accent` on hover); secondary actions use `.btn-ghost`. Reuse these classes rather than inventing new button styles. Destructive actions use `--danger` text or border with a `--danger-light` background.
- **Forms**: reuse `.form-group`, `label`, `.form-input` (focus turns the border `--accent`), `.auth-error` for a form-level error, `.auth-notice` for a success notice.
- **Spacing**: rem-based, using the values already in the file (0.25, 0.5, 0.75, 0.875, 1, 1.25, 1.5, 2, 2.5, 3, 4rem). Containers are `max-width: var(--max-width); margin: 0 auto; padding: 0 2rem`.
- **Breakpoints**: the file is desktop-first with `@media (max-width: 900px)` (grids collapse to one column) and `@media (max-width: 600px)` (tighter padding). Use the same two.
- **Transitions**: `0.2s` on color, background and border-color, as everywhere else.

When the UI needs a colour that doesn't exist yet (e.g. a colour per category), **add a new variable to `:root` in `style.css`** with a clear name and use it, rather than a hex value in page CSS. The landing page's category bars already suggest a palette to formalise:

```css
--cat-food: #e8a540;
--cat-transport: #4a7fd6;
--cat-bills: #7f6fd0;
--cat-health: #3f9b7a;
--cat-entertainment: #d46a8c;
--cat-shopping: #c17f24;
--cat-other: #8a8a8a;
```

Check whether these already exist before adding them; if they do, reuse them.

## Expense-tracker specifics

- **Data model**: an expense has `amount`, `category`, `date` (ISO `YYYY-MM-DD`), `description` (optional). Categories are the `CATEGORIES` list in `db.py` (Food, Transport, Bills, Health, Entertainment, Shopping, Other). Pass that list to the template instead of hard-coding options. There is no income, budget or account table: don't design UI for data that doesn't exist. If a design idea needs new data, say so and leave it out.
- **Currency is INR (₹)**. Show amounts as `₹1,23,456.00` (Indian digit grouping). In JS use `new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" })`. In Jinja, use a currency filter if `app.py` has one; otherwise propose registering a small `inr` filter in `app.py` (one function, no new package) rather than formatting by hand in several templates. Use `font-variant-numeric: tabular-nums` wherever amounts line up in a column.
- **Dates**: show as "12 Nov 2026" or "Today" / "Yesterday" in lists, never raw ISO strings.
- **States**: every data view needs an empty state (new user, no expenses yet), with a friendly line and the primary action (e.g. "Add your first expense"), plus a sensible layout for long descriptions and large amounts.

## Code conventions (match the repo)

**Templates**
- New page → new `templates/<page>.html` that `{% extends "base.html" %}` and fills `title`, `head`, `content` and `scripts` as needed. Reusable pieces → a Jinja macro or include in `templates/` (e.g. `templates/macros/`).
- `url_for()` for every internal link, form action and static file, with no hard-coded URLs. (The footer's hard-coded `/terms` and `/privacy` links are an existing slip; don't copy them.)
- Semantic HTML: `section`, `header`, `h1`–`h3` in order, `form` with real `label`s, `table` only for genuinely tabular data.
- Jinja escapes `{{ }}` output automatically. Never add `|safe` to user-entered text such as descriptions.
- Forms: correct input types (`type="number"` with `step="0.01"` and `min="0.01"`, or `inputmode="decimal"`, for amounts; `type="date"` defaulting to today), `required` and `maxlength` that match the server-side validation, re-filled values after a server error (as `register.html` does), and the submit button disabled on submit so an expense isn't saved twice.
- Dialogs (e.g. confirm delete) close on Escape and on backdrop click, return focus to the button that opened them, and use `role="dialog"` with `aria-modal="true"`. The landing page's video modal shows the pattern.

**CSS**
- Shared tokens, and patterns reused across pages, go in `style.css`. Page-specific styles go in a **new file** `static/css/<page>.css`, linked from `{% block head %}`, never inline `<style>` (the landing page's inline modal style is an older exception).
- Class naming follows the existing style: a short block prefix with hyphenated parts (`.expense-list`, `.expense-list-item`, `.expense-list-amount`), modifiers as an extra class (`.stat-note-down`), states as `.is-*` (`.is-open`, `.is-active`).
- Only variables for colours, fonts and radii. No `!important` in new code.

**JavaScript**
- Only when it improves the experience: confirm-before-delete, show/hide, filtering an already-rendered list, live amount formatting. The page must still work through normal form submits without it.
- Page-specific logic goes in `static/js/<page>.js`, loaded from `{% block scripts %}` with `url_for('static', ...)`; tiny site-wide behaviours can go in `main.js`. Match `main.js`'s style: `document.querySelectorAll("[data-...]").forEach(...)` hooks on `data-` attributes rather than styling classes, small named functions, no globals, no libraries.
- Set user text with `textContent`, never `innerHTML`.

**Backend touch-points (keep them minimal)**
A UI task often needs the route to pass data. Follow `CLAUDE.md`: queries go in a new helper in `database/db.py` (parameterised `?` SQL, `with closing(get_db())`), the route just fetches and renders, and HTTP errors use `abort()`. Only touch a placeholder route (`/expenses/add`, `/profile`...) if the task is for that page, and don't build the other placeholders along the way. Add a simple "page loads" test in `tests/` for a new page, in the style of `tests/test_app.py`.

## Icons

The repo has no icon library. It uses inline SVG icons drawn in the Feather/Lucide style (`viewBox="0 0 24 24"`, `fill="none"`, `stroke="currentColor"`, `stroke-width="2"`, round caps and joins), e.g. the password eye toggle in `register.html`. Keep it that way: no CDN script and no new dependency.

- When a page needs several icons, create (or extend) a Jinja macro file, e.g. `templates/macros/icons.html` with `{% macro icon(name, size=20) %}` holding the SVG paths for each icon. Templates then use `{{ icon("utensils") }}`. Add only the icons actually used. Copy path data from Lucide's icon set (lucide.dev) rather than drawing it from memory, and check that the icons render correctly.
- Decorative icons get `aria-hidden="true"`; icon-only buttons get an `aria-label`.
- Use icons where they speed up recognition (category, action), not on every label. Category mapping (Lucide names): Food `utensils`, Transport `bus`, Bills `receipt`, Health `heart-pulse`, Entertainment `clapperboard`, Shopping `shopping-bag`, Other `circle-ellipsis`. Actions: add `plus`, edit `pencil`, delete `trash-2`, filter `sliders-horizontal`, search `search`, date `calendar`, trend `trending-up` / `trending-down`, export `download`.
- Category icons sit in a small rounded tile (`border-radius: var(--radius-sm)`) tinted with the category colour at low opacity (`color-mix(in srgb, var(--cat-food) 14%, transparent)`), with the icon in the full category colour.

## Motion

Spendly's motion is restrained. Add animation only where it helps someone follow a change:
- hover on clickable cards and rows: border colour shift and/or 1–2px lift, 0.2s
- first paint of a dashboard: a quick fade-up (opacity + 8px) on the cards, staggered by ~50ms
- disclosure (filters, menus, modals): fade + small scale or slide, 150–250ms
- category bars: grow from 0 to their width once on load

Animate only `transform` and `opacity` (plus colour transitions), use an ease-out curve, and wrap motion in `@media (prefers-reduced-motion: reduce)` to switch it off.

## Avoid

- Generic or dated UI: heavy gradients, bevels, harsh dark shadows, cramped tables, unstyled browser controls, emoji as icons.
- A second visual language: new fonts, a new accent colour, a new button style, or a different radius scale.
- Clutter: more than one primary button per view, or decorative elements that carry no information.
- An unstructured code dump: one giant file, inline styles, or the same markup repeated where a macro or loop would do.

## Before you hand it over

- Every colour is a variable; nothing hard-coded except `rgba` in a shadow.
- Headings use the serif display font, and buttons/forms reuse the existing classes.
- It works at 360px, 600px, 900px and 1200px widths. Tap targets are at least 44px on mobile, and nothing overflows with a long description or a ₹10,00,000 amount.
- Keyboard focus is visible, labels are real, and colour is not the only signal (e.g. down/up trend also has an arrow or sign).
- If you can run the app (`make run`, port 5001) and open a browser, look at the page at a mobile and a desktop width before declaring it done; spacing problems are visible there and not in the code.

## Output format

Structure the answer so the user can review the thinking quickly and then apply the code:

```
## UI structure
**Layout:** one or two sentences (desktop and mobile).
**Key sections:**
- Section: what it shows / does
**UX decisions:**
- 3–5 bullets, each a decision plus why.

## Code
### templates/<page>.html
### static/css/<page>.css
### static/js/<page>.js            (only if needed)
### static/css/style.css            (only new tokens or shared patterns, shown as an addition)
### app.py / database/db.py         (only the route/helper changes the page needs)

## Integration notes
- anything to wire up, new variables added, tests added
- assumptions, and any data the design would need that doesn't exist yet
```
