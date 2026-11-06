# Notices

Stageshow source is MIT licensed; see `LICENSE`.

Imported from [Benji Taylor's Stageshow 1.1.1](https://github.com/benjitaylor/skills/tree/299140fafd08df55a9c234e610c3f64af3f45531/stageshow).

Product and operating-system names, familiar device geometry, app icons, and
illustrated interfaces are used as examples. Those names and marks remain
with their owners; the Stageshow license does not grant trademark rights or
imply endorsement. Adapt examples to the product you are illustrating.

The Radix-inspired look uses publicly documented color and spacing values;
its source is identified in `examples/looks/radix.css`. This copy uses original
letter tiles in `assets/app-icons.ts` in place of upstream app-bundle artwork.
The Wikipedia
study includes two local photographs dedicated under CC0 1.0 (also used
in the Finder, Telegram and annotation studies); their authors,
original source pages and modifications are recorded in
[`examples/wikipedia/PHOTOS.md`](examples/wikipedia/PHOTOS.md). Other scenes
use CSS and vector illustrations. No third-party fonts are bundled, and the
playground does not fetch fonts or photographs from external services at runtime.

The local brand registry in `kit/brands/` includes SVG artwork from SVGL (MIT), payment-icons (Apache 2.0), Cryptocurrency Icons (CC0 1.0), and Simple Icons (CC0 1.0). Linear, American Express and USDC use original letter tiles in this copy. Per-file sources, hashes and license files are listed in [`kit/brands/SOURCES.md`](kit/brands/SOURCES.md). The original artwork and brand usage terms remain with their respective owners.

`Phone frame="photo"` is optional. Supply your own permitted bezel image via
`--ss-phone-photo-light: url(...)` and optionally `--ss-phone-photo-dark`.
Without it, the kit uses its CSS-drawn `pro` frame. No bezel photographs are
bundled.
