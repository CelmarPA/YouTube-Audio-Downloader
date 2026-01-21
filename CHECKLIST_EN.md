# ✅ Test Checklist – YouTube Audio Downloader

## 1. Interface & UX
- [✔️] Launch the application without errors (`python main.py`)  
- [✔️] Verify that the icon and theme are loaded correctly  
- [✔️] Test language switching (pt-BR / en-US) and restart the application  
- [✔️] Check window responsiveness (resizing where applicable)  
- [✔️] Test tooltips for all buttons and fields  

## 2. Audio Download
- [✔️] Paste a **single video URL** and download audio (MP3 format)  
- [✔️] Paste a video URL with another supported format (e.g., M4A)  
- [✔️] Verify that the downloaded file is playable  
- [✔️] Check that the file name is **sanitized correctly**  

## 3. “Keep Original” Option
- [✔️] Enable “Keep Original” and download video + audio  
- [✔️] Test video resolution selection (Auto / 720p / 1080p, etc.)  
- [✔️] Disable “Keep Original” and verify only audio is downloaded  

## 4. Playlist
- [✔️] Paste a playlist URL and open selection modal  
- [✔️] Select/deselect videos manually  
- [✔️] Verify “Select All” button  
- [✔️] Verify “Deselect All” button  
- [✔️] Confirm selection and download only selected videos  

## 5. Audio Normalization
- [✔️] Verify that downloaded files without normalization remain without the tag  
- [✔️] Download audio with normalization enabled  
- [✔️] Check if the X-NORMALIZED tag is present  
- [✔️] Verify that the audio LUFS is within the target (-14 ± 1)  

## 6. Folders & Files
- [✔️] Change download folder and verify files are saved in the correct location  
- [✔️] Open download folder using the integrated button (`open_download_folder`)  
- [✔️] Test behavior with duplicate file names  

## 7. Errors & Limitations
- [✔️] Paste an invalid URL and verify error message  
- [✔️] Paste a private/restricted video and check warning  
- [✔️] Disconnect from the internet and attempt download, check error handling  
- [✔️] Test download of a very long video and verify stability  

## 8. FFmpeg Integration
- [✔️] Verify that FFmpeg is detected correctly  
- [✔️] Test audio normalization command (loudnorm)  
- [✔️] Test audio format conversion (MP3, M4A)  

## 9. Performance & Stability
- [✔️] Download multiple videos simultaneously and verify stability  
- [✔️] Pause/resume downloads (if available)  
- [✔️] Cancel a download mid-process and verify cleanup of incomplete files  
