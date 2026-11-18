#!/usr/bin/env python3
"""Build an accurate Firth of Forth coverage SVG from OpenStreetMap data.

Sources (ODbL; https://www.openstreetmap.org/copyright):
  - Firth of Forth water polygon, OSM relation 9493077
  - River Forth centreline, OSM relation 9493112

Land in the frame is the bounding box minus that water polygon. The river
west of the firth (towards Stirling) is drawn as a centreline because the
OSM river relation is a line, not a polygonal area.

This script is a build tool. It is not linked from the site.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from shapely.geometry import box, mapping, shape
from shapely.ops import unary_union
from shapely.validation import make_valid

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
# Default output lives in the site's img/ folder.
OUT = ROOT.parent / "img" / "forth-map.svg"

# Slightly padded from the brief's 55.85–56.20 N, 3.90–3.10 W so Stirling
# (approx. 56.117 N, 3.937 W) sits inside the frame.
WEST, EAST = -3.98, -3.05
SOUTH, NORTH = 55.88, 56.22

SIMPLIFY = 0.00022  # ~15–25 m; keeps the shoreline accurate at this scale

# Theme
WATER = "#15202c"
LAND = "#1c1c22"
COAST = "#e10600"
COAST_WIDTH = 1.35
RIVER = "#3a5570"
RIVER_WIDTH = 2.4
FRAME_BG = "#101012"
FRAME_STROKE = "rgba(243, 239, 230, 0.12)"
PIN = "#e10600"
PIN_CORE = "#1a0505"
INK = "#f3efe6"
INK_SOFT = "#b4afa4"
INK_WATER = "#8aa0b8"
LABEL_RED = "#ff4d42"

# Places (lon, lat) — WGS84
BONESS = (-3.605, 56.017)
QUEENSFERRY = (-3.398, 55.990)  # South Queensferry, near the bridges
EDINBURGH = (-3.189, 55.953)
STIRLING = (-3.937, 56.117)
FALKIRK = (-3.784, 56.001)
FIRTH_LABEL = (-3.26, 56.012)
RIVER_LABEL = (-3.90, 56.145)


def load_geom(path: Path):
    raw = json.loads(path.read_text())
    if raw.get("type") == "FeatureCollection":
        geoms = [shape(f["geometry"]) for f in raw["features"]]
        return unary_union(geoms)
    if raw.get("type") == "Feature":
        return shape(raw["geometry"])
    return shape(raw)


def ring_to_path(coords, proj, close=True) -> str:
    pts = [proj(lon, lat) for lon, lat, *_ in (coords if coords and not isinstance(coords[0], (int, float)) else [])]
    # coords is a sequence of (lon, lat)
    pts = [proj(c[0], c[1]) for c in coords]
    if len(pts) < 2:
        return ""
    d = [f"M{pts[0][0]:.2f},{pts[0][1]:.2f}"]
    d += [f"L{x:.2f},{y:.2f}" for x, y in pts[1:]]
    if close:
        d.append("Z")
    return " ".join(d)


def geom_to_path(g, proj, close=True) -> str:
    g = make_valid(g)
    parts = []
    geoms = []
    if g.geom_type == "Polygon":
        geoms = [g]
    elif g.geom_type == "MultiPolygon":
        geoms = list(g.geoms)
    elif g.geom_type == "LineString":
        return ring_to_path(list(g.coords), proj, close=False)
    elif g.geom_type == "MultiLineString":
        return " ".join(ring_to_path(list(line.coords), proj, close=False) for line in g.geoms)
    for poly in geoms:
        parts.append(ring_to_path(list(poly.exterior.coords), proj, close=True))
        for hole in poly.interiors:
            parts.append(ring_to_path(list(hole.coords), proj, close=True))
    return " ".join(p for p in parts if p)


def main() -> None:
    bbox = box(WEST, SOUTH, EAST, NORTH)

    firth = load_geom(DATA / "firth-of-forth-9493077.geojson")
    river = load_geom(DATA / "river-forth-9493112.geojson")
    firth_c = make_valid(firth).intersection(bbox)
    river_c = make_valid(river).intersection(bbox)
    land = bbox.difference(make_valid(firth))
    # Keep only the land that sits in the frame (identical to land if firth is inside).
    land = land.intersection(bbox)

    firth_s = firth_c.simplify(SIMPLIFY, preserve_topology=True)
    land_s = land.simplify(SIMPLIFY, preserve_topology=True)
    river_s = river_c.simplify(SIMPLIFY, preserve_topology=True)

    def count_pts(g):
        if g.is_empty:
            return 0
        if g.geom_type == "Polygon":
            return len(g.exterior.coords) + sum(len(r.coords) for r in g.interiors)
        if g.geom_type.startswith("Multi"):
            return sum(count_pts(p) for p in g.geoms)
        if "Line" in g.geom_type:
            if g.geom_type == "LineString":
                return len(g.coords)
            return sum(len(p.coords) for p in g.geoms)
        return 0

    print("firth pts", count_pts(firth_c), "->", count_pts(firth_s))
    print("land  pts", count_pts(land), "->", count_pts(land_s))
    print("river pts", count_pts(river_c), "->", count_pts(river_s))

    # Confirm the two markers sit on land, just inland of the south shore.
    from shapely.geometry import Point

    for name, coord in (("Bo'ness", BONESS), ("Queensferry", QUEENSFERRY)):
        p = Point(*coord)
        d = p.distance(firth_c.boundary) * 111320
        print(f"{name}: on_land={land.covers(p)} in_water={firth.covers(p)} shore={d:.0f}m")

    # Projection: equirectangular with cos(mean lat) scaling.
    # Geography fills the frame so the firth can meet the east edge
    # (it continues out to sea) and the land continues on the other sides.
    content_w = 860
    lat0 = (SOUTH + NORTH) / 2
    kx = math.cos(math.radians(lat0))
    width_geo = (EAST - WEST) * kx
    height_geo = NORTH - SOUTH
    scale = content_w / width_geo
    content_h = height_geo * scale
    vb_w = content_w
    vb_h = content_h
    radius = 16
    pad_l = pad_t = 0

    def proj(lon, lat):
        return ((lon - WEST) * kx * scale, (NORTH - lat) * scale)

    land_d = geom_to_path(land_s, proj, close=True)
    firth_d = geom_to_path(firth_s, proj, close=True)
    river_d = geom_to_path(river_s, proj, close=False)
    # Stroke the real coastline only, not the artificial bbox cuts.
    shore = firth_s.boundary.difference(bbox.boundary.buffer(1e-8))
    shore_d = geom_to_path(shore, proj, close=False)

    def pxy(coord):
        return proj(coord[0], coord[1])

    bx, by = pxy(BONESS)
    qx, qy = pxy(QUEENSFERRY)
    ex, ey = pxy(EDINBURGH)
    sx, sy = pxy(STIRLING)
    fx, fy = pxy(FALKIRK)
    wx, wy = pxy(FIRTH_LABEL)
    rx, ry = pxy(RIVER_LABEL)

    # Report projected positions for the markers, in SVG units and as % of the map pane.
    print(f"viewBox={vb_w:.1f}x{vb_h:.1f}")
    print(f"Bo'ness SVG ({bx:.1f},{by:.1f})")
    print(f"Queensferry SVG ({qx:.1f},{qy:.1f})")
    print(f"lon order check: Bo'ness x {bx:.1f} should be west/left of Queensferry x {qx:.1f}: {bx < qx}")
    print(f"lat order check: Bo'ness y {by:.1f} should be north/above Queensferry y {qy:.1f}: {by < qy}")

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" class="map-svg" viewBox="0 0 {vb_w:.2f} {vb_h:.2f}" role="img" aria-labelledby="map-title map-desc">
  <title id="map-title">Coverage area map of Central Scotland</title>
  <desc id="map-desc">Accurate vector outline of the Firth of Forth coastline, from OpenStreetMap data. Lee is based in Bo’ness, on the south shore. Queensferry, also on the south shore beside the Forth bridges, is the meeting point for riders coming from the north. Edinburgh, Falkirk and Stirling are marked for context.</desc>
  <defs>
    <clipPath id="map-frame">
      <rect x="0.5" y="0.5" width="{vb_w-1:.2f}" height="{vb_h-1:.2f}" rx="{radius}"/>
    </clipPath>
  </defs>
  <style>
    .map-pin-name {{ font-family: Oswald, "Arial Narrow", sans-serif; font-size: 26px; letter-spacing: 0.06em; fill: {INK}; }}
    .map-sub {{ font-family: "Source Sans 3", "Segoe UI", sans-serif; font-size: 16px; fill: {INK_SOFT}; }}
    .map-quiet {{ font-family: Oswald, "Arial Narrow", sans-serif; font-size: 16px; letter-spacing: 0.1em; fill: {INK_SOFT}; }}
    .map-water {{ font-family: Oswald, "Arial Narrow", sans-serif; font-size: 18px; letter-spacing: 0.16em; fill: {INK_WATER}; }}
    @media (max-width: 700px) {{
      .map-pin-name {{ font-size: 36px; }}
      .map-sub {{ font-size: 22px; }}
      .map-quiet {{ font-size: 22px; }}
      .map-water {{ font-size: 24px; }}
    }}
  </style>
  <g clip-path="url(#map-frame)">
    <rect width="{vb_w:.2f}" height="{vb_h:.2f}" fill="{LAND}"/>
    <path class="map-firth" d="{firth_d}" fill="{WATER}"/>
    <path class="map-shore" d="{shore_d}" fill="none" stroke="{COAST}" stroke-width="{COAST_WIDTH}" stroke-linejoin="round" stroke-linecap="round"/>
    <path class="map-river" d="{river_d}" fill="none" stroke="{RIVER}" stroke-width="{RIVER_WIDTH}" stroke-linecap="round" stroke-linejoin="round"/>
  </g>
  <rect x="0.5" y="0.5" width="{vb_w-1:.2f}" height="{vb_h-1:.2f}" rx="{radius}" fill="none" stroke="{FRAME_STROKE}" stroke-width="1"/>

  <g class="map-places" font-family="Oswald, 'Arial Narrow', sans-serif" fill="{INK}">
    <text class="map-quiet" x="{ex:.2f}" y="{ey+26:.2f}" text-anchor="end">Edinburgh</text>
    <circle cx="{ex:.2f}" cy="{ey:.2f}" r="2.8" fill="{INK_SOFT}"/>
    <text class="map-quiet" x="{sx+10:.2f}" y="{sy+22:.2f}" text-anchor="start">Stirling</text>
    <circle cx="{sx:.2f}" cy="{sy:.2f}" r="2.8" fill="{INK_SOFT}"/>
    <text class="map-quiet" x="{fx:.2f}" y="{fy+26:.2f}" text-anchor="middle">Falkirk</text>
    <circle cx="{fx:.2f}" cy="{fy:.2f}" r="2.8" fill="{INK_SOFT}"/>
    <text class="map-water" x="{wx:.2f}" y="{wy:.2f}" text-anchor="middle">Firth of Forth</text>
    <text class="map-water" x="{rx:.2f}" y="{ry:.2f}" text-anchor="start">River Forth</text>
  </g>

  <g class="map-pin">
    <circle cx="{bx:.2f}" cy="{by:.2f}" r="11" fill="{PIN}"/>
    <circle cx="{bx:.2f}" cy="{by:.2f}" r="4.2" fill="{PIN_CORE}"/>
    <text class="map-pin-name" x="{bx:.2f}" y="{by+32:.2f}" text-anchor="middle">Bo’ness</text>
    <text class="map-sub" x="{bx:.2f}" y="{by+50:.2f}" text-anchor="middle">Base</text>
  </g>
  <g class="map-pin">
    <circle cx="{qx:.2f}" cy="{qy:.2f}" r="11" fill="{PIN}"/>
    <circle cx="{qx:.2f}" cy="{qy:.2f}" r="4.2" fill="{PIN_CORE}"/>
    <text class="map-pin-name" x="{qx+14:.2f}" y="{qy+32:.2f}" text-anchor="start">Queensferry</text>
    <text class="map-sub" x="{qx+14:.2f}" y="{qy+50:.2f}" text-anchor="start">Meeting point</text>
  </g>
</svg>
'''
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg)
    print("wrote", OUT, "bytes", OUT.stat().st_size)


if __name__ == "__main__":
    main()
