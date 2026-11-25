from urllib.parse import quote


MAX_TEXT = 40


def dummy_image(text: str) -> str:
    """URL of a placeholder picture with the text on it."""
    text = text.strip()
    if len(text) > MAX_TEXT:
        text = text[: MAX_TEXT - 1].rstrip() + "…"
    return f"https://placehold.co/640x360/png?text={quote(text, safe='')}"
