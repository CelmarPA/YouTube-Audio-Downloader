# i18n/en_US.py

TRANSLATIONS = {
    "url": "Video or Playlist URL",
    "paste": "Paste URL from clipboard",
    "audio_format_label": "Audio Format:",
    "audio_format": "Select audio output format",
    "audio_quality": "Select audio bitrate (kbps applies to MP3/M4A only)",
    "audio_quality_label": "Audio Quality (kbps):",
    "download": "Download",
    "download_btn": "Start downloading the file",
    "pause": "Pause",
    "pause_resume_btn": "Pause and resume the download process",
    "resume": "Resume",
    "cancel": "Cancel",
    "cancel_btn": "Cancel the current download",
    "playlist": "Playlist",
    "keep_original": "Keep Original",
    "keep_original_ckb": "Keep original video file after extraction",
    "normalize_audio": "Normalize Audio",
    "normalize_ckb": "Normalize audio to target LUFS (-14 dB)",
    "resolution_label": "Resolution:",
    "video_resolution": "Select video resolution for download (Auto, 480p, 720p, 1080p), Auto: sets the best resolution available",
    "show_log": "Show log",
    "choose": "Choose folder",
    "choose_label": "Choose…",
    "save_in_label": "Save in:",
    "open": "Open folder",
    "open_label": "Open folder",
    "help": "Open help",
    "theme": "Toggle theme",
    "lang": "Toggle language",

    "app.window.log_validate_url": "No URL provided",
    "app.window.log_on_cancel_clicked_playlist": "⏭️ Cancellation requested: waiting for current item to finish.",
    "app.window.log_on_cancel_clicked_single": "❌ Cancellation requested: download will be interrupted immediately",
    "app.window.log_on_no_resume": "Download paused, discarded by user.",
    "app.window.log_on_file_finished": "Completed:",

    "app.window.show_restart_title": "Restart required",
    "app.window.show_restart": "The application needs to restart to apply the language change.",

    "app.window.state_to_resume_title": "Paused download found",
    "app.window.state_to_resume": "There is a paused download.\nDo you want to resume?",
    "app.window.on_cancel_clicked_title": "Cancel playlist",
    "app.window.on_cancel_clicked": "Do you wish to cancel after the current item finishes?",
    "app.window.show_mix_warming_title": "YouTube MIX detected",
    "app.window.show_mix_warming": (
        "YouTube MIX playlists are automatically generated and customizable.\n\n"
        "They may contain up to 5,000 videos and do not represent a fixed playlist.\n\n"
        "For this reason, playlist download is not supported for MIX content.\n\n"
        "The playlist option will be disabled."
    ),

    "app.window.status_on_cancel_clicked_playlist": "⏭️ Finishing current playlist item...",
    "app.window.status_on_cancel_clicked_single": "Canceling download...",

    "app.window.error_log_validate_not_url": "Please enter a YouTube URL.",
    "app.window.error_log_not_looks_url": "Invalid YouTube URL:",

    "playlist_frame.select_all_btn_label": "Select all",
    "playlist_frame.select_all_btn": "Select all videos in the list",
    "playlist_frame.deselect_all_btn_label": "Deselect all",
    "playlist_frame.deselect_all_btn": "Deselect all videos in the list",
    "playlist_frame.download_btn_label": "Download",
    "playlist_frame.download_btn": "Download the videos selected",
    "playlist_frame.cancel_btn_label": "Cancel",
    "playlist_frame.cancel_btn": "Close the selection window",

    "download_controller.log_restricted": "🔒 Restricted video (authentication required)",
    "download_controller.log_not_entries": "Playlist has no valid videos",
    "download_controller.log_not_selected_entries": "No videos selected, download canceled",
    "download_controller.log_pending_cancel": "Download aborted before start",

    "download_controller.handle_auth_failed_title": "Restricted video skipped",
    "download_controller.handle_auth_failed": "A private or age-restricted video could not be downloaded and was skipped.",
    "download_controller.ask_user_title": "Cancel playlist",
    "download_controller.ask_user": "The playlist download was canceled.\n\nDo you want to keep the current file?\n\n",

    "download_controller.status_entries": "videos loaded",
    "download_controller.status_loading_playlist": "📋 Loading playlist…",
    "download_controller.status_restricted": "🔐 Restricted video, retrying with browser cookies...",

    "download_controller.error_restricted_msg": "Failed to extract video metadata.\nThis video may be private or age-restricted.",
    "download_controller.error_restricted_title": "Restricted video",
    "download_controller.error_not_info": "Failed to extract playlist metadata.\n\nThe playlist may be private, age-restricted, or require authentication.",
    "download_controller.error_not_info_title": "Restricted video",

    "downloader.unknown_video_title": "untitled",
    "downloader.log_selected_entries": "Playlist selection detected",
    "downloader.log_prepare_dirs": "Preparing directories...",
    "downloader.log_skipping_cached": "Skipping cached:",
    "downloader.log_not_should_download": "File already exists, skipping download",
    "downloader.log_cancel_keep": "Canceled with keep",
    "downloader.log_cancel_no_keep": "Canceled with no keep",
    "downloader.log_cancel_after_current": "⏭️ Cancel requested after current item",
    "downloader.log_cancel_immediate": "Immediate cancel requested",
    "downloader.log_format_resolution": "🎞️ Selected format:",
    "downloader.log_starting": "Starting:",
    "downloader.log_remove_tmp": "Temporary file removed:",
    "downloader.log_cancel_wanna_keep": "Playlist canceled — keep current file?",
    "downloader.log_cancel_keep_normalization": "Cancelled with maintain → skipping normalization",
    "downloader.log_files_collected": "Files collected:",
    "downloader.log_not_files_to_process": "No files to normalize",
    "downloader.log_not_files_found": "File not found:",
    "downloader.log_ignore_canceled": "Ignored (canceled):",
    "downloader.log_ignore_blocked": "Ignored (blocked):",
    "downloader.log_ignore_extension": "Ignored (extension):",
    "downloader.log_ignore_already_normalized": "Ignored (already normalized)",
    "downloader.log_normalize_init": "Normalizing:",
    "downloader.log_normalize_finish": "Finished",
    "downloader.log_move_tmp_kept": "Kept:",
    "downloader.log_cleanup": ".part removed:",
    "downloader.log_cleanup_intermediate": "Intermediate removed:",
    "downloader.log_cleanup_ext_not_allowed": "File removed (ext not allowed):",
    "downloader.log_delete_canceled": "File deleted:",
    "downloader.log_pause": "⏸️ Paused by user",
    "downloader.log_resume": "▶️ Resumed by user",
    "downloader.log_save_state_invalid": "State not saved: no active URL or selection",
    "downloader.log_save_state": "State saved",
    "downloader.log_clear_state": "State file removed:",
    "downloader.log_cleanup_empty": "Empty folder removed:",
    "downloader.log_cleanup_tmp_normalize": "temp_normalize removed:",
    "downloader.log_cleanup_after_cancel_finished_folder": "TMP playlist folder removed:",
    "downloader.log_cleanup_after_cancel_finished": "Download canceled",
    "downloader.log_cleanup_after_cancel_finish": "Download finished",
    "downloader.log_retrying": "🔐 Retrying with cookies from:",
    "downloader.log_cleanup_orphan_tmps": "Orphan TMP removed:",

    "downloader.status_prepare_dirs": "Starting download...",
    "downloader.status_pause": "⏸️ Paused",
    "downloader.status_resume": "▶️ Resuming download...",
    "downloader.status_canceled": "Download canceled ❌",
    "downloader.status_canceled_finish": "Download finished ✔",
    "downloader.status_notify_restricted": "🚫 Private / unavailable video skipped",
    "downloader.status_skipped_restricted": "🚫 Skipped restricted video:",

    "downloader.log_error_download_failed": "Download failed:",
    "downloader.log_error_not_entries": "No new item to download",
    "downloader.log_error_restricted_private": "🚫 Restricted / private video skipped:",
    "downloader.log_error_auth_failed": "🚫 Auth failed for video",
    "downloader.log_error_remove_tmp": "Failed to remove temp file:",
    "downloader.log_error_cleanup": "Failed to remove .part:",
    "downloader.log_error_cleanup_intermediate": "Failed to remove intermediary:",
    "downloader.log_error_cleanup_remove": "Failed to remove file:",
    "downloader.log_error_delete_canceled": "File could NOT be deleted (in use):",
    "downloader.log_error_cleanup_tmp_normalize": "Failed to remove temp_normalize:",
    "downloader.log_error_cleanup_after_cancel_finished": "Failed to remove TMP playlist folder:",
    "downloader.log_retrying_failed": "🚫 All browser cookies exhausted",
    "downloader.log_error_cleanup_orphan_tmps": "Failed to remove orphan TMP:",

    "downloader.error_download_playlist": "One or more private / age-restricted videos could not be downloaded and were skipped.",
    "downloader.error_notify_restricted": "Some videos in this playlist are private, removed or unavailable and were skipped.",

    "ready": "Ready",
    "initiating": "Initiating...",
    "canceling": "Canceling download...",
    "paused": "paused",
    "mode": "mode",
    "error": "Error",
    "download_error": "Download Error",
    "yes": "Yes",
    "no": "No",

    "log.no_url": "No URL provided",
    "log.invalid_url": "Invalid URL",
    "log.completed": "Completed",

    "status.progress": "Progress:",
    "status.index": "Item",

    "error.invalid_url": "Invalid YouTube URL.",
    "error.no_url": "Please enter a YouTube URL.",

    "error_level": "ERROR",
    "info": "INFO",
    "cancel_level": "CANCEL",
    "auth": "AUTH",
    "flow": "FLOW",
    "start": "START",
    "cache": "CACHE",
    "skip": "SKIP",
    "download_level": "DOWNLOAD",
    "done": "DONE",
    "normalize": "NORMALIZE",
    "normalize_error": "NORMALIZE|ERROR",
    "video": "VIDEO",
    "video_error": "VIDEO|ERROR",
    "cleanup": "CLEANUP",
    "pause_level": "PAUSE",
    "resume_level": "RESUME",
    "state": "STATE",
    "warning": "WARNING",
    
    "HELP_TEXT": {
        "title": "Help & Quick Guide",
        "header": "YouTube Audio Downloader",

        "intro": (
            "YouTube Audio Downloader is a desktop application designed to download "
            "audio from YouTube videos and playlists with optional video preservation. "
            "It provides fine-grained control over format, quality, and resolution "
            "while maintaining a simple and intuitive workflow."
        ),

        "features_title": "Main Features",
        "features": [
            "✔ Download audio from YouTube videos (MP3 and others)",
            "✔ Optional preservation of the original video file",
            "✔ Video resolution selection when keeping the original file",
            "✔ Playlist support with manual item selection",
            "✔ Pause, resume, and cancel downloads at any time",
            "✔ Fully local application (no cloud processing)"
        ],

        "usage_title": "Quick Usage Guide",
        "usage": [
            "1. Paste a YouTube video or playlist URL",
            "2. Select the desired audio format (MP3 as default)",
            "3. (Optional) Enable \"Keep Original\" to also download the video file",
            "4. If \"Keep Original\" is enabled, choose the preferred video resolution (Auto as default)",
            "5. Choose the destination folder",
            "6. Click Download and monitor progress"
        ],

        "tips_title": "Important Notes",
        "tips": [
            "• The application requires an internet connection to download content from YouTube",
            "• When \"Keep Original\" is disabled, only audio is downloaded and video resolution is ignored",
            "• Resolution selection applies only when keeping the original video file",
            "• The \"Auto\" resolution mode downloads the best available quality for each video",
            "• Some videos may have resolution or access restrictions imposed by YouTube",
            "• Playlist downloads allow manual selection of which videos will be downloaded"
        ],

        "restart_note": (
            "Some configuration changes, such as language selection, "
            "require restarting the application to take effect."
        ),

        "git_label": "GitHub Project:",
        "git_url": "https://github.com/CelmarPA/YouTube-Audio-Downloader"
    }
}
