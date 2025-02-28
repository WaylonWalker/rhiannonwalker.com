from markdown_it import MarkdownIt
from markdown_it.rules_inline import StateInline


def subscript_plugin(md: MarkdownIt):
    """Plugin to replace `H~2~O` with `H<sub>2</sub>O`"""

    def subscript_rule(state: StateInline, silent: bool):
        """Inline rule for detecting and replacing `H~2~O` style subscript expressions."""
        start = state.pos
        max_pos = state.posMax

        # Ensure we have `~` followed by content and a closing `~`
        if state.src[start] != "~":
            return False

        if start + 2 >= max_pos:  # Ensure there's at least one character after `~`
            return False

        end = state.src.find("~", start + 1)
        if end == -1 or end >= max_pos:
            return False

        if silent:
            return False  # Don't do anything in silent mode

        # Extract subscript content
        sub_text = state.src[start + 1 : end].strip()  # Remove unwanted spaces

        # Open `<sub>` tag
        state.push("sub_open", "sub", 1)

        # Add the actual subscript text
        token = state.push("text", "", 0)
        token.content = sub_text  # Set content inside `<sub>...</sub>`

        # Close `</sub>` tag
        state.push("sub_close", "sub", -1)

        # Move parser position past processed text
        state.pos = end + 1
        return True

    md.inline.ruler.before("emphasis", "subscript", subscript_rule)


if __name__ == "__main__":
    # Example usage
    md = MarkdownIt().use(subscript_plugin)
    output = md.render("This is water: H~2~O")
    print(output)
