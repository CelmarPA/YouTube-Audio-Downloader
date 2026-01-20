# core/ydl_logger.py

from i18n.manager import I18nManager
from utils.app_config import load_config


class YDLLogger:

    # ⚠️ warnings ruidosos e inofensivos do yt-dlp
    _IGNORED_WARNINGS = (
        "youtube is forcing sabr streaming",
        "some web client https formats have been skipped",
        "some web_safari client https formats have been skipped",
        "no supported javascript runtime could be found",
        "youtube extraction without a js runtime has been deprecated",
    )

    def __init__(self, downloader):
        self.config: dict = load_config()

        self.language: str = self.config.get("language", "en-US")

        self.i18n: I18nManager = I18nManager(language=self.language)

        self.downloader = downloader


    def debug(self, msg: str) -> None:
        # yt-dlp usa debug pra spam interno
        pass

    def warning(self, msg: str) -> None:
        text = msg.lower()

        # 🔇 ignora warnings conhecidos
        if any(w in text for w in self._IGNORED_WARNINGS):
            return

        self._handle(msg, level=self.i18n.t("warning"))

    def error(self, msg: str) -> None:
        self._handle(msg, level=self.i18n.t("error_level"))

    def _handle(self, msg: str, level: str) -> None:
        text: str = msg.lower()

        # 🔒 private / removed / unavailable
        if any(x in text for x in (
            "private video",
            "video unavailable",
            "removed by the uploader",
            "sign in if you've been granted access",
            "sign in to confirm your age"
        )):
            self.downloader.notify_restricted(msg)
            return

        # fallback log
        self.downloader.log(msg, level=level)
