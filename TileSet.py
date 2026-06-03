import pygame
import os

# 1. KONFIGURASI UKURAN UBIN
TILE_SIZE_ASLI = 16  # Ukuran ubin di dalam file PNG Anda
SKALA_PERBESARAN = 4 # Perbesar gambar 4x lipat agar pas di layar Fullscreen
TILE_SIZE = TILE_SIZE_ASLI * SKALA_PERBESARAN # Hasil akhirnya adalah 64x64 piksel


def load_and_slice_tileset(relative_path, tile_size):
    """
    Memotong spritesheet berbentuk grid (baris & kolom) secara otomatis
    dan langsung memperbesar ukurannya agar proporsional di layar.
    """
    # Mencari posisi absolut folder skrip ini (e:\py\hloges)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Menggabungkan folder skrip dengan jalur relatif aset yang diberikan
    full_path = os.path.join(current_dir, relative_path)

    try:
        sheet = pygame.image.load(full_path).convert_alpha()
        print(f"BERHASIL: Spritesheet ditemukan dan dimuat dari {full_path}")
    except pygame.error:
        print(f"CRITICAL ERROR: File TIDAK ditemukan di: {full_path}")
        print("Menggunakan surface tiruan merah agar game tidak crash.")
        # Cadangan darurat ubin merah jika file hilang
        sheet = pygame.Surface((tile_size * 10, tile_size * 10))
        sheet.fill((200, 0, 0)) 

    sheet_width = sheet.get_width()
    sheet_height = sheet.get_height()
    
    cols = sheet_width // tile_size
    rows = sheet_height // tile_size
    
    tiles_grid = []
    for r in range(rows):
        row_tiles = []
        for c in range(cols):
            rect = pygame.Rect(c * tile_size, r * tile_size, tile_size, tile_size)
            tile_image = sheet.subsurface(rect)
            
            # --- PROSES UPSCALING ---
            scaled_tile = pygame.transform.scale_by(tile_image, SKALA_PERBESARAN)
            
            row_tiles.append(scaled_tile)
        tiles_grid.append(row_tiles)
        
    return tiles_grid

# --- EKSEKUSI PEMOTONGAN ---
# Jalur disesuaikan dengan struktur folder baru Anda yang sudah dirapikan: assets -> Maps -> map.png

PATH_ASET = os.path.join('assets', 'Maps', 'map.png')
all_tiles = load_and_slice_tileset(PATH_ASET, TILE_SIZE_ASLI)

def get_tile_safely(grid, row, col):
    """
    Mengambil ubin hasil potongan secara aman. Jika koordinat baris/kolom 
    melebihi ukuran gambar asli Anda, akan dikembalikan ubin kosong transparan.
    """
    try:
        if 0 <= row < len(grid) and 0 <= col < len(grid[row]):
            return grid[row][col]
    except Exception:
        pass
    blank = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    return blank

