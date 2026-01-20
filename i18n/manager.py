# i18n/manager.py

from i18n.pt_BR import TRANSLATIONS as PT
from i18n.en_US import TRANSLATIONS as EN


class I18nManager:
    """
    Internationalization (i18n) manager.

    This class provides access to translated strings based on the
    currently selected language. It supports runtime language switching
    and safe fallback behavior.
    """

    SUPPORTED_LANGUAGES : dict = {
        "pt-BR": PT,
        "en-US": EN,
    }

    def __init__(self,  language="en-US") -> None:
        """
        Initialize the I18nManager with a default language.

        :param language: Language code (e.g., 'en-US', 'pt-BR')
        :type language: str
        """

        self.language = language

    def set_language(self, lang: str) -> None:
        """
        Change the active language if supported.

        :param lang: Language code to switch to
        :type lang: str
        """

        if lang in self.SUPPORTED_LANGUAGES:
            self.language = lang

    def t(self, key: str) -> str:
        """
        Translate a key to the current language.

        If the key is not found, the key itself is returned as fallback.

        :param key: Translation key
        :type key: str
        :return: Translated string or key if not found
        :rtype: str
        """

        return self.SUPPORTED_LANGUAGES[self.language].get(key, key)

    def help_text(self, key: str) -> dict:
        """
        Retrieve structured help text for a given key.

        This method is intended for tooltips, help dialogs, or
        extended UI descriptions.

        :param key: Help text key
        :type key: str
        :return: Help text dictionary
        :rtype: dict
        """

        return self.SUPPORTED_LANGUAGES[self.language].get(key)
