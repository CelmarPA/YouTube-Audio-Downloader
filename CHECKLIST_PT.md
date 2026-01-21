<!-- markdownlint-disable -->
# ✅ Checklist de Testes – YouTube Audio Downloader

## 1. Interface e UX
- [✔️] Abrir a aplicação sem erros (`python main.py`)  
- [✔️] Verificar que o ícone e tema são carregados corretamente  
- [✔️] Testar mudança de idioma (pt-BR / en-US) e reiniciar a aplicação  
- [✔️] Verificar a responsividade das janelas (redimensionamento quando aplicável)  
- [✔️] Testar tooltips de todos os botões e campos  

## 2. Download de Áudio
- [✔️] Inserir URL de **vídeo único** e baixar áudio (formato MP3)  
- [✔️] Inserir URL de vídeo com outro formato suportado (ex: M4A)  
- [✔️] Verificar que o arquivo baixado é reproduzível  
- [✔️] Conferir se o nome do arquivo foi **sanitizado corretamente**  

## 3. Opção “Manter Original”
- [✔️] Habilitar “Keep Original” e baixar vídeo + áudio  
- [✔️] Testar seleção de resolução de vídeo (Auto / 720p / 1080p, etc.)  
- [✔️] Desabilitar “Keep Original” e verificar que apenas áudio é baixado  

## 4. Playlist
- [✔️] Inserir URL de playlist e abrir modal de seleção  
- [✔️] Selecionar/deselecionar vídeos manualmente  
- [✔️] Verificar botão “Selecionar Todos”  
- [✔️] Verificar botão “Deselecionar Todos”  
- [✔️] Confirmar seleção e iniciar download apenas dos vídeos marcados  

## 5. Normalização de Áudio
- [✔️] Verificar se arquivos baixados sem normalização permanecem sem tag  
- [✔️] Baixar áudio com normalização habilitada  
- [✔️] Conferir se tag `X-NORMALIZED` está presente  
- [✔️] Verificar se o LUFS do áudio está dentro do alvo (-14 ± 1)  

## 6. Pastas e Arquivos
- [✔️] Alterar pasta de download e verificar se os arquivos vão para o local correto  
- [✔️] Abrir pasta de download pelo botão integrado (`open_download_folder`)  
- [✔️] Testar comportamento com nomes de arquivos duplicados  

## 7. Erros e Limitações
- [✔️] Inserir URL inválida e verificar mensagem de erro  
- [✔️] Inserir vídeo privado ou restrito e verificar aviso  
- [✔️] Desconectar internet e tentar baixar, verificar tratamento de erro  
- [✔️] Testar download de vídeo muito longo e verificar estabilidade  

## 8. Integração com FFmpeg
- [✔️] Conferir que FFmpeg é detectado corretamente  
- [✔️] Testar comando de normalização de áudio (loudnorm)  
- [✔️] Testar conversão de formatos de áudio (MP3, M4A)  

## 9. Performance e Estabilidade
- [✔️] Baixar múltiplos vídeos simultaneamente e verificar estabilidade  
- [✔️] Pausar/resumir downloads (se funcionalidade disponível)  
- [✔️] Cancelar download no meio do processo e verificar limpeza de arquivos incompletos  
