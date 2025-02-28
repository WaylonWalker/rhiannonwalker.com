from markdown_it import MarkdownIt
from markdown_it.rules_inline import StateInline


def keys_plugin(md: MarkdownIt):
    """Plugin to replace `++Ctrl+Alt+Del++` with `<kbd>Ctrl</kbd> + <kbd>Alt</kbd> + <kbd>Del</kbd>`"""

    def keys_rule(state: StateInline, silent: bool):
        """Inline rule for detecting and replacing `++Ctrl+Alt+Del++` style key sequences."""
        start = state.pos
        max_pos = state.posMax

        # Ensure we start with `++`
        if state.src[start : start + 2] != "++":
            return False

        # Find the closing `++`
        end = state.src.find("++", start + 2)
        if end == -1 or end + 2 > max_pos:
            return False

        if silent:
            return False  # Do nothing in silent mode

        keys_text = state.src[start + 2 : end]
        keys = [k.strip() for k in keys_text.split("+")]  # Ensure clean key names

        # Process each key
        for i, key in enumerate(keys):
            # Open `<kbd>` tag
            state.push("kbd_open", "kbd", 1)

            # Add the actual key text
            token = state.push("text", "", 0)
            token.content = key  # Assign the key name as text content

            # Close `</kbd>` tag
            state.push("kbd_close", "kbd", -1)

            # Add a " + " separator if it's not the last key
            if i < len(keys) - 1:
                token = state.push("text", "", 0)
                token.content = " + "

        # Move position past the processed input
        state.pos = end + 2
        return True

    md.inline.ruler.before("emphasis", "keys", keys_rule)


if __name__ == "__main__":
    # Example usage
    md = MarkdownIt().use(keys_plugin)
    output = md.render("Press ++Ctrl+Alt+Del++ to restart.")
    print(output)

