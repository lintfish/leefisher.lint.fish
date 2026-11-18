# Lee Fisher — advanced motorcycle training (preview)

Local preview of a static site for Lee Fisher’s new advanced motorcycle training business, intended later for GitHub Pages at `https://leefisher.lint.fish`.

Plain HTML, CSS, and a little vanilla JavaScript. No build step, no bundler, no package manager.

This copy is a test preview: it is marked `noindex, nofollow`, and `robots.txt` disallows all crawlers. Do not treat it as a public launch.

## Structure

```
leefisher-site/
  index.html      Home page (hero, about, courses, how it works, coverage, FAQs, vouchers, contact)
  404.html        Custom not-found page
  CNAME           GitHub Pages custom domain: leefisher.lint.fish
  robots.txt      Disallows all crawlers
  favicon.svg     Chevron-in-bezel mark (matches the placeholder logo)
  css/styles.css  Self-contained dark-only styles
  js/config.js    The one place to set the business name and phone number
  js/main.js      Applies the config, plus the mobile nav
  img/logo.svg        Placeholder logo
  img/forth-map.svg   Coverage map (OpenStreetMap coastline)
  tools/              Map build script and source GeoJSON (not linked from the site)
  README.md           This file
```

## Changing the business name and phone number

Edit `js/config.js` only:

```js
window.SITE_CONFIG = {
  businessName: "[Business Name]",
  phoneDisplay: "07XXX XXXXXX",
  phoneTel: "07XXXXXXXXX"
};
```

The wordmark, page titles, and `tel:` / `sms:` links all read from that file. The logo is a symbol-only placeholder (no name drawn into the SVG), so it can stay when the name is decided.

## Design

- Palette: near-black asphalt (`#080809`) with a racing-red accent (`#e10600`) and a slightly lighter red (`#ff4d42`) for small text and links, plus warm off-white text (`#f3efe6`). Buttons use white text on `#e10600`.
- Fonts: [Oswald](https://fonts.google.com/specimen/Oswald) for display, [Source Sans 3](https://fonts.google.com/specimen/Source+Sans+3) for body text (Google Fonts).
- Motifs: vanishing-point road, speed lines, a decorative tachometer, and an accurate Firth of Forth vector map built from OpenStreetMap data — all CSS/SVG, no stock photographs. Map data © OpenStreetMap contributors (ODbL).

## Notes

- Prices are shown as provisional, as agreed.
- Past roles (police motorcyclist, IAM RoadSmart examiner, IAM Masters Mentor) are mentioned in plain text only. There are no IAM, RoadSmart, or police logos, and a disclaimer states the business is not affiliated with or endorsed by Police Scotland or IAM RoadSmart.
- Invented supporting copy (for example the “how it works” steps, and some course blurbs) is marked “Draft wording — to be confirmed.”
- The site has not been published from this folder. Creating a GitHub repo, pushing, or going live needs an explicit OK.
