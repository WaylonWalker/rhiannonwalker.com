from markata import Markata
import json

markata = Markata()

with open("tags.json", "w") as fp:
    json.dump(markata.get_tags(), fp)
