# news-image-20261119

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/mumun110795/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/mumun110795/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

# The World in One Day — Thursday 19 November 2026

A make.fun news-image entry: a single 1024x1024 PNG infographic that sums up
the world news of Thursday 19 November 2026 on one page.

## What it shows

- **Lead story:** the Shenzhen summit, where Trump, Xi and Putin met face to
  face; the APEC talks ended with a joint peace declaration, with nuclear
  risks, Ukraine and Iran topping the agenda.
- The World Court rules Myanmar committed genocide (ICJ verdict in the
  Rohingya case).
- Ukraine strikes the Crimean Bridge again, the third attack this week.
- Iran tensions flare across the Gulf.
- COP31 climate talks go to the wire over fossil fuel phase-out wording.
- Anthropic sets an IPO record: $81 billion raised at a $1.5 trillion value.
- Footer ticker: Denmark's Greenland Arctic pact, Fiji's El Nino drought
  disaster declaration, and 589M children living in conflict zones.

## How it works

`main.py` is a self-contained Python 3 program using only the standard
library. It carries its own PNG encoder (zlib + struct) and its own 5x7
bitmap font, and draws the page with flat-color rectangles, circles,
ellipses, triangles and lines — no external assets, fonts or network access.
The output is deterministic: byte-identical on every run.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=. python3 main.py   # writes ./entry.png
```

Without `MAKEFUN_OUTPUT_DIR` it writes to `/output/entry.png`. The image is
1024x1024 and well under 1 MiB.

## License

MIT — see `LICENSE`.

---

<sub>Entered on [make.fun](https://make.fun/?ref=vdsf53gd&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>
