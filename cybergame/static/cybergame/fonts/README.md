# Self-hosted Fredoka

The app used to pull Fredoka from `fonts.googleapis.com`. That meant every
child's browser sent its IP address to Google on every page load. An IP is a
persistent identifier, and handing one to a third party is outside COPPA's
"support for internal operations" exception, so the Google links were removed
from `base.html`.

Until the four files below are committed here, the app falls back to a rounded
system font. It looks fine; it just isn't Fredoka.

To add them (run from the repo root):

    cd cybergame/static/cybergame/fonts
    for w in 400 500 600 700; do
      curl -sL -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36" \
        "https://fonts.googleapis.com/css2?family=Fredoka:wght@$w" \
        | grep -oE 'https://[^)]+\.woff2' | head -1 \
        | xargs curl -sL -o "fredoka-$w.woff2"
    done
    ls -l fredoka-*.woff2        # four files, roughly 30-60 KB each

Then commit them. No CSS change is needed; the @font-face rules at the top of
style.css already point at these filenames.

Fredoka is licensed under the SIL Open Font License 1.1, which permits
redistribution, including bundled in a repository like this.
