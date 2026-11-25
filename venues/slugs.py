"""Формирование URL-идентификатора (slug) площадки из русского названия."""
from django.utils.text import slugify

TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}


def make_slug(name: str, pk: int) -> str:
    """Вернуть slug вида «aktovyy-zal-1».

    slugify() отбрасывает кириллицу, поэтому сначала транслитерируем.
    Идентификатор в конце делает slug уникальным даже для похожих названий.
    """
    latin = "".join(TRANSLIT.get(char, char) for char in name.lower())
    return f"{slugify(latin) or 'venue'}-{pk}"
