# Self-hosted Fredoka

The app used to pull Fredoka from `fonts.googleapis.com`. That meant every
child's browser sent its IP address to Google on every page load. An IP is a
persistent identifier, and handing one to a third party is outside COPPA's
"support for internal operations" exception, so the Google links were removed
from `base.html`.

The app currently falls back to a rounded system stack
(`"Trebuchet MS", "Segoe UI", system-ui, sans-serif`). It looks fine; it just
isn't Fredoka.

## Why the @font-face rules are not in style.css yet

Production serves static files through WhiteNoise's
`CompressedManifestStaticFilesStorage`. That backend parses every CSS file at
`collectstatic` time and rewrites each URL it finds to the hashed filename.

**A `url()` pointing at a file that does not exist is a hard error, not a
warning.** `collectstatic` fails, the release command fails, and the container
crash-loops. So the `@font-face` block and the font files have to land in the
same commit. Do not add one without the other.

## Adding the font

Step 1 — fetch the four weights into this directory:

    cd cybergame/static/cybergame/fonts
    for w in 400 500 600 700; do
      curl -sL -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36" \
        "https://fonts.googleapis.com/css2?family=Fredoka:wght@$w" \
        | grep -oE 'https://[^)]+\.woff2' | head -1 \
        | xargs curl -sL -o "fredoka-$w.woff2"
    done
    ls -l fredoka-*.woff2        # four files, roughly 30-60 KB each

If any file is 0 bytes, stop — do not commit, or the deploy will fail.

Step 2 — paste this at the very top of `../style.css`:

```css
@font-face {
  font-family: "Fredoka";
  src: url("fonts/fredoka-400.woff2") format("woff2");
  font-weight: 400; font-style: normal; font-display: swap;
}
@font-face {
  font-family: "Fredoka";
  src: url("fonts/fredoka-500.woff2") format("woff2");
  font-weight: 500; font-style: normal; font-display: swap;
}
@font-face {
  font-family: "Fredoka";
  src: url("fonts/fredoka-600.woff2") format("woff2");
  font-weight: 600; font-style: normal; font-display: swap;
}
@font-face {
  font-family: "Fredoka";
  src: url("fonts/fredoka-700.woff2") format("woff2");
  font-weight: 700; font-style: normal; font-display: swap;
}
```

Step 3 — prove it before pushing. This is the exact step that fails in
production, and it does not run during normal local development:

    python manage.py collectstatic --noinput

If that succeeds, the deploy will too.

## Licence

Fredoka is licensed under the SIL Open Font License 1.1, which permits
redistribution, including bundled in a repository like this one.
