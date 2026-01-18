# core/ydl_logger.py


class YDLLogger:

    def __init__(self, downloader):
        self.downloader = downloader

    def debug(self, msg: str) -> None:
        pass

    def warning(self, msg: str) -> None:
        self._handle(msg, level= "WARNING")

    def error(self, msg: str) -> None:
        self._handle(msg, level= "ERROR")

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
