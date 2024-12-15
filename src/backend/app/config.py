import os
import sqlite3

# Direktori dan lokasi database
BASE_DIR = os.path.dirname(__file__)
ALBUM_IMAGES_DIR = os.path.join(BASE_DIR, 'album_images')
MUSIC_AUDIOS_DIR = os.path.join(BASE_DIR, 'music_audios')
DATABASE_PATH = os.path.join(BASE_DIR, 'testing2.db')

# Pastikan direktori untuk file gambar dan audio ada
os.makedirs(ALBUM_IMAGES_DIR, exist_ok=True)
os.makedirs(MUSIC_AUDIOS_DIR, exist_ok=True)

# Buat koneksi ke database
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# Membuat tabel album_images
cursor.execute("""
CREATE TABLE IF NOT EXISTS album_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    path TEXT NOT NULL
)
""")

# Membuat tabel music_audios
cursor.execute("""
CREATE TABLE IF NOT EXISTS music_audios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    path TEXT NOT NULL
)
""")

# Contoh fungsi untuk memasukkan data awal (opsional)
def insert_sample_data():
    # Contoh data untuk album_images
    if not cursor.execute("SELECT COUNT(*) FROM album_images").fetchone()[0]:
        cursor.execute("INSERT INTO album_images (name, path) VALUES (?, ?)", 
                       ("example.jpg", os.path.join(ALBUM_IMAGES_DIR, "example.jpg")))
    
    # Contoh data untuk music_audios
    if not cursor.execute("SELECT COUNT(*) FROM music_audios").fetchone()[0]:
        cursor.execute("INSERT INTO music_audios (name, path) VALUES (?, ?)", 
                       ("example.mid", os.path.join(MUSIC_AUDIOS_DIR, "example.mid")))

# Panggil fungsi untuk memasukkan data awal
insert_sample_data()

# Commit perubahan dan tutup koneksi
conn.commit()
conn.close()

print(f"Database initialized at {DATABASE_PATH}")
