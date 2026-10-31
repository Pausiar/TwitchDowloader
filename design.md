# Design: Twitch VOD Downloader

The locked system. Every Hallmark run reads this first and pages share it. Change it on purpose; the file is the rule.

## System
- Genre: modern-minimal
- Shape of the first page: Split Studio (diptych; copy left, real app capture right). Document pages: head plus numbered folds.
- Theme: Cobalt (deal 1/3, seed 089a44)
- Axes: light/cool paper, grotesk display, one cobalt accent · posture: restrained

## Tokens
`tokens.css` is the source of truth. The roles:
```css
:root {
  --color-paper: oklch(98.6% 0.005 250);  --color-paper-2: oklch(96.2% 0.008 252);  --color-paper-3: oklch(93% 0.011 252);
  --color-ink: oklch(21% 0.028 262);  --color-ink-2: oklch(36% 0.022 260);  --color-muted: oklch(50% 0.018 258);  --color-rule: oklch(90% 0.009 252);
  --color-accent: oklch(52% 0.19 258);  --color-accent-deep: oklch(43% 0.2 262);  --color-accent-ink: oklch(98.6% 0.005 250);  --color-focus: oklch(52% 0.19 258);
  --font-display: "Familjen Grotesk", system-ui, sans-serif;  --font-body: "IBM Plex Sans", system-ui, sans-serif;  --font-outlier: "JetBrains Mono", ui-monospace, monospace;
  --radius-card: 8px;  --radius-pill: 999px;  --rule-hair: 1px;  --shadow-card: 0 1px 2px oklch(21% 0.028 262 / 0.06);
}
```
Spacing is the 4px scale up to `--space-4xl` 144px; type uses `--text-display` 44–84px, `--text-section` 32–56px, body 16px at 1.55; section gaps 120/144/176px.

## Controls
- Primary: cobalt fill, 8px radius, 48px high, keycap bottom edge (3px `--shadow-key-accent`).
- Secondary: paper keycap with 3px neutral edge; quiet links carry actions without a box. All controls 44px minimum.
- Tabs: pill rail on `--color-paper-2`; selected tab is a paper key.

## Motion
- Character: still. Static seeded ASCII field at the hero edge, no parallax; keys depress 2px; reduced motion removes transforms and lowers the field.

## Variants
- Documents (legal, FAQ, guide): same head, nav and footer; body is numbered folds (76px summary rows, mono numerals, plus/minus affordance). No hero, no display-scale section heads; the page is a reference, not a landing strip.

## Exports
`tokens.css` in this project. Tailwind, DTCG or shadcn blocks are added here on request.
