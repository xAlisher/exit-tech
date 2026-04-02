# Spec: exit-card

## File
`src/components/exit-card.js`

## Input
Single `exit` object — shape from `src/data/exits.js`

## Output
DOM `<article class="exit-card">` element

## Behaviour
- Renders `exit.what` with strikethrough style (class: `exit-card__what`)
- Renders `exit.why` as body text (class: `exit-card__why`)
- Renders alternative with arrow prefix `→` (class: `exit-card__alternative`)
  - If `exit.alternativeUrl` exists, alternative is an `<a>` tag
  - If no alternative, render "nothing, and that's the point"
- Renders category tag using `exit.category` (class: `tag tag--{category}`)
- Renders counter badge showing `exit.exitCount` — clicking calls `onCounterClick(exit)`
- Renders share button — clicking calls `onShare(exit)`
- Renders `exit.authorHandle` and formatted date via `utils/date.js`
- If `exit.almostOut` is true, renders almost-out badge

## Function signature
```js
export default function renderExitCard(exit, { onCounterClick, onShare } = {})
```

## Does NOT handle
- Data fetching
- Routing
- State management
- Comments
- Auth
