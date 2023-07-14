"""Module for convert text to EWS HTMLBody."""

from exchangelib import HTMLBody  # type: ignore


def convert_to_ews_html(text: str) -> HTMLBody:
    """Convert text to EWS HTMLBody."""

    formatted_text_lines = []

    text_lines = text.split("\n")

    for line in text_lines:
        index = line.find(":")
        formatted_text_lines.append(
            f"<b>{line[:index]}</b>{line[index:]}<br>"  # noqa: WPS221, WPS237
        )

    return HTMLBody("".join(formatted_text_lines))
