from basic_pitch.inference import predict_and_save, ICASSP_2022_MODEL_PATH
import os
import glob

# Fungsi untuk mengonversi semua file WAV dalam folder ke MIDI
def batch_wav_to_midi(input_directory, output_directory, model_path=ICASSP_2022_MODEL_PATH):
    """
    Mengonversi semua file WAV dalam folder ke MIDI menggunakan Basic Pitch.

    Args:
        input_directory (str): Path ke folder yang berisi file WAV.
        output_directory (str): Path ke direktori output untuk menyimpan file MIDI.
        model_path (str): Path ke model yang digunakan untuk prediksi.

    Returns:
        None
    """
    # Pastikan direktori output ada
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Cari semua file WAV di folder input
    wav_files = glob.glob(os.path.join(input_directory, "*.wav"))

    if not wav_files:
        print("Tidak ada file WAV yang ditemukan di folder:", input_directory)
        return

    print(f"Ditemukan {len(wav_files)} file WAV. Memulai konversi...")

    # Proses setiap file WAV
    for wav_file_path in wav_files:
        print(f"Memproses file: {wav_file_path}")
        try:
            # Gunakan fungsi Basic Pitch untuk mengonversi dan menyimpan hasilnya
            predict_and_save(
                audio_path_list=[wav_file_path],
                output_directory=output_directory,
                save_midi=True,
                sonify_midi=False,
                save_model_outputs=False,
                save_notes=False,
                model_or_model_path=model_path,
            )
            print(f"Berhasil dikonversi: {wav_file_path}")
        except Exception as e:
            print(f"Gagal memproses file {wav_file_path}. Error: {e}")

    print(f"Semua file WAV selesai dikonversi. File MIDI disimpan di: {output_directory}")


# Contoh penggunaan
if __name__ == "__main__":
    # Folder input yang berisi file WAV
    input_dir = "sounds"  # Ganti dengan folder tempat file WAV Anda
    
    # Folder output untuk menyimpan file MIDI
    output_dir = "output_midi"

    # Panggil fungsi untuk memproses semua file WAV
    batch_wav_to_midi(input_dir, output_dir)
