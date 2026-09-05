---
title: Rhiannon Walker
description: One Breath at a Time
date: 2026-09-04
published: true
slug: ""
template: home.html
jinja: true
hero_first_name: Rhiannon
hero_last_name: Walker
hero_tagline: One Breath at a Time
hero_avatar: https://dropper.wayl.one/api/file/858c063f-d5ac-45bc-8c01-b347fb01becd.png
hero_links:
  - label: About
    url: /about/
  - label: Archive
    url: /archive/
  - label: Projects
    url: /projects/
---

Welcome to my corner of the internet.

## Recent writing

{{ render_feed("blog", 5, "card") }}

## Projects

{{ render_feed("projects", 5, "card") }}
