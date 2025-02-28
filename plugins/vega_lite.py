"""
Markata Plugin: Vega Diagram Renderer

This plugin converts Vega code blocks in Markdown files into rendered Vega diagrams.

# Installation

Ensure Vega-Embed is available in your site. If serving locally, add the script to your template:

```html
<script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
```

# Configuration

Enable the plugin in `markata.toml`:

```toml
[markata]
hooks = ["markata.plugins.vega_renderer"]
```

# Usage

Use Vega code blocks in your Markdown content:

```vega
{
  "$schema": "https://vega.github.io/schema/vega-lite/v4.json",
  "data": {"url": "https://vega.github.io/editor/data/barley.json"},
  "mark": "bar",
  "encoding": {
    "x": {"aggregate": "sum", "field": "yield", "type": "quantitative"},
    "y": {"field": "variety", "type": "nominal"},
    "color": {"field": "site", "type": "nominal"}
  }
}
```

# Notes

- Requires the Markata markdown-it-py backend with the `html` option enabled.
"""

import json
from markata.hookspec import hook_impl
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from markata import Markata

VEGA_BLOCK_RE = re.compile(r"```vega\n(.*?)\n```", re.DOTALL)


@hook_impl
def pre_render(markata: "Markata") -> None:
    for article in markata.iter_articles("processing vega blocks"):
        key = markata.make_hash("vega", article.content)
        if "vega" in article.content:
            article.content = VEGA_BLOCK_RE.sub(replace_vega_block, article.content)


def replace_vega_block(match: re.Match) -> str:
    vega_code = match.group(1).strip()
    vega_block = (
        f"""<div class="vega-chart" data-vega='{json.dumps(vega_code)}'></div>"""
    )
    return vega_block
