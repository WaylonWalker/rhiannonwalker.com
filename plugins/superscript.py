from markdown_it import MarkdownIt
from markdown_it.rules_inline import StateInline


def superscript_plugin(md: MarkdownIt):
    """Plugin to replace `29^th^` with `29<sup>th</sup>`"""

    def superscript_rule(state: StateInline, silent: bool):
        """Inline rule for detecting and replacing `29^th^` style superscript expressions."""
        start = state.pos
        max_pos = state.posMax

        # Ensure we have `^` followed by content and a closing `^`
        if state.src[start] != "^":
            return False

        if start + 2 >= max_pos:  # Ensure there's at least one character after `^`
            return False

        end = state.src.find("^", start + 1)
        if end == -1 or end >= max_pos:
            return False

        if silent:
            return False  # Don't modify in silent mode

        # Extract superscript content
        sup_text = state.src[start + 1 : end].strip()  # Remove unwanted spaces

        # Open `<sup>` tag
        state.push("sup_open", "sup", 1)

        # Add the actual superscript text
        token = state.push("text", "", 0)
        token.content = sup_text  # Set content inside `<sup>...</sup>`

        # Close `</sup>` tag
        state.push("sup_close", "sup", -1)

        # Move parser position past processed text
        state.pos = end + 1
        return True

    md.inline.ruler.before("emphasis", "superscript", superscript_rule)


if __name__ == "__main__":
    # Example usage
    md = MarkdownIt().use(superscript_plugin)
    output = md.render("This is my 29^th^ birthday!")
    print(output)
