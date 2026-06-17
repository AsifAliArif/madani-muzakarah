import json
import re
from difflib import SequenceMatcher
from html import escape

QURAN_BRACKET_START = "\ufd3f"
QURAN_BRACKET_END = "\ufd3e"


def fuzzy_find_position(text: str, needle: str) -> tuple[int, int] | None:
    if not needle or not text:
        return None
    if needle in text:
        idx = text.index(needle)
        return idx, idx + len(needle)
    best_ratio = 0.0
    best_span = None
    nlen = len(needle)
    for i in range(len(text)):
        window = text[i : i + nlen + 10]
        ratio = SequenceMatcher(None, needle, window[:nlen]).ratio()
        if ratio > best_ratio and ratio >= 0.75:
            best_ratio = ratio
            best_span = (i, i + nlen)
    return best_span


def wrap_quran_text(text: str) -> str:
    text = text.strip()
    if text.startswith(QURAN_BRACKET_START):
        return text
    return f"{QURAN_BRACKET_START}{text}{QURAN_BRACKET_END}"


def apply_ai_formatting_to_html(html: str, extracted_data: list[dict]) -> str:
    plain = re.sub(r"<[^>]+>", "", html)
    plain = plain.replace("&nbsp;", " ")

    for item in extracted_data:
        original = item.get("original_text_found", "")
        processed = item.get("processed_text_with_aeraab", original)
        text_type = item.get("type", "arabic")

        if not original:
            continue

        span = fuzzy_find_position(plain, original)
        if not span:
            if original in html:
                replacement = processed
                if text_type == "quran":
                    replacement = wrap_quran_text(processed)
                    css_class = "quran-text"
                else:
                    css_class = "arabic-text"
                safe = escape(replacement)
                html = html.replace(escape(original), f'<span class="{css_class}">{safe}</span>', 1)
            continue

        display_text = wrap_quran_text(processed) if text_type == "quran" else processed
        css_class = "quran-text" if text_type == "quran" else "arabic-text"
        safe = escape(display_text)
        replacement = f'<span class="{css_class}">{safe}</span>'

        if original in html:
            html = html.replace(escape(original), replacement, 1)
        elif original in plain:
            html = html.replace(original, replacement, 1)

    return html


def parse_llm_json(response_text: str) -> list[dict]:
    text = response_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
        return data.get("extracted_data", [])
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            data = json.loads(match.group())
            return data.get("extracted_data", [])
    return []
