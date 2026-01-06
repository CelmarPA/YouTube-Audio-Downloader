# utils/sanitize.py

import re
import unicodedata


def sanitize_filename(name: str) -> str:
    """
    Sanitize a filename to remove invalid characters and normalize it.

    Args:
        name (str): Original filename.

    Returns:
        str: Sanitized filename safe for filesystem.
    """

    if not name:
        return "untitled"
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")
    name = re.sub(r"[^A-Za-z0-9._@-]+", "_", name)
    name = re.sub(r"_+", "_", name)

    return name.strip("_")