# ==============================================================================
# PEMETAAN INDEKS MATRIKS AKURAT BERDASARKAN GAMBAR MAP.PNG (RILLASETS)
# ==============================================================================
MAP_TILES_IMAGE = {
    0:  get_tile_safely(all_tiles, 4, 1),   # Indeks 0 = Lantai Utama / Jalan
    1:  get_tile_safely(all_tiles, 1, 0),   # Indeks 1 = Dinding Menghadap Bawah
    2:  get_tile_safely(all_tiles, 8, 4),   # Indeks 2 = Dinding Menghadap Atas
    3:  get_tile_safely(all_tiles, 10, 3),   # Indeks 3 = Dinding Menghadap Kanan
    4:  get_tile_safely(all_tiles, 10, 2),   # Indeks 4 = Dinding Menghadap Kiri
    5:  get_tile_safely(all_tiles, 11, 3),   # Indeks 5 = Pojok Kiri-Atas
    6:  get_tile_safely(all_tiles, 11, 2),   # Indeks 6 = Pojok Kanan-Atas
    7:  get_tile_safely(all_tiles, 8, 3),   # Indeks 7 = Pojok Kiri-Bawah
    8:  get_tile_safely(all_tiles, 8, 2),   # Indeks 8 = Pojok Kanan-Bawah
    9:  get_tile_safely(all_tiles, 7, 0),   # Indeks 9 = Dinding Tengah (Tepi kanan dan kiri ruangan)
    10: get_tile_safely(all_tiles, 0, 0),   # Indeks 10 = Dinding Tengah / Isi Batu Padat
    11: get_tile_safely(all_tiles, 2, 0),   
    12: get_tile_safely(all_tiles, 8, 0),   # Indeks 12 = Dinding Tengah (ujung bawah/Kanan ruangan) U shape
    13: get_tile_safely(all_tiles, 3, 0),   # Indeks 13 = Dinding Tengah (ujung bawah/Kiri ruangan)
    14: get_tile_safely(all_tiles, 4, 0),   # Indeks 14 = Dinding Tengah (Tepi bawah kiri ruangan)
    15: get_tile_safely(all_tiles, 5, 0),   # Indeks 15 = Dinding Tengah (Tepi bawah kanan ruangan)
    16: get_tile_safely(all_tiles, 7, 1),   # Indeks 16 = dua ruangan siku kiri atas
    17: get_tile_safely(all_tiles, 7, 2),   # Indeks 17 = dua ruangan siku kanan atas
    18: get_tile_safely(all_tiles, 12, 0),
    19: get_tile_safely(all_tiles, 12, 1),
    20: get_tile_safely(all_tiles, 12, 2),
    21: get_tile_safely(all_tiles, 0, 4),
    22: get_tile_safely(all_tiles, 0, 5),
    23: get_tile_safely(all_tiles, 0, 6),
    24: get_tile_safely(all_tiles, 1, 4),
    25: get_tile_safely(all_tiles, 1, 5),
    26: get_tile_safely(all_tiles, 1, 6),
    27: get_tile_safely(all_tiles, 16, 0),
    28: get_tile_safely(all_tiles, 16, 1),
    29: get_tile_safely(all_tiles, 16, 2),
    30: get_tile_safely(all_tiles, 17, 2),
    31: get_tile_safely(all_tiles, 13, 5),
}
# if score == 13:  # Atas(1) + Kiri(4) + Kanan(8) -> Bawah Terbuka
#                 if diag_kanan_atas == 0:
#                     indexed_map[r][c] = 25
#                 elif diag_kiri_atas == 0:
#                     indexed_map[r][c] = 26
#                 else:
#                     indexed_map[r][c] = 1  # Dinding Menghadap Bawah
#             elif score == 14:  # Bawah(2) + Kiri(4) + Kanan(8) -> Atas Terbuka
#                 indexed_map[r][c] = 2  # Dinding Menghadap Atas
#             elif score == 7:  # Atas(1) + Bawah(2) + Kiri(4) -> Kanan Terbuka
#                 indexed_map[r][c] = 3  # Dinding Menghadap Kanan
#             elif score == 11:  # Atas(1) + Bawah(2) + Kanan(8) -> Kiri Terbuka
#                 if (diag_kiri_bawah == 0 and diag_kanan_bawah == 0 and diag_kiri_atas == 0):
#                     indexed_map[r][c] = 16
#                 else:
#                     indexed_map[r][c] = 4  # Dinding Menghadap Kiri

#             # --- 2. POJOK / SUDUT LUAR ---
#             elif score == 10:  # Bawah(2) + Kanan(8)
#                 if tile_bawah == 1 and tile_kanan == 1:
#                     indexed_map[r][c] = 18  # Pojok Kanan-Bawah
#                 else:
#                     indexed_map[r][c] = 1  # Pojok Kiri-Atas
#             elif score == 6:  # Bawah(2) + Kiri(4)
#                 indexed_map[r][c] = 19  # Pojok Kanan-Atas
#             elif score == 9:  # Atas(1) + Kanan(8)
#                 indexed_map[r][c] = 6  # Pojok Kiri-Bawah
#             elif score == 5:  # Atas(1) + Kiri(4)
#                 indexed_map[r][c] = 20  # Pojok Kanan-Bawah

#             # --- 3. LORONG TERJEPIT / PERTEMUAN JALAN ---
#             elif score == 3:  # Atas(1) + Bawah(2) -> Kiri Kanan Terbuka
#                 indexed_map[r][c] = 9
#             elif score == 12:  # Kiri(4) + Kanan(8) -> Atas Bawah Terbuka
#                 indexed_map[r][c] = 1

#             # --- 4. UJUNG PERTEMUAN LORONG / T-JUNCTION ---
#             elif score == 2:
#                 indexed_map[r][c] = 17  
#             elif score == 8:
#                 indexed_map[r][c] = 21
#             elif score == 4:
#                 indexed_map[r][c] = 23
#             elif score == 1:
#                 indexed_map[r][c] = 12

#             # --- 5. DETEKSI DIAGONAL UNTUK POJOKAN SIKU TAJAM ---
#             elif score == 15:
#                 if diag_kanan_bawah == 0:
#                     indexed_map[r][c] = 11  
#                 elif diag_kiri_bawah == 0:
#                     if diag_kiri_atas == 0:
#                         indexed_map[r][c] = 24  
#                     else:
#                         indexed_map[r][c] = 14  
#                 elif diag_kiri_atas == 0:
#                     indexed_map[r][c] = 15
#                 elif diag_kanan_atas == 0:
#                     indexed_map[r][c] = 13
#                 else:
#                     indexed_map[r][c] = 10  # Void Padat
#             elif score == 14:
#                 if (diag_kanan_bawah == 0 and diag_kiri_bawah == 0 and diag_kiri_atas == 0 and diag_kanan_atas == 0):
#                     indexed_map[r][c] = 12
#             elif score == 0:
#                 indexed_map[r][c] = 1  
#             else:
#                 indexed_map[r][c] = 10
