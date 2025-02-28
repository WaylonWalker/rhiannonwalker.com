## not working yet
from markata.hookspec import hook_impl
from markdown_it import MarkdownIt
from markdown_it.rules_core import StateCore
from markdown_it.token import Token


def abbreviations_plugin(md: MarkdownIt, global_abbrs=None):
    """Plugin to replace `*[HTML]: Hyper Text Markup Language`
    with `<abbr title="Hyper Text Markup Language">HTML</abbr>`"""

    if global_abbrs is None:
        global_abbrs = {}

    def extract_abbreviations(state: StateCore):
        """Extract abbreviations from document without modifying state.src"""
        lines = state.src.split("\n")
        local_abbrs = {}

        # Store new lines excluding abbreviation definitions
        new_lines = []
        for line in lines:
            if line.startswith("*[") and "]: " in line:
                abbr, desc = line[2:].split("]: ", 1)
                local_abbrs[abbr.strip()] = desc.strip()
            else:
                new_lines.append(line)

        # Merge local and global abbreviations
        abbrs = {**global_abbrs, **local_abbrs}

        # Process abbreviations in tokens without modifying `state.src`
        for token in state.tokens:
            if token.type == "inline":
                new_children = []
                for child in token.children:
                    if child.type == "text":
                        new_text = child.content
                        for abbr, title in abbrs.items():
                            if abbr in new_text:
                                # Replace the abbreviation with an abbr HTML element
                                parts = new_text.split(abbr)
                                new_children.append(
                                    Token("text", "", 0, content=parts[0])
                                )
                                new_children.append(Token("abbr_open", "abbr", 1))
                                new_children[-1].attrSet("title", title)
                                new_children.append(Token("text", "", 0, content=abbr))
                                new_children.append(Token("abbr_close", "abbr", -1))
                                new_text = "".join(
                                    parts[1:]
                                )  # Continue processing rest
                        if new_text:
                            new_children.append(Token("text", "", 0, content=new_text))
                    else:
                        new_children.append(child)
                token.children = new_children

    md.core.ruler.before("normalize", "abbreviations", extract_abbreviations)


# ======= Markata Integration =======
def get_markata_abbrs(markata):
    """Load abbreviations from Markata config"""
    return markata.config.get("abbreviations", {})


@hook_impl
def configure(markata):
    markata.config.abbreviations = get_markata_abbrs(markata)


@hook_impl
def render(markata):
    md = MarkdownIt().use(abbreviations_plugin, markata.config.abbreviations)
    for post in markata.posts:
        post.html = md.render(post.content)
