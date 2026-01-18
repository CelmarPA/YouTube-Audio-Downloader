# i18n/pt_BR.py

TRANSLATIONS = {
    "url": "URL do vídeo ou playlist",
    "paste": "Colar URL da área de transferência",
    "audio_format_label": "Formato de áudio:",
    "audio_format": "Selecione o formato de saída de áudio",
    "audio_quality": "Selecione o bitrate de áudio (kbps aplica-se apenas a MP3/M4A)",
    "audio_quality_label": "Qualidade de áudio (kbps):",
    "download": "Baixar",
    "download_btn": "Iniciar o download do arquivo",
    "pause": "Pausar",
    "pause_resume_btn": "Pausar e retomar o processo de download",
    "resume": "Retomar",
    "cancel": "Cancelar",
    "cancel_btn": "Cancelar o download atual",
    "playlist": "Playlist",
    "keep_original": "Manter original",
    "keep_original_ckb": "Manter o arquivo de vídeo original após a extração",
    "normalize_audio": "Normalizar áudio",
    "normalize_ckb": "Normalizar o áudio para o LUFS alvo (-14 dB)",
    "resolution_label": "Resolução:",
    "video_resolution": "Selecione a resolução do vídeo (Auto, 480p, 720p, 1080p). Auto: define a melhor resolução disponível",
    "show_log": "Mostrar log",
    "choose": "Escolher pasta",
    "choose_label": "Escolher…",
    "save_in_label": "Salvar em:",
    "open": "Abrir pasta",
    "open_label": "Abrir pasta",
    "help": "Abrir ajuda",
    "theme": "Alternar tema",
    "lang": "Alternar idioma",

    "app.window.log_validate_url": "Nenhuma URL fornecida",
    "app.window.log_on_cancel_clicked_playlist": "⏭️ Cancelamento solicitado: aguardando o item atual finalizar.",
    "app.window.log_on_cancel_clicked_single": "❌ Cancelamento solicitado: o download será interrompido imediatamente",
    "app.window.log_on_no_resume": "Download pausado e descartado pelo usuário.",
    "app.window.log_on_file_finished": "Concluído:",

    "app.window.show_restart_title": "Reinicialização necessária",
    "app.window.show_restart": "O aplicativo precisa ser reiniciado para aplicar a alteração de idioma.",

    "app.window.state_to_resume_title": "Download pausado encontrado",
    "app.window.state_to_resume": "Existe um download pausado.\nDeseja retomá-lo?",
    "app.window.on_cancel_clicked_title": "Cancelar playlist",
    "app.window.on_cancel_clicked": "Deseja cancelar após o item atual finalizar?",
    "app.window.show_mix_warming_title": "MIX do YouTube detectado",
    "app.window.show_mix_warming": (
        "Playlists MIX do YouTube são geradas automaticamente e personalizáveis.\n\n"
        "Elas podem conter até 5.000 vídeos e não representam uma playlist fixa.\n\n"
        "Por esse motivo, o download de playlists não é suportado para conteúdos MIX.\n\n"
        "A opção de playlist será desativada."
    ),

    "app.window.status_on_cancel_clicked_playlist": "⏭️ Finalizando o item atual da playlist...",
    "app.window.status_on_cancel_clicked_single": "Cancelando download...",

    "app.window.error_log_validate_not_url": "Por favor, insira uma URL do YouTube.",
    "app.window.error_log_not_looks_url": "URL do YouTube inválida:",

    "playlist_frame.select_all_btn_label": "Selecionar tudo",
    "playlist_frame.select_all_btn": "Selecionar todos os vídeos da lista",
    "playlist_frame.deselect_all_btn_label": "Desmarcar tudo",
    "playlist_frame.deselect_all_btn": "Desmarcar todos os vídeos da lista",
    "playlist_frame.download_btn_label": "Baixar",
    "playlist_frame.download_btn": "Baixar os vídeos selecionados",
    "playlist_frame.cancel_btn_label": "Cancelar",
    "playlist_frame.cancel_btn": "Fechar a janela de seleção",

    "download_controller.log_restricted": "🔒 Vídeo restrito (autenticação necessária)",
    "download_controller.log_not_entries": "A playlist não possui vídeos válidos",
    "download_controller.log_not_selected_entries": "Nenhum vídeo selecionado, download cancelado",
    "download_controller.log_pending_cancel": "Download abortado antes de iniciar",

    "download_controller.handle_auth_failed_title": "Vídeo restrito ignorado",
    "download_controller.handle_auth_failed": "Um vídeo privado ou com restrição de idade não pôde ser baixado e foi ignorado.",
    "download_controller.ask_user_title": "Cancelar playlist",
    "download_controller.ask_user": "O download da playlist foi cancelado.\n\nDeseja manter o arquivo atual?\n\n",

    "download_controller.status_entries": "vídeos carregados",
    "download_controller.status_loading_playlist": "📋 Carregando playlist…",
    "download_controller.status_restricted": "🔐 Vídeo restrito, tentando novamente com cookies do navegador...",

    "download_controller.error_restricted_msg": "Falha ao extrair os metadados do vídeo.\nEste vídeo pode ser privado ou ter restrição de idade.",
    "download_controller.error_restricted_title": "Vídeo restrito",
    "download_controller.error_not_info": "Falha ao extrair os metadados da playlist.\n\nA playlist pode ser privada, ter restrição de idade ou exigir autenticação.",
    "download_controller.error_not_info_title": "Vídeo restrito",

    "downloader.unknown_video_title": "sem título",
    "downloader.log_selected_entries": "Seleção de playlist detectada",
    "downloader.log_prepare_dirs": "Preparando diretórios...",
    "downloader.log_skipping_cached": "Ignorando cache:",
    "downloader.log_not_should_download": "O arquivo já existe, download ignorado",
    "downloader.log_cancel_keep": "Cancelado mantendo o arquivo",
    "downloader.log_cancel_no_keep": "Cancelado sem manter o arquivo",
    "downloader.log_cancel_after_current": "⏭️ Cancelamento solicitado após o item atual",
    "downloader.log_cancel_immediate": "Cancelamento imediato solicitado",
    "downloader.log_format_resolution": "🎞️ Formato selecionado:",
    "downloader.log_starting": "Iniciando:",
    "downloader.log_remove_tmp": "Arquivo temporário removido:",
    "downloader.log_cancel_wanna_keep": "Playlist cancelada — manter o arquivo atual?",
    "downloader.log_cancel_keep_normalization": "Cancelado mantendo → pulando normalização",
    "downloader.log_files_collected": "Arquivos coletados:",
    "downloader.log_not_files_to_process": "Nenhum arquivo para normalizar",
    "downloader.log_not_files_found": "Arquivo não encontrado:",
    "downloader.log_ignore_canceled": "Ignorado (cancelado):",
    "downloader.log_ignore_blocked": "Ignorado (bloqueado):",
    "downloader.log_ignore_extension": "Ignorado (extensão):",
    "downloader.log_ignore_already_normalized": "Ignorado (já normalizado)",
    "downloader.log_normalize_init": "Normalizando:",
    "downloader.log_normalize_finish": "Finalizado",
    "downloader.log_move_tmp_kept": "Mantido:",
    "downloader.log_cleanup": ".part removido:",
    "downloader.log_cleanup_intermediate": "Intermediário removido:",
    "downloader.log_cleanup_ext_not_allowed": "Arquivo removido (extensão não permitida):",
    "downloader.log_delete_canceled": "Arquivo deletado:",
    "downloader.log_pause": "⏸️ Pausado pelo usuário",
    "downloader.log_resume": "▶️ Retomado pelo usuário",
    "downloader.log_save_state_invalid": "Estado não salvo: nenhuma URL ou seleção ativa",
    "downloader.log_save_state": "Estado salvo",
    "downloader.log_clear_state": "Arquivo de estado removido:",
    "downloader.log_cleanup_empty": "Pasta vazia removida:",
    "downloader.log_cleanup_tmp_normalize": "temp_normalize removido:",
    "downloader.log_cleanup_after_cancel_finished_folder": "Pasta TMP da playlist removida:",
    "downloader.log_cleanup_after_cancel_finished": "Download cancelado",
    "downloader.log_cleanup_after_cancel_finish": "Download finalizado",
    "downloader.log_retrying": "🔐 Tentando novamente com cookies de:",
    "downloader.log_cleanup_orphan_tmps": "TMP órfão removido:",

    "downloader.status_prepare_dirs": "Iniciando download...",
    "downloader.status_pause": "⏸️ Pausado",
    "downloader.status_resume": "▶️ Retomando download...",
    "downloader.status_canceled": "Download cancelado ❌",
    "downloader.status_canceled_finish": "Download finalizado ✔",
    "downloader.status_notify_restricted": "🚫 Vídeo privado / indisponível ignorado",
    "downloader.status_skipped_restricted": "🚫 Vídeo restrito ignorado:",

    "downloader.log_error_download_failed": "Falha no download:",
    "downloader.log_error_not_entries": "Nenhum novo item para baixar",
    "downloader.log_error_restricted_private": "🚫 Vídeo restrito / privado ignorado:",
    "downloader.log_error_auth_failed": "🚫 Falha de autenticação para o vídeo",
    "downloader.log_error_remove_tmp": "Falha ao remover arquivo temporário:",
    "downloader.log_error_cleanup": "Falha ao remover .part:",
    "downloader.log_error_cleanup_intermediate": "Falha ao remover intermediário:",
    "downloader.log_error_cleanup_remove": "Falha ao remover arquivo:",
    "downloader.log_error_delete_canceled": "O arquivo NÃO pôde ser deletado (em uso):",
    "downloader.log_error_cleanup_tmp_normalize": "Falha ao remover temp_normalize:",
    "downloader.log_error_cleanup_after_cancel_finished": "Falha ao remover pasta TMP da playlist:",
    "downloader.log_retrying_failed": "🚫 Todos os cookies do navegador foram esgotados",
    "downloader.log_error_cleanup_orphan_tmps": "Falha ao remover TMP órfão:",

    "downloader.error_download_playlist": "Um ou mais vídeos privados / com restrição de idade não puderam ser baixados e foram ignorados.",
    "downloader.error_notify_restricted": "Alguns vídeos desta playlist são privados, removidos ou indisponíveis e foram ignorados.",

    "ready": "Pronto",
    "initiating": "Iniciando...",
    "canceling": "Cancelando download...",
    "paused": "pausado",
    "mode": "modo",

    "log.no_url": "Nenhuma URL fornecida",
    "log.invalid_url": "URL inválida",
    "log.completed": "Concluído",

    "status.progress": "Progresso:",
    "status.index": "Item",

    "error.invalid_url": "URL do YouTube inválida.",
    "error.no_url": "Por favor, insira uma URL do YouTube.",

    "HELP_TEXT": {
        "title": "Ajuda & Guia Rápido",
        "header": "YouTube Audio Downloader",

        "intro": (
            "YouTube Audio Downloader é um aplicativo desktop projetado para baixar "
            "áudio de vídeos e playlists do YouTube, com opção de preservação do vídeo original. "
            "Ele oferece controle detalhado sobre formato, qualidade e resolução, "
            "mantendo um fluxo de uso simples e intuitivo."
        ),

        "features_title": "Principais Recursos",
        "features": [
            "✔ Baixar áudio de vídeos do YouTube (MP3 e outros formatos)",
            "✔ Opção de preservar o arquivo de vídeo original",
            "✔ Seleção de resolução do vídeo ao manter o arquivo original",
            "✔ Suporte a playlists com seleção manual dos itens",
            "✔ Pausar, retomar e cancelar downloads a qualquer momento",
            "✔ Aplicativo totalmente local (sem processamento em nuvem)"
        ],

        "usage_title": "Guia Rápido de Uso",
        "usage": [
            "1. Cole a URL de um vídeo ou playlist do YouTube",
            "2. Selecione o formato de áudio desejado (MP3 como padrão)",
            "3. (Opcional) Ative \"Manter Original\" para também baixar o arquivo de vídeo",
            "4. Se \"Manter Original\" estiver ativado, escolha a resolução de vídeo desejada (Auto como padrão)",
            "5. Escolha a pasta de destino",
            "6. Clique em Baixar e acompanhe o progresso"
        ],

        "tips_title": "Notas Importantes",
        "tips": [
            "• O aplicativo requer conexão com a internet para baixar conteúdo do YouTube",
            "• Quando \"Manter Original\" estiver desativado, apenas o áudio será baixado e a resolução do vídeo será ignorada",
            "• A seleção de resolução se aplica somente ao manter o arquivo de vídeo original",
            "• O modo de resolução \"Auto\" baixa a melhor qualidade disponível para cada vídeo",
            "• Alguns vídeos podem ter restrições de resolução ou acesso impostas pelo YouTube",
            "• Downloads de playlists permitem a seleção manual dos vídeos que serão baixados"
        ],

        "restart_note": (
            "Algumas alterações de configuração, como a seleção de idioma, "
            "exigem a reinicialização do aplicativo para entrarem em vigor."
        ),

        "git_label": "Projeto no GitHub:",
        "git_url": "https://github.com/CelmarPA/YouTube-Audio-Downloader"
    }
}
