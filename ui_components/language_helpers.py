from __future__ import annotations

import unicodedata

LANGUAGE_LABELS = {
    "aleman": "Alemán",
    "frances": "Francés",
    "espanol": "Español",
    "griego": "Griego",
    "ruso": "Ruso",
}
TRANSLATION_LANGUAGES = {
    "aleman": "de",
    "frances": "fr",
    "espanol": "es",
    "griego": "el",
    "ruso": "ru",
}

PRONUNCIATION_LANGUAGES = {
    "aleman": "de-DE",
    "frances": "fr-FR",
    "espanol": "es-ES",
    "griego": "el-GR",
    "ruso": "ru-RU",
}


def pretty_name(value: str) -> str:
    return value.replace("_", " ").replace("-", " ").strip().title()


def language_config_key(language: str) -> str:
    normalized = unicodedata.normalize("NFD", language.casefold())
    without_accents = "".join(
        char for char in normalized if unicodedata.category(char) != "Mn"
    )
    return without_accents.replace("_", " ").replace("-", " ").strip()
