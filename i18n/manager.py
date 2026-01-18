# i18n/manager.py

from i18n.pt_BR import TRANSLATIONS as PT
from i18n.en_US import TRANSLATIONS as EN


class I18nManager:

    SUPPORTED_LANGUAGES : dict = {
        "pt-BR": PT,
        "en-US": EN,
    }

    def __init__(self,  language="en-US") -> None:
        self.language = language

    def set_language(self, lang: str) -> None:
        if lang in self.SUPPORTED_LANGUAGES:
            self.language = lang

    def t(self, key: str) -> str:
        return self.SUPPORTED_LANGUAGES[self.language].get(key, key)

    def help_text(self, key: str) -> dict:
        return self.SUPPORTED_LANGUAGES[self.language].get(key)