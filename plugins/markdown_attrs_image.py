import re


def markdown_img_attrs(state, silent):
    # This regex will match the pattern like ![alt text](url){.class-name}
    img_regex = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)\{([^\}]+)\}")

    tokens = state.tokens
    i = 0

    while i < len(tokens):
        token = tokens[i]
        if token.type == "inline" and token.content:
            # Search for the image pattern in the content of the inline token
            match = img_regex.search(token.content)
            if match:
                # Extract alt text, URL, and class
                alt_text = match.group(1)
                url = match.group(2)
                class_name = match.group(3)

                # Create an image token
                img_token = state.push("image", "img", 0)
                img_token.attrs = [
                    ("src", url),
                    ("alt", alt_text),
                    ("class", class_name),
                ]

                # Adjust the content to be just the image tag in markdown
                token.content = (
                    token.content[: match.start()]
                    + f'<img src="{url}" alt="{alt_text}" class="{class_name}">'
                    + token.content[match.end() :]
                )
                i += 1
                continue
        i += 1

    return None
