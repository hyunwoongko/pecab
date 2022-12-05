import emoji
import regex

_emojis = {}
unicodes = [
    "‍",
    "︀",
    "︁",
    "︂",
    "︃",
    "︄",
    "︅",
    "︆",
    "︇",
    "︈",
    "︉",
    "︊",
    "︋",
    "︌",
    "︍",
    "︎",
    "️",
]

try:
    for lang in ["pt", "it", "es", "en"]:
        _emojis.update(emoji.unicode_codes.UNICODE_EMOJI[lang])
except Exception as e:
    raise ImportError("pecab requires `emoji==1.2.0`. " "please install that version.")

_emojis.update({k: "unicode" for k in unicodes})


def get_emoji(text):
    emoji_list = []
    flags = regex.findall("[\U0001F1E6-\U0001F1FF]", text)

    for grapheme in regex.findall(r"\X", text):
        if any(char in _emojis for char in grapheme):
            emoji_list.append(grapheme)

    return emoji_list + flags
