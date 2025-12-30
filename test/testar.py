from core.audio import Audio
import os

def test_normalize_mp3():
    input_file = "test.mp3"
    output_file = "test.normalized.mp3"

    if not os.path.exists(input_file):
        print(f"Arquivo não encontrado: {input_file}")
        return

    print("Normalizando áudio...")

    try:
        Audio(input_file).normalize(
            output_path=output_file,
            target_lufs=-14.0
        )
        print(f"Normalização concluída: {output_file}")

    except Exception as e:
        print(f"Erro ao normalizar: {e}")