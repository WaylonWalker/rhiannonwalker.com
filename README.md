# rhiannonwalker.com

> One Breath at a Time

Rhiannon Walker's corner of the internet — honest stories, creative work, and the small things that help us keep going. Live at [https://rhiannonwalker.com](https://rhiannonwalker.com).

Take what you need, stay as long as you like, and come back when you need another breath.

## About Rhiannon

We are a mid-30s couple with two kids. My husband, son, and daughter are all neurodivergent which gives them superpowers. I on the other hand try to navigate surviving Complex Trauma from all forms along with living through new traumas as they arrive.

I am undergoing a never-ending fight against Neuroendocrine Cancer (NET Cancer) and Ehlers-Danlos Syndrome. I am missing part of my lung, thanks to the wonderful Cancer, but refuse to let it slow me down. Anxiety is always at my side like a third saggy boob along with current undiagnosed medical issues.

> If this all seems chaotic it's because it is. My coping mechanisms are signing myself up for more than I can handle and proving myself wrong.

Just when you thought that was enough for anyone to tackle, well, we purchased our first home on 2/22/22. We were previously renting and had to rush to buy. Our home wasn't perfect, but I have a vision in my mind, and plenty of Pinterest boards to back me up of the beautiful home it will turn into.

If this sounds at all interesting to you — or even a hot mess express that you can't look away from — well follow along!

Full story: [rhiannonwalker.com/about](https://rhiannonwalker.com/about/) (`pages/blog/about.md`)

## What you'll find here

- **Blog / Rhiannon's Life** (`pages/blog/`) — stories on cancer, trauma, anxiety, recovery, family life, and new homeownership
- **Projects** (`pages/project/`) — quilting, appliqué, and other creative work
- **Daily Notes** (`pages/daily/`) — day-to-day notes (private, encrypted — DM for access)
- **Gratitude** (`pages/gratitude/`) — gratitude practice
- **Shots** (`pages/shots/`) — photo grid
- **Pins** (`pages/pins.md`) — pinned links from around the web

Browse by topic: Anxiety, Appliqué, Quilts, Gratitude — plus full [Archive](https://rhiannonwalker.com/archive/).

## Built with

- [markata-go](https://github.com/WaylonWalker/markata-go) — static site generator, config in `markata-go.toml`
- Content in Markdown under `pages/**/*.md`
- Custom theme in `templates-go/`, palettes in `palettes/` (`rhiannon-floral`), assets in `static/`
- Feeds: RSS / Atom / JSON + sitemap, search via Bleve (`/api/search`), Webmention + IndieAuth enabled

## Local development

```bash
just build        # markata-go build (cleans output/ first)
just build-fast   # faster incremental build
just watch        # markata-go serve --fast on :8005
just serve        # full serve on :8005
```

Output goes to `output/`.

## License

MIT — see [LICENSE](LICENSE).
