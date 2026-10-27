---
name: readme-showcase
description: Turn a repository's README.md into an attractive, engaging showcase with a hero banner, badges, real screenshots, demo GIFs, embedded videos, feature grids, a quick start and a polished layout. Use when asked to write, rewrite, improve, beautify or "make attractive" a README, add screenshots/GIFs/demo videos to a README, or prepare a repo for launch or sharing.
---

# README Showcase

Make a README that sells the project in five seconds and gets someone running it in five minutes. Everything in it must be **true for this repo**: real screenshots of the real app, commands that actually work and features that actually exist.

Works with any agent that can read files and run shell commands (Claude Code, Codex, Gemini CLI, OpenCode, Cursor and others).

## Workflow

### 1. Understand the project (don't write yet)
- Read the existing README, the package manifest (`package.json`, `pyproject.toml`, `Cargo.toml`, `*.xcodeproj`, `go.mod`), the entry points, `.github/workflows`, `LICENSE`, and the existing `docs/` and `assets/` folders.
- Find out: what it does, who it's for, what makes it different, the platforms it runs on, how to install and run it, and whether it has a UI, a CLI or is a library.
- Get repo facts with `git remote -v` and, if `gh` is available, `gh repo view --json name,description,homepageUrl,licenseInfo,repositoryTopics,stargazerCount`.
- Keep any content worth saving: license, credits, citations and contributor notes.

### 2. Capture visuals (the most important step)
Store all media in `assets/` (or the existing `docs/images`/`.github/assets`). Use lowercase kebab-case names: `hero.png`, `demo.gif`, `feature-search.png`.

| Project type | What to capture | How |
|:--|:--|:--|
| Web app / site | Hero screenshot, 2–4 feature screens, a 5–15 s demo GIF | Start the dev server, then `scripts/screenshot.mjs` (Playwright) |
| CLI / TUI | A terminal recording of the main command | `vhs` tape → GIF, or `asciinema` + `agg` |
| Desktop / mobile app | Window screenshots, a short screen recording | macOS `screencapture -l<winid>` / `-R x,y,w,h`; iOS `xcrun simctl io booted screenshot`/`recordVideo` |
| Library / API | A code snippet plus its output; an architecture diagram | Carbon-style code image, or a Mermaid diagram (GitHub renders it) |
| Any | Banner / social preview | `scripts/banner.py` (SVG, no dependencies) |

Helpers in this skill's `scripts/` folder:
- `screenshot.mjs <url> <out.png> [--width 1440 --height 900 --dark --full]`: Playwright screenshot, retina, optionally full page.
- `video-to-gif.sh <in.mp4|mov> <out.gif> [width=900] [fps=15]`: high-quality palette GIF through ffmpeg.
- `banner.py --title "Name" --tagline "One line" --out assets/banner.svg [--accent "#7c3aed"]`: gradient hero banner that looks good in light and dark themes.
- `demo.tape`: a VHS template for CLI demos (`vhs scripts/demo.tape`).

Rules for media:
- **Never fake a screenshot** or use stock images that look like the product. If you can't run the app, leave a clearly marked placeholder (`<!-- TODO: screenshot of X -->`) and tell the user.
- Fill the app with realistic sample data before capturing. Hide secrets, tokens, emails and personal paths.
- Keep GIFs under ~5 MB (≤ 15 s, ≤ 900 px wide, 10–15 fps). Use MP4 for anything longer.
- **Video on GitHub:** a committed `.mp4` does *not* play inline from a relative path. Either upload it by dragging it into a GitHub issue or PR comment and paste the resulting `https://github.com/user-attachments/assets/...` URL on its own line (it renders as a player), or link a YouTube thumbnail: `[![Demo](https://img.youtube.com/vi/ID/maxresdefault.jpg)](https://youtu.be/ID)`. Ask the user to upload it if you can't.
- Provide light and dark variants where it matters, using `<picture>` with `prefers-color-scheme`.
- Compress PNGs (`pngquant`/`oxipng` if available) and always write descriptive `alt` text.

### 3. Write the README
Use `references/template.md` as the skeleton, and delete any section that doesn't apply. Order:

1. **Hero:** centred banner or logo, name, a one-line value proposition, badges (keep to ≤ 6–8) and quick links (Website · Docs · Demo · Download).
2. **Visual proof:** the hero screenshot or demo GIF, immediately.
3. **Why / highlights:** 3–6 benefits, each one an emoji plus a bold phrase and one sentence. Benefits, not implementation trivia.
4. **Feature gallery:** a 2-column table of screenshots with captions, or `<details>` blocks for long lists.
5. **Quick start:** the shortest real path to running it, using copy-paste code blocks with language tags. Add prerequisites and install options (brew/npm/pip/release download) as tabs-in-`<details>`.
6. **Usage:** common examples with their output, and a config table if relevant.
7. **How it works:** a Mermaid diagram or short architecture notes (optional).
8. **Roadmap** (checkbox list), **Contributing**, **License**, **Acknowledgements**.
9. A footer with a back-to-top link and a "star the repo" nudge.

See `references/components.md` for ready-made snippets: badges, `<picture>`, image grids, collapsible sections, Mermaid, alerts (`> [!TIP]`), star-history chart, contributors image and a table of contents.

### 4. Style rules
- Lead with the reader's outcome. Use short paragraphs and scannable headings. Use emoji only as section markers, at most one per heading.
- Center the hero section with `<div align="center">` and keep the body left-aligned.
- Give images a set `width` (e.g. `width="100%"` for the hero, `width="49%"` for pairs) so they stay crisp on mobile.
- Use one accent colour across badges, banners and diagrams.
- Every link and badge must resolve, and every command must be one you ran or verified from the source.
- Match the project's tone: playful for side projects, crisp for developer tools and enterprise work.

### 5. Verify
- Run `scripts/check-readme.sh README.md`. It checks that local image paths exist, flags oversized media and lists external links. Fix every failure.
- Preview the rendering: `gh markdown-preview` if installed, or `npx --yes markdown-preview`/VS Code preview, or push to a branch and view it on GitHub.
- Confirm the result reads well at a narrow phone width.
- Report to the user what you captured, what is still a placeholder and anything they need to do (such as uploading a video or setting the repo's social preview image under Settings → General).

Don't commit or push unless the user asks.
