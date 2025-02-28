import json
from markdown_it import MarkdownIt
from markdown_it.rules_inline import StateInline
import os
import re

# Load emoji mappings from JSON
with open(os.path.join(os.path.dirname(__file__), "emoji_map.json")) as f:
    EMOJI_MAP = json.load(f)["mappings"]

# Compile regex for finding emoji codes
EMOJI_RE = re.compile(r"(:[a-zA-Z0-9_+-]+:)")


def render_emoji(tokens, idx, options, env):
    """Renderer for emoji tokens"""
    return tokens[idx].content


def emoji_plugin(md: MarkdownIt):
    """Plugin to replace emoji shortcodes like `:smile:` with Unicode emojis."""

    def emoji_rule(state: StateInline, silent: bool):
        """Inline rule for detecting and replacing emoji shortcodes."""
        # Only process if we have a colon
        if state.src[state.pos] != ":":
            return False

        # Don't process if we're in the middle of an emoji
        if state.pos > 0 and state.src[state.pos - 1] == ":":
            return False

        match = EMOJI_RE.match(state.src[state.pos : state.pos + 30])
        if not match:
            return False

        emoji_code = match.group(1)
        emoji_unicode = EMOJI_MAP.get(emoji_code)
        if not emoji_unicode:
            return False

        if silent:
            return True

        token = state.push("emoji", "", 0)
        token.content = emoji_unicode
        token.markup = emoji_code

        state.pos += len(emoji_code)
        return True

    # Add custom renderer
    md.renderer.rules["emoji"] = render_emoji

    # Add rule before emphasis
    md.inline.ruler.before("emphasis", "emoji", emoji_rule)


if __name__ == "__main__":
    # Example usage
    md = MarkdownIt().use(emoji_plugin)
    output = md.render("I am happy :smile: and I love coding :computer:!")
    print(output)
    # Print total number of supported emojis
    print(f"Total supported emojis: {len(EMOJI_MAP)}")
