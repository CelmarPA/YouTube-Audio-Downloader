; =========================================
; YouTube Audio Downloader Installer
; =========================================

[Setup]
AppName=YouTube Audio Downloader
AppVersion=1.0
AppPublisher=Pereira A.C.
DefaultDirName={pf}\YouTube Audio Downloader
DefaultGroupName=YouTube Audio Downloader
UninstallDisplayName=YouTube Audio Downloader
UninstallDisplayIcon={app}\YouTubeAudioDownloader.exe
OutputBaseFilename=YouTubeAudioDownloaderSetup
SetupIconFile=assets\icon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=none

; =========================================
; Files
; =========================================

[Files]
; Executável principal
Source: "dist\YouTubeAudioDownloader.exe"; DestDir: "{app}"; Flags: ignoreversion

; Pastas do projeto
Source: "bin\*"; DestDir: "{app}\bin"; Flags: recursesubdirs
Source: "assets\*"; DestDir: "{app}\assets"; Flags: recursesubdirs
Source: "config\*"; DestDir: "{app}\config"; Flags: recursesubdirs
Source: "i18n\*"; DestDir: "{app}\i18n"; Flags: recursesubdirs
Source: "venv\*"; DestDir: "{app}\venv"; Flags: recursesubdirs

; =========================================
; Icons
; =========================================

[Icons]
Name: "{group}\YouTube Audio Downloader"; Filename: "{app}\YouTubeAudioDownloader.exe"
Name: "{commondesktop}\YouTube Audio Downloader"; Filename: "{app}\YouTubeAudioDownloader.exe"

; =========================================
; Run after install
; =========================================

[Run]
Filename: "{app}\YouTubeAudioDownloader.exe"; Description: "Launch YouTube Audio Downloader"; Flags: nowait postinstall skipifsilent

; =========================================
; Uninstall cleanup
; =========================================

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
Type: filesandordirs; Name: "{userappdata}\YouTube Audio Downloader"
Type: filesandordirs; Name: "{localappdata}\YouTube Audio Downloader"
