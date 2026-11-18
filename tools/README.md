# Coverage map build

This folder is a build tool. It is not linked from the site.

The coverage map in `img/forth-map.svg` (also inlined on the homepage) is a
vector outline of the real Firth of Forth, generated from OpenStreetMap data.

## Sources

- Firth of Forth water polygon, OSM relation
  [9493077](https://www.openstreetmap.org/relation/9493077)
  (`data/firth-of-forth-9493077.geojson`)
- River Forth centreline, OSM relation
  [9493112](https://www.openstreetmap.org/relation/9493112)
  (`data/river-forth-9493112.geojson`)

Land in the frame is the bounding box minus the firth polygon. The river west
of the firth (towards Stirling) is drawn as a centreline because that OSM
relation is a line, not an area.

Data © OpenStreetMap contributors, [ODbL](https://www.openstreetmap.org/copyright).

## Rebuild

From this directory, with Shapely installed:

```
python3 build_forth_map.py
```

Then copy the new `img/forth-map.svg` into the coverage `<figure>` in
`index.html` if you want the homepage inlined copy to match.

The frame is about 55.88–56.22 N, 3.98–3.05 W (a slight pad on the brief’s
55.85–56.20 N, 3.90–3.10 W so Stirling sits inside). Projection is
equirectangular with `cos(mean latitude)` scaling. The coastline is simplified
to about 15–25 m.
