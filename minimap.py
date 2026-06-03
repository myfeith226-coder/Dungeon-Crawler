import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from TileSet import MAP_TILES_IMAGE, TILE_SIZE
def draw_minimap(screen, dungeon_map, player):
    # 1. Tentukan ukuran satu ubin kecil di minimap (dalam pixel)
    MINI_TILE = 3  # 1 ubin map digambar sebesar 3x3 pixel di layar
    
    # 2. Tentukan posisi kotak minimap di layar game (Pojok Kanan Atas)
    # Sesuaikan SCREEN_WIDTH dengan resolusi window game kamu
    MINIMAP_X = SCREEN_WIDTH - (len(dungeon_map[0]) * MINI_TILE) - 20
    MINIMAP_Y = 20
    
    # 3. Gambar Background/Bingkai Minimap (Hitam Transparan)
    lebar_m = len(dungeon_map[0]) * MINI_TILE
    tinggi_m = len(dungeon_map) * MINI_TILE
    
    # Membuat efek transparan (alpha) pada background minimap
    bg_surface = pygame.Surface((lebar_m, tinggi_m), pygame.SRCALPHA)
    bg_surface.fill((0, 0, 0, 150)) # Warna hitam dengan transparansi 150
    screen.blit(bg_surface, (MINIMAP_X, MINIMAP_Y))
    
    # 4. Loop seluruh isi peta untuk menggambar Dinding & Jalan
    for row_idx, row in enumerate(dungeon_map):
        for col_idx, tile in enumerate(row):
            # Hitung koordinat gambar pixel di atas layar minimap
            mx = MINIMAP_X + (col_idx * MINI_TILE)
            my = MINIMAP_Y + (row_idx * MINI_TILE)
            
            if tile == 0:
                # Warna Abu-abu terang untuk Lantai/Jalan Koridor
                pygame.draw.rect(screen, (80, 80, 80), (mx, my, MINI_TILE, MINI_TILE))
            elif tile != 0:
                # Warna Hitam/Dinding Padat
                pygame.draw.rect(screen, (20, 20, 20), (mx, my, MINI_TILE, MINI_TILE))

    # 5. GAMBAR POSISI KSATRIA (Titik Merah Berkedip)
    # Konversi koordinat pixel dunia asli ksatria menjadi koordinat koordinat minimap
    # TILE_SIZE adalah ukuran ubin asli game kamu (misal 16, 32, atau 64)
    p_grid_x = player.rect.centerx // TILE_SIZE
    p_grid_y = player.rect.centery // TILE_SIZE
    
    pmx = MINIMAP_X + (p_grid_x * MINI_TILE)
    pmy = MINIMAP_Y + (p_grid_y * MINI_TILE)

    # Gambar titik merah ksatria (sedikit diperbesar biar kelihatan jelas)
    pygame.draw.rect(screen, (255, 0, 0), (pmx, pmy, MINI_TILE + 1, MINI_TILE + 1))
    
    # 6. Gambar Garis Bingkai Pembatas Minimap biar makin Estetik
    pygame.draw.rect(screen, (255, 255, 255), (MINIMAP_X - 1, MINIMAP_Y - 1, lebar_m + 2, tinggi_m + 2), 1)