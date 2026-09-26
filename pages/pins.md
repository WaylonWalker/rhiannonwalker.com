---
title: Pins
description: Pinned links from around the web
published: true
slug: pins
template: pins.html
jinja: true
---

{% if feed_posts("pins") %}
{{ render_feed("pins", {"template": "pins-feed-preview.html"}) }}
{% else %}
No pins yet.
{% endif %}
