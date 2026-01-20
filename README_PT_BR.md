# 🎵 YouTube Audio Downloader

Uma **aplicação desktop profissional** para baixar **áudio de vídeos e playlists do YouTube**, com preservação opcional do vídeo, construída com **Python, Tkinter, yt-dlp e FFmpeg**.

Desenvolvida com **arquitetura limpa**, **separação clara de responsabilidades** e **UX de nível profissional**, o projeto foca em confiabilidade, transparência e controle total local.

---

## 📘 Tabela de Conteúdos

* [🎵 YouTube Audio Downloader](#-youtube-audio-downloader)

  * [📘 Tabela de Conteúdos](#-tabela-de-conteúdos)
  * [🔥 Visão Geral](#-visão-geral)
  * [⚡ Principais Funcionalidades](#-principais-funcionalidades)
  * [🚀 Guia Rápido de Uso](#-guia-rápido-de-uso)
  * [📝 Observações Importantes](#-observações-importantes)
  * [🏗 Arquitetura do Projeto](#-arquitetura-do-projeto)
  * [🛠 Tecnologias](#-tecnologias)
  * [💻 Instalação](#-instalação)
  * [⚙ Configuração](#-configuração)
  * [▶ Executando a Aplicação](#-executando-a-aplicação)
  * [📂 Estrutura de Pastas](#-estrutura-de-pastas)
  * [📜 Licença](#-licença)
  * [👤 Autor](#-autor)

---

## 🔥 Visão Geral

**YouTube Audio Downloader** é uma **aplicação desktop totalmente local**, projetada para baixar áudio de vídeos e playlists do YouTube, oferecendo:

✔ Controle detalhado sobre o formato de áudio
✔ Preservação opcional do arquivo de vídeo original
✔ Suporte a playlists com seleção manual de itens
✔ Fluxo de trabalho limpo e intuitivo
✔ Nenhum processamento em nuvem — tudo roda localmente

O projeto prioriza **clareza, segurança e controle**, tornando-o adequado tanto para usuários casuais quanto para avançados.

---

## ⚡ Principais Funcionalidades

* ✔ Baixar áudio de vídeos do YouTube (MP3 e outros formatos)
* ✔ Preservação opcional do arquivo de vídeo original
* ✔ Seleção de resolução do vídeo quando manter o arquivo original
* ✔ Suporte a playlists com seleção manual de vídeos
* ✔ Pausar, retomar e cancelar downloads a qualquer momento
* ✔ Aplicação totalmente local (sem serviços em nuvem)
* ✔ Suporte a idiomas e temas
* ✔ Manipulação segura de arquivos e verificação de normalização

---

## 🚀 Guia Rápido de Uso

1. Cole a **URL de um vídeo ou playlist do YouTube**
2. Selecione o **formato de áudio desejado** (MP3 é o padrão)
3. *(Opcional)* Ative **Manter Original** para também baixar o vídeo
4. Se ativado, escolha a **resolução do vídeo** (Auto por padrão)
5. Escolha a **pasta de destino**
6. Clique em **Download** e acompanhe o progresso

---

## 📝 Observações Importantes

* • É necessária **conexão com a internet** para baixar conteúdos do YouTube
* • Quando **Manter Original** estiver desativado, apenas o áudio é baixado
* • A seleção de resolução aplica-se **somente** ao manter o vídeo original
* • O modo **Auto** baixa a melhor qualidade disponível de cada vídeo
* • Alguns vídeos podem ter **restrições de idade, região ou acesso**
* • Downloads de playlists permitem **seleção manual de vídeos**
* • Algumas alterações de configuração (como idioma) exigem **reiniciar o aplicativo**

---

## 🏗 Arquitetura do Projeto

```
UI (Tkinter)
 └── AppWindow
      ├── Controlador de Downloads
      ├── Modal de Seleção de Playlist
      ├── Internacionalização (i18n)
      ├── Gerenciador de Tema
      └── Lógica de Download (yt-dlp + FFmpeg)
```

A arquitetura é projetada para ser:

* Modular
* Testável
* Fácil de estender
* Fácil de manter

---

## 🛠 Tecnologias

* Python 3.10+
* Tkinter
* yt-dlp
* FFmpeg
* Mutagen (metadados de áudio)
* Configuração baseada em JSON

---

## 💻 Instalação

```bash
git clone https://github.com/CelmarPA/YouTube-Audio-Downloader
cd YouTube-Audio-Downloader
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## ⚙ Configuração

Todas as preferências do usuário são armazenadas localmente em um arquivo JSON de configuração.

Algumas configurações (como idioma) exigem **reinício do aplicativo**.

O FFmpeg deve estar **incluso** no pacote da aplicação ou disponível no PATH do sistema.

---

## ▶ Executando a Aplicação

```bash
python main.py
```

---

## 📂 Estrutura de Pastas

```
YouTube-Audio-Downloader/
│
├── assets/
│   ├── br_icon.png
│   ├── icon.ico
│   ├── icon.png
│   └── us_icon.png
│
├── bin/
│   ├── ffmpeg.exe
│   ├── ffplay.exe
│   └── ffprobe.exe
│
├── config/
│   └── app_config.json
│
├── controller/
│   └── download_controller.py
│
├── core/
│   ├── audio.py
│   ├── downloader.py
│   └── ydl_logger.py
│
├── download_state/
│
├── i18n/
│   ├── en_US.py
│   ├── manager.py
│   └── pt_BR.py
│
├── ui/
│   ├── dialogs/
│   │   └── themed_messagebox.py
│   ├── app_window.py
│   ├── help_window.py
│   ├── playlist_frame.py
│   └── tooltip.py
│
├── utils/
│   ├── app_config.py
│   ├── audio_tags.py
│   ├── helpers.py
│   ├── paths.py
│   ├── sanitize.py
│   └── window.py
│
├── widgets/
│   └── folders.py
│
├── main.py
├── requirements.txt
└── README.md
```

---

## 📜 Licença

Este projeto é **open-source** e licenciado sob a **MIT License**.

Você está livre para usar, modificar e distribuir para **fins pessoais ou educacionais**.

---

## 👤 Autor

**Celmar Pereira de Andrade**

* GitHub: [https://github.com/CelmarPA](https://github.com/CelmarPA)
* Projeto: [https://github.com/CelmarPA/YouTube-Audio-Downloader](https://github.com/CelmarPA/YouTube-Audio-Downloader)
* [LinkedIn](https://www.linkedin.com/in/celmar-pereira-de-andrade/)

---

## 💬 Feedback

Aproveite o aplicativo e sinta-se à vontade para sugerir melhorias ou relatar problemas!
