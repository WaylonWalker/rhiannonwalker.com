from markdown_it import MarkdownIt
from markdown_it.rules_inline import StateInline


def mark_plugin(md: MarkdownIt):
    """Plugin to replace `==marked==` with `<mark>marked</mark>`"""

    def mark_rule(state: StateInline, silent: bool):
        """Inline rule for detecting and replacing `==marked==` style highlighting."""
        start = state.pos
        max_pos = state.posMax

        # Ensure we have `==` at the start
        if state.src[start : start + 2] != "==":
            return False

        # Find closing `==`
        end = state.src.find("==", start + 2)
        if end == -1 or end + 2 > max_pos:
            return False

        if silent:
            return False  # Don't modify in silent mode

        # Extract marked text
        marked_text = state.src[start + 2 : end].strip()  # Strip spaces

        # Open `<mark>` tag
        state.push("mark_open", "mark", 1)

        # Add marked text
        token = state.push("text", "", 0)
        token.content = marked_text

        # Close `</mark>` tag
        state.push("mark_close", "mark", -1)

        # Move parser position past processed text
        state.pos = end + 2
        return True

    md.inline.ruler.before("emphasis", "mark", mark_rule)


if __name__ == "__main__":
    # Example usage
    md = MarkdownIt().use(mark_plugin)
    output = md.render("This is ==important== text.")
    print(output)
