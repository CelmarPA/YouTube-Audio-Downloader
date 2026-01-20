# core/ydl_logger.py

from i18n.manager import I18nManager
from utils.app_config import load_config


class YDLLogger:
    """
    Custom logger adapter for yt-dlp.

    This class intercepts yt-dlp log messages and redirects them to the
    application's logging system, applying filtering, internationalization,
    and special handling for restricted content.
    """

    # ⚠️ Noisy and harmless yt-dlp warnings to be ignored
    _IGNORED_WARNINGS = (
        "youtube is forcing sabr streaming",
        "some web client https formats have been skipped",
        "some web_safari client https formats have been skipped",
        "no supported javascript runtime could be found",
        "youtube extraction without a js runtime has been deprecated",
    )

    def __init__(self, downloader):
        """
        Initialize the yt-dlp logger wrapper.

        :param downloader: Downloader instance that will receive log callbacks
        :type downloader: Any
        """

        self.config: dict = load_config()

        self.language: str = self.config.get("language", "en-US")

        self.i18n: I18nManager = I18nManager(language=self.language)

        self.downloader = downloader


    def debug(self, msg: str) -> None:
        """
        Handle yt-dlp debug messages.

        yt-dlp uses debug level for internal spam.
        Intentionally ignored.
        """

        # yt-dlp uses debug for internal spam
        pass

    def warning(self, msg: str) -> None:
        """
        Handle yt-dlp warning messages.

        Filters known noisy warnings before forwarding them.

        :param msg: Warning message
        :type msg: str
        """

        text = msg.lower()

        # 🔇 Ignore known harmless warnings
        if any(w in text for w in self._IGNORED_WARNINGS):
            return

        self._handle(msg, level=self.i18n.t("warning"))

    def error(self, msg: str) -> None:
        """
        Handle yt-dlp error messages.

        :param msg: Error message
        :type msg: str
        """

        self._handle(msg, level=self.i18n.t("error_level"))

    def _handle(self, msg: str, level: str) -> None:
        """
        Central handler for yt-dlp log messages.

        Detects restricted/unavailable content and notifies the downloader.
        Otherwise, forwards the message to the standard application logger.

        :param msg: Log message
        :type msg: str
        :param level: Log level label
        :type level: str
        """

        text: str = msg.lower()

        # 🔒 Private / removed / unavailable content detection
        if any(x in text for x in (
            "private video",
            "video unavailable",
            "removed by the uploader",
            "sign in if you've been granted access",
            "sign in to confirm your age"
        )):
            self.downloader.notify_restricted(msg)
            return

        # Fallback logging
        self.downloader.log(msg, level=level)
