# The World Today - 13 November 2026

One 1024 x 1024 editorial front page, drawn from primitives, for make.fun's
`news-image-01` challenge: sum up Friday 13 November 2026 in a single image.

The program is Python 3, standard library only. No network, no external
assets, no clock, no randomness: two runs write byte-identical files.

## Run

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

With `MAKEFUN_OUTPUT_DIR` unset it writes `/output/entry.png`. Output is a
1024 x 1024 PNG, well under the 1 MiB cap, and the run takes about a second.

## What the picture shows

A masthead, one lead scene, and four panels. Every story is one that was
reported on 13 November 2026:

1. **Lead, Bahrain / Gulf.** Iran says it hit a US early-warning radar in
   Bahrain, retaliation for a US strike on telecom infrastructure at Sirik;
   Gulf shipping is on alert. Drawn as a radar dome on a platform with a
   damaged wedge, an impact burst, and an incoming missile trail over water.
2. **Ukraine / talks.** Zelensky met US envoys Witkoff and Kushner, with
   European partners joining the talks. Drawn as a three-flag table.
3. **Tech / markets.** Nvidia chief Jensen Huang stepped down amid a spy
   scandal, with the US Senate summoning him. Drawn as a falling line and a
   chip.
4. **Assam / India.** A bus and a truck collided at Golaghat: 26 killed, 11
   injured. Drawn as the two vehicles on the road.
5. **Nairobi / Kenya.** An under-construction building collapsed: six killed,
   five injured. Drawn as a slab on props with rubble.

Nothing is invented: no invented numbers, no speculation shown as fact. The
footer says what the page is, an illustrated summary of reported news and not
a photograph.

## Layout rules

Every string is measured before it is drawn. `fit()` returns the largest
glyph scale whose rendering fits the box it is given, `txt_fit()` draws at that
scale and records the measured width, and `build()` asserts that no recorded
string is wider than its box. Captions are three separate strips (art, kicker,
headline) so artwork and text never overlap, and nothing is drawn in light ink
on the light paper background.

## Files

- `main.py` - the program.
- `entry.png` - the rendered image at the submitted commit.
- `LICENSE` - MIT.
