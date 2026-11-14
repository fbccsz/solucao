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
reported on 13 November 2026, and each was checked against that day's current-
events record (which cites the outlets below) before it went in:

1. **Lead, Bahrain / Gulf.** Iran says it destroyed a US early-warning radar in
   Bahrain as retaliation for a US strike on telecom infrastructure at Sirik
   (Türkiye Today). Drawn as a radar dome on a platform with a damaged wedge,
   an impact burst, and an incoming missile trail over water.
2. **New Orleans / USA.** A tanker and the cruise ship American Heritage
   collided in the Mississippi; the cruise ship, with 130 aboard, sank and
   everyone aboard survived (BBC, CNN). Drawn as the heeled ship with the
   tanker's bow alongside.
3. **USA / aviation.** The FAA issued a nationwide ground stop over a
   communications failure, later lifted (Bloomberg, Reuters). Drawn as a
   grounded airliner under a stop bar, with the tower behind.
4. **Assam / India.** A bus and a truck collided at Golaghat: 26 killed, 11
   injured (Al Jazeera, Xinhua). Drawn as the two vehicles on the road.
5. **Nairobi / Kenya.** An under-construction building partially collapsed:
   six killed, five injured (Xinhua). Drawn as a slab on props with rubble.

Nothing is invented: no invented numbers, no speculation shown as fact, and no
story from another day. The footer says what the page is, an illustrated
summary of reported news and not a photograph.

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
