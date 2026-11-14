# The World Today — 13 November 2026

Original editorial illustration for the `news-image-01` challenge.

This repository contains a deterministic Python program that generates a single 1024 × 1024 PNG summarizing major world-news topics from 13 November 2026 in a compact editorial layout.

## Files

- `main.py` — generates the final image.
- `entry.png` — generated output preview.
- `LICENSE` — MIT license.

## Run

```sh
MAKEFUN_OUTPUT_DIR=out python main.py
```

If `MAKEFUN_OUTPUT_DIR` is not set, the program writes `/output/entry.png`.

## Properties

- No external dependencies
- No network access
- Deterministic output
- PNG output at 1024 × 1024
- Output file remains well under the size limit

## Coverage

The illustration highlights eight international topics in a single image:

- Ukraine
- Gaza
- COP31 climate finance
- Strait of Hormuz security
- Microsoft service outage
- Assam bus collision
- Kenya building collapse
- Mississippi river collision
