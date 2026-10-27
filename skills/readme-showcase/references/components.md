# README components

## Badges (shields.io)
`https://img.shields.io/badge/<label>-<message>-<color>?style=for-the-badge&logo=<simpleicons-slug>&logoColor=white`
Dynamic: `/github/stars/O/R`, `/github/v/release/O/R`, `/github/actions/workflow/status/O/R/ci.yml`, `/npm/v/PKG`, `/pypi/v/PKG`, `/github/downloads/O/R/total`.
Use the same `style` for all badges. Tech icons row: `https://skillicons.dev/icons?i=ts,react,python`.

## Light/dark image
```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.png">
  <img src="assets/hero-light.png" width="100%" alt="...">
</picture>
```

## Side-by-side images
`<img src="a.png" width="49%"> <img src="b.png" width="49%">`

## Video
- GitHub-hosted: a bare `https://github.com/user-attachments/assets/<id>` URL on its own line renders as a player.
- YouTube: `[![Watch the demo](https://img.youtube.com/vi/ID/maxresdefault.jpg)](https://youtu.be/ID)`

## Alerts
```
> [!TIP]
> Helpful advice.
```
Types: NOTE, TIP, IMPORTANT, WARNING, CAUTION.

## Collapsible
```html
<details><summary><b>Title</b></summary>

Markdown content (keep the blank line above).
</details>
```

## Keyboard keys
`<kbd>⌘</kbd> + <kbd>K</kbd>`

## Social proof
- Star history: `[![Star History](https://api.star-history.com/svg?repos=O/R&type=Date)](https://star-history.com/#O/R&Date)`
- Contributors: `<a href="https://github.com/O/R/graphs/contributors"><img src="https://contrib.rocks/image?repo=O/R"></a>`

## Typing headline
`https://readme-typing-svg.demolab.com?font=Inter&size=22&center=true&width=600&lines=Line+one;Line+two`

## Table of contents
Only for READMEs longer than ~6 sections. Anchors are lowercase, with spaces turned into `-` and emoji/punctuation dropped (`## 🚀 Quick start` → `#-quick-start`).
