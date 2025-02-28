import emoji
import json


def generate_emoji_map():
    """Generate a complete mapping of emoji codes to unicode characters."""
    emoji_map = {}
    
    # Common emoji shortcodes to try
    shortcodes = [
        ":smile:", ":heart:", ":rocket:", ":fire:", ":thumbsup:", ":tada:", 
        ":check:", ":x:", ":warning:", ":bulb:", ":book:", ":computer:", 
        ":star:", ":sparkles:", ":link:", ":wrench:", ":gear:", ":clock:",
        ":eyes:", ":memo:", ":zap:", ":bug:", ":hammer:", ":art:", ":pencil:",
        ":paperclip:", ":file_folder:", ":calendar:", ":chart:", ":mag:",
        ":lock:", ":key:", ":tools:", ":package:", ":bookmark:", ":label:",
        ":dollar:", ":moneybag:", ":credit_card:", ":gem:", ":trophy:",
        ":medal:", ":crown:", ":diamond:", ":gift:", ":party:", ":cake:",
        ":balloon:", ":heart_eyes:", ":sunglasses:", ":muscle:", ":rainbow:",
        ":cloud:", ":umbrella:", ":snowflake:", ":sunny:", ":moon:", ":earth:",
        ":phone:", ":email:", ":inbox:", ":outbox:", ":bell:", ":camera:",
        ":video:", ":microphone:", ":headphones:", ":speaker:", ":battery:",
        ":electric_plug:", ":bulb:", ":flashlight:", ":wrench:", ":hammer:",
        ":nut_and_bolt:", ":gear:", ":chains:", ":link:", ":paperclip:",
        ":scissors:", ":lock:", ":key:", ":hammer_and_wrench:", ":shield:",
        ":warning:", ":no_entry:", ":stop:", ":check:", ":x:", ":question:",
        ":exclamation:", ":information:", ":plus:", ":minus:", ":divide:",
        ":equals:", ":hash:", ":asterisk:", ":copyright:", ":registered:",
        ":tm:", ":arrow_up:", ":arrow_down:", ":arrow_left:", ":arrow_right:",
        ":arrow_up_down:", ":arrow_left_right:", ":arrow_forward:", 
        ":arrow_backward:", ":fast_forward:", ":rewind:", ":play:", ":pause:",
        ":stop:", ":record:", ":shuffle:", ":repeat:", ":skip:", ":previous:",
    ]
    
    # Try each shortcode
    for code in shortcodes:
        try:
            unicode_char = emoji.emojize(code, language='alias')
            if unicode_char != code:  # Only add if conversion was successful
                emoji_map[code] = unicode_char
        except Exception as e:
            print(f"Error with {code}: {e}")
            continue

    return {"mappings": emoji_map}


if __name__ == "__main__":
    # Generate the mapping
    emoji_map = generate_emoji_map()

    # Save to JSON
    with open("emoji_map.json", "w", encoding="utf-8") as f:
        json.dump(emoji_map, f, ensure_ascii=False, indent=4)

    print(f"Generated emoji map with {len(emoji_map['mappings'])} emojis")
