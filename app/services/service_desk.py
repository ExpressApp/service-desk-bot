"""Functions for service desk."""

localize_sizes = {"MiB": "МБ", "KiB": "КБ", "B": "Б"}


def pretty_file_size(text: str) -> str:
    """Return localize size text."""
    localize_text = text

    for us_size, ru_size in localize_sizes.items():
        if us_size in localize_text:
            localize_text = localize_text.replace(us_size, f" {ru_size}")

    return localize_text
