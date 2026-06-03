import pygame
import sys
import math
import random
from config import *
from TileSet import MAP_TILES_IMAGE, TILE_SIZE
from UI import MainMenu, PauseMenu, HUD
# 1. KONFIGURASI UTAMA
TILE_SIZE = 64
FPS = 60
MAP_COLS = 100
MAP_ROWS = 100

tangga_sudah_muncul = False
id_ubin_tangga = 31 
from minimap import *
# 2. ALGORITMA ROOM & CORRIDOR
class Room:
    def __init__(self, x, y, w, h):
        self.x1, self.y1 = x, y
        self.x2, self.y2 = x + w, y + h
        self.center_x = int((self.x1 + self.x2) / 2)
        self.center_y = int((self.y1 + self.y2) / 2)

    def intersects(self, other):
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )


def generate_dungeon_with_corridors(cols, rows, max_rooms=14):
    dungeon = [[1 for _ in range(cols)] for _ in range(rows)]
    rooms = []
    for _ in range(max_rooms):
        w, h = random.randint(6, 12), random.randint(6, 12)
        x, y = random.randint(1, cols - w - 2), random.randint(1, rows - h - 2)
        new_room = Room(x, y, w, h)
        failed = any(new_room.intersects(other) for other in rooms)
        if not failed:
            for r in range(new_room.y1, new_room.y2):
                for c in range(new_room.x1, new_room.x2):
                    dungeon[r][c] = 0
            if len(rooms) > 0:
                prev_x, prev_y = rooms[-1].center_x, rooms[-1].center_y
                if random.randint(0, 1) == 1:
                    create_h_corridor(dungeon, prev_x, new_room.center_x, prev_y)
                    create_v_corridor(
                        dungeon, prev_y, new_room.center_y, new_room.center_x
                    )
                else:
                    create_v_corridor(dungeon, prev_y, new_room.center_y, prev_x)
                    create_h_corridor(
                        dungeon, prev_x, new_room.center_x, new_room.center_y
                    )
            rooms.append(new_room)
    return dungeon, rooms[0].center_x, rooms[0].center_y, rooms


def create_h_corridor(dungeon, x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        dungeon[y][x] = 0
        dungeon[y + 1][x] = 0


def create_v_corridor(dungeon, y1, y2, x):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        dungeon[y][x] = 0
        dungeon[y][x + 1] = 0


def index_dungeon_map(raw_map, cols, rows):
    """
    Versi Final: Bitmasking berbasis TEMBOK (1) dengan perbaikan
    kombinasi skor untuk sudut pertemuan ruangan, lorong, dan sudut tajam 8-arah.
    """
    indexed_map = [[0 for _ in range(cols)] for _ in range(rows)]

    for r in range(rows):
        for c in range(cols):
            if raw_map[r][c] == 0:
                indexed_map[r][c] = 0  # Tetap Lantai Utama / Jalan
                continue

            # Cek tetangga 4-arah utama (0 = lantai, 1 = tembok).
            tile_atas = raw_map[r - 1][c] if r > 0 else 1
            tile_bawah = raw_map[r + 1][c] if r < rows - 1 else 1
            tile_kiri = raw_map[r][c - 1] if c > 0 else 1
            tile_kanan = raw_map[r][c + 1] if c < cols - 1 else 1

            # Ambil data 4-arah diagonal (PENTING UNTUK POJOKAN TAJAM SIKU LUAR)
            diag_kanan_bawah = (
                raw_map[r + 1][c + 1] if (r < rows - 1 and c < cols - 1) else 1
            )
            diag_kiri_bawah = raw_map[r + 1][c - 1] if (r < rows - 1 and c > 0) else 1
            diag_kanan_atas = raw_map[r - 1][c + 1] if (r > 0 and c < cols - 1) else 1
            diag_kiri_atas = raw_map[r - 1][c - 1] if (r > 0 and c > 0) else 1

            # Hitung skor bitmask berbasis TEMBOK (Atas=1, Bawah=2, Kiri=4, Kanan=8)
            score = 0
            if tile_atas == 1:
                score += 1
            if tile_bawah == 1:
                score += 2
            if tile_kiri == 1:
                score += 4
            if tile_kanan == 1:
                score += 8

            # =================================================================
            # EVALUASI INDEKS BERDASARKAN SKOR KOMBINASI TEMBOK
            # =================================================================

            # --- 1. SISI WALL LURUS (3 Sisi Tembok, 1 Sisi Terbuka ke Lantai) ---
            if score == 13:  # Atas(1) + Kiri(4) + Kanan(8) -> Bawah Terbuka
                if diag_kanan_atas == 0:
                    indexed_map[r][c] = 25
                elif diag_kiri_atas == 0:
                    indexed_map[r][c] = 26
                else:
                    indexed_map[r][c] = 1  # Dinding Menghadap Bawah
            elif score == 14:  # Bawah(2) + Kiri(4) + Kanan(8) -> Atas Terbuka
                indexed_map[r][c] = 2  # Dinding Menghadap Atas
            elif score == 7:  # Atas(1) + Bawah(2) + Kiri(4) -> Kanan Terbuka
                indexed_map[r][c] = 3  # Dinding Menghadap Kanan
            elif score == 11:  # Atas(1) + Bawah(2) + Kanan(8) -> Kiri Terbuka
                if (
                    diag_kiri_bawah == 0
                    and diag_kanan_bawah == 0
                    and diag_kiri_atas == 0
                ):
                    indexed_map[r][c] = 16
                else:
                    indexed_map[r][c] = 4  # Dinding Menghadap Kiri

            # --- 2. POJOK / SUDUT LUAR (2 Sisi Tembok Bersebelahan) ---
            elif score == 10:  # Bawah(2) + Kanan(8)
                if tile_bawah == 1 and tile_kanan == 1:
                    indexed_map[r][c] = 18  # Pojok Kanan-Bawah
                else:
                    indexed_map[r][c] = 1  # Pojok Kiri-Atas
            elif score == 6:  # Bawah(2) + Kiri(4)
                indexed_map[r][c] = 19  # Pojok Kanan-Atas
            elif score == 9:  # Atas(1) + Kanan(8)
                indexed_map[r][c] = 6  # Pojok Kiri-Bawah
            elif score == 5:  # Atas(1) + Kiri(4)
                indexed_map[r][c] = 20  # Pojok Kanan-Bawah

            # --- 3. LORONG TERJEPIT / PERTEMUAN JALAN (2 Sisi Tembok Berhadapan) ---
            elif (
                score == 3
            ):  # Atas(1) + Bawah(2) -> Kiri Kanan Terbuka (Penyekat Vertikal)
                indexed_map[r][c] = 9
            elif (
                score == 12
            ):  # Kiri(4) + Kanan(8) -> Atas Bawah Terbuka (Penyekat Horizontal)
                indexed_map[r][c] = 1

            # --- 4. UJUNG PERTEMUAN LORONG / T-JUNCTION (Hanya 1 Sisi Tembok) ---
            elif score == 2:  # Hanya Bawah Tembok, sisa sisi adalah Lantai
                indexed_map[r][c] = 17  # Sambungan Ujung Bawah / Kanan Ruangan
            elif score == 8:  # Hanya Kanan Tembok
                indexed_map[r][c] = 21
            elif score == 4:  # Hanya Kiri Tembok
                indexed_map[r][c] = 23
            elif score == 1:  # Hanya Atas Tembok
                indexed_map[r][c] = 12

            # --- 5. DETEKSI DIAGONAL UNTUK POJOKAN SIKU TAJAM (Score == 15 / Full Tembok Utama) ---
            elif score == 15:
                # Siku Kanan-Atas (Kasus ujung tembok di sebelah kanan karakter biru)
                if diag_kanan_bawah == 0:
                    indexed_map[r][
                        c
                    ] = 11  # Menyesuaikan indeks pojokan kanan-atas punyamu
                # Siku Kiri-Atas
                elif diag_kiri_bawah == 0:
                    if diag_kiri_atas == 0:
                        indexed_map[r][
                            c
                        ] = 24  # Menyesuaikan indeks pojokan kiri-atas punyamu
                    else:
                        indexed_map[r][
                            c
                        ] = 14  # Menyesuaikan indeks pojokan kiri-atas punyamu
                # Siku Kanan-Bawah
                elif diag_kiri_atas == 0:
                    indexed_map[r][c] = 15
                # Siku Kiri-Bawah
                elif diag_kanan_atas == 0:
                    indexed_map[r][c] = 13
                else:
                    indexed_map[r][
                        c
                    ] = 10  # Benar-benar Dinding Solid Tengah / Void Padat
            elif score == 14:
                if (
                    diag_kanan_bawah == 0
                    and diag_kiri_bawah == 0
                    and diag_kiri_atas == 0
                    and diag_kanan_atas == 0
                ):
                    indexed_map[r][c] = 12
            elif score == 0:
                indexed_map[r][c] = 1  # Lantai Utama / Jalan
            # --- 6. DEFAULT VOID / DINDING SOLID DALAM ---
            else:
                indexed_map[r][c] = 10

    return indexed_map


# Generate peta mentah lalu konversi ke peta berindeks
RAW_MAP, START_GRID_X, START_GRID_Y, daftar_ruangan = generate_dungeon_with_corridors(
    MAP_COLS, MAP_ROWS
)
DUNGEON_MAP = index_dungeon_map(RAW_MAP, MAP_COLS, MAP_ROWS)

# 3. KELAS ENTITAS (PLAYER & BULLET)
from character import *

# 4. INITIALIZATION
clock = pygame.time.Clock()
stage = 2
SPAWN_X = START_GRID_X * TILE_SIZE
SPAWN_Y = START_GRID_Y * TILE_SIZE
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

path_menu_bgm = os.path.join(
    BASE_DIR,
    "assets",
    "Audio",
    "main_menu.ogg"
)

path_bgm = os.path.join(
    BASE_DIR,
    "assets",
    "Audio",
    "gameplay.ogg"
)

pygame.mixer.music.load(path_bgm)
pygame.mixer.music.set_volume(0.5)

# player = Player(START_GRID_X, START_GRID_Y)
ksatria = Player(SPAWN_X, SPAWN_Y)
# daftar_musuh = []
# daftar_proyektil = []
# daftar_chest = []

# ruangan_musuh_biasa = daftar_ruangan[1:-1]


# print(path_senjata)
path_musuh = os.path.join(BASE_DIR, "assets", "Enemy1", "noBKG_KnightRun_strip.png")
path_boss = os.path.join(BASE_DIR, "assets", "Boss")
path_boss2 = os.path.join(BASE_DIR, "assets", "Boss2")
path_boss3 = os.path.join(BASE_DIR, "assets", "Boss3")
senjata = Senjata(3)
# musuh = Musuh(500, 400, "assets/Enemy1/noBKG_KnightRun_strip.png", 8)
# for room in ruangan_musuh_biasa:
#     jumlah_musuh = random.randint(1, 3)
#     for _ in range(jumlah_musuh):
#         grid_x = random.randint(room.x1 + 2, room.x2 - 3)
#         grid_y = random.randint(room.y1 + 2, room.y2 - 3)
#         musuh_biasa = Musuh(grid_x * TILE_SIZE, grid_y * TILE_SIZE, path_musuh, 8)
#         musuh_biasa.apakah_boss = False
        
#         # Masukkan ke list pakai append manual
#         daftar_musuh.append(musuh_biasa)
#     spawn_peti = random.choice([True, False]) # Peluang 50/50
#     if spawn_peti:
#         chest_x = random.randint(room.x1 + 2, room.x2 - 3) * TILE_SIZE
#         chest_y = random.randint(room.y1 + 2, room.y2 - 3) * TILE_SIZE
#         print(f"Successfully spawned a chest at Grid X: {chest_x//TILE_SIZE}, Y: {chest_y//TILE_SIZE}")
        
#         # SANGAT RINGKAS: Cukup panggil kelasnya, dia otomatis mengurus gambarnya sendiri!
#         peti_baru = Chest(chest_x, chest_y) # Samakan skalanya dengan musuh/player
#         daftar_chest.append(peti_baru) 

# walls = []
# for row_idx, row in enumerate(DUNGEON_MAP):
#     for col_idx, tile in enumerate(row):
#         if tile != 0:
#             walls.append(
#                 pygame.Rect(
#                     col_idx * TILE_SIZE, row_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE
#                 )  
#             )
            
# ruangan_boss = daftar_ruangan[-1]
# boss_pixel_x = ruangan_boss.center_x * TILE_SIZE
# boss_pixel_y = ruangan_boss.center_y * TILE_SIZE
# boss_spawn = False

def buat_level_baru():
    global DUNGEON_MAP, daftar_ruangan, daftar_musuh, walls, boss_spawn, ksatria, tangga_sudah_muncul, daftar_proyektil, stage, boss_pixel_x, boss_pixel_y,daftar_chest,ruangan_boss
    DUNGEON_MAP = []
    daftar_chest = []
    # 1. Generate ulang peta baru (sesuaikan dengan nama fungsi generator Anda)
    RAW_MAP, START_GRID_X, START_GRID_Y, daftar_ruangan = generate_dungeon_with_corridors(
        MAP_COLS, MAP_ROWS
    )
    DUNGEON_MAP = index_dungeon_map(RAW_MAP, MAP_COLS, MAP_ROWS)
    
    # 2. Kosongkan total list lama agar data level sebelumnya hilang
    daftar_musuh = []
    walls = []
    daftar_proyektil = []
    boss_spawn = False
    tangga_sudah_muncul = False
    ruangan_boss = daftar_ruangan[-1]
    boss_pixel_x = ruangan_boss.center_x * TILE_SIZE
    boss_pixel_y = ruangan_boss.center_y * TILE_SIZE
    # 3. Jalankan ulang logika spawn kroco berdasarkan ruangan baru
    ruangan_musuh_biasa = daftar_ruangan[1:-1]
    for room in ruangan_musuh_biasa:
        jumlah_musuh = random.randint(1, 3)
        for _ in range(jumlah_musuh):
            grid_x = random.randint(room.x1 + 2, room.x2 - 3)
            grid_y = random.randint(room.y1 + 2, room.y2 - 3)
            musuh_biasa = Musuh(grid_x * TILE_SIZE, grid_y * TILE_SIZE, path_musuh, 8)
            musuh_biasa.apakah_boss = False
            daftar_musuh.append(musuh_biasa)
            
        spawn_peti = random.choice([True, False]) # Peluang 50/50
        if spawn_peti:
                chest_x = random.randint(room.x1 + 2, room.x2 - 3) * TILE_SIZE
                chest_y = random.randint(room.y1 + 2, room.y2 - 3) * TILE_SIZE
                print(f"Successfully spawned a chest at Grid X: {chest_x//TILE_SIZE}, Y: {chest_y//TILE_SIZE}")
                
                # SANGAT RINGKAS: Cukup panggil kelasnya, dia otomatis mengurus gambarnya sendiri!
                peti_baru = Chest(chest_x, chest_y) # Samakan skalanya dengan musuh/player
                daftar_chest.append(peti_baru) 
    # 4. Ambil data dinding baru dari peta yang baru di-generate
    for row_idx, row in enumerate(DUNGEON_MAP):
        for col_idx, tile in enumerate(row):
            if tile != 0:
                walls.append(pygame.Rect(col_idx * TILE_SIZE, row_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                
    # 5. Pindahkan posisi ksatria ke titik awal ruangan pertama (Room 0)
    ruangan_awal = daftar_ruangan[0]
    ksatria.rect.x = ruangan_awal.center_x * TILE_SIZE
    ksatria.rect.y = ruangan_awal.center_y * TILE_SIZE

main_menu = MainMenu()

game_state = "menu"
pygame.mixer.music.load(path_menu_bgm)
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

fade_alpha = 0
pause_menu = PauseMenu()
hud = HUD()
loading_image = pygame.image.load(
    os.path.join(
        BASE_DIR,
        "assets",
        "UI",
        "loading.png"
    )
).convert()

loading_image = pygame.transform.scale(
    loading_image,
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)

loading_timer = 0

# 5. MAIN LOOP
while True:
    clock.tick(FPS) 
    
    # Perbarui koordinat kamera hanya saat sedang aktif bermain
    if game_state == "playing" and not pause_menu.active:
        camera_x = ksatria.rect.centerx - SCREEN_WIDTH // 2
        camera_y = ksatria.rect.centery - SCREEN_HEIGHT // 2
        
    # ========================================================
    # 1. EVENT HANDLING LOOP (HANYA UNTUK TOMBOL UTAMA SEKALI KLIK)
    # ========================================================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        # --- LOGIKA EVENT SAAT BERADA DI MAIN MENU ---
        if game_state == "menu":
            result = main_menu.handle_event(event)
            if result == "play":


                game_state = "loading"
                fade_alpha = 0
                loading_timer = 0
                pygame.mixer.music.stop()  # Hentikan musik menu saat mulai bermain
                pygame.mixer.music.load(path_bgm)  # Muat musik gameplay
                pygame.mixer.music.play(-1)  # Mulai musik latar secara loop

                ksatria.hp = 100
                ksatria.hidup = True # Reset HP saat mulai level baru
                buat_level_baru()  # Panggil fungsi untuk membuat level baru saat mulai bermain
            elif result == "options":
                print("OPTIONS")
            elif result == "exit":
                pygame.quit()
                sys.exit()
                
        # --- LOGIKA EVENT SAAT BERADA DI DALAM GAMEPLAY ---
        elif game_state == "playing":
            if pause_menu.active:
                result = pause_menu.handle_event(event)
                if result == "play":
                    pause_menu.toggle()
                elif result == "options":
                    print("OPTIONS")
                elif result == "exit":
                    pygame.mixer.music.stop()  # Hentikan musik saat keluar ke menu utama
                    pygame.mixer.music.load(path_menu_bgm)  # Muat ulang musik menu
                    pygame.mixer.music.play(-1)  # Mulai musik menu secara loop

                    game_state = "menu"
                    pause_menu.toggle()
            
            # Deteksi Tombol Sekali Tekan (Bisa diakses baik saat main maupun pause)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause_menu.toggle()       
                # SEKARANG BENAR: Senjata bisa diganti langsung saat bermain (tidak terkunci di menu pause)
                elif event.key == pygame.K_1: senjata.ganti_senjata(0)
                elif event.key == pygame.K_2: senjata.ganti_senjata(1)
                elif event.key == pygame.K_3: senjata.ganti_senjata(2)
                elif event.key == pygame.K_4: senjata.ganti_senjata(3)
                elif event.key == pygame.K_5: senjata.ganti_senjata(4)

    # ========================================================
    # 2. SEPARATOR STATE: MENU & LOADING SCREEN (MENGGUNAKAN CONTINUE)
    # ========================================================
    if game_state == "menu":
        main_menu.draw(screen)
        pygame.display.flip()
        continue   

    if game_state == "loading":
        screen.blit(loading_image, (0, 0))
        loading_timer += 1
        if loading_timer >= 120:
            game_state = "playing" # Pindah ke gameplay setelah loading selesai
        pygame.display.flip()
        continue

    # ========================================================
    # 3. LOGIKA UPDATE GAMEPLAY (HANYA JALAN JIKA GAME TIDAK DI-PAUSE)
    # ========================================================
    if game_state == "playing" and not pause_menu.active:
        keys = pygame.key.get_pressed()
    
        # Logika Penggunaan Potion dari Tas Inventory
        if keys[pygame.K_h]: 
            if len(ksatria.inventory) > 0:
                potion_dipakai = ksatria.inventory.pop() 
                potion_dipakai.gunakan(ksatria)
            else:
                print("Inventory Anda kosong! Tidak ada potion untuk digunakan.")
                
        # Perbarui Logika Posisi Entitas & Senjata
        ksatria.update(walls)
        senjata.update(ksatria, daftar_proyektil)
        
        for musuh in daftar_musuh:
            if musuh.hidup:
                musuh.update(ksatria, walls)
                
        # Perbarui Logika Proyektil Terbang & Hapus Jika Luar Batas
        for p in daftar_proyektil[:]:
            p.update()
            render_p_x = p.rect.x - camera_x
            if render_p_x > SCREEN_WIDTH + 100 or render_p_x < -100:
                if p in daftar_proyektil:
                    daftar_proyektil.remove(p)

        # --------------------------------------------------------
        # DETEKSI COLLISION TABRAKAN & DAMAGE SYSTEM
        # --------------------------------------------------------
        # A. Ksatria Tertabrak Musuh Kroco
        for musuh in daftar_musuh:
            if musuh.hidup and not musuh.apakah_boss:
                if ksatria.rect.colliderect(musuh.hitbox):
                    ksatria.terkena_pukul(10, musuh.rect)

        # B. Senjata Melee Player Menyerang Musuh atau Peti
        if senjata.menyerang and not senjata.sudah_kena and senjata.tipe_serangan != "ranged":
            for musuh in daftar_musuh:
                if musuh.hidup and senjata.rect.colliderect(musuh.hitbox):
                    musuh.terkena_pukul(senjata.damage)
                    senjata.sudah_kena = True
                    break 
            for chest in daftar_chest:
                if not chest.sudah_terbuka and senjata.rect.colliderect(chest.hitbox):
                    chest.terkena_pukul(ksatria) 
                    senjata.sudah_kena = True
                    break

        # C. Proyektil Player Menyerang Musuh atau Peti
        for p in daftar_proyektil[:]:
            peluru_hancur = False
            for musuh in daftar_musuh:
                if musuh.hidup and p.rect.colliderect(musuh.hitbox):
                    musuh.terkena_pukul(p.damage)
                    peluru_hancur = True
                    break
            for chest in daftar_chest:
                if not chest.sudah_terbuka and p.rect.colliderect(chest.hitbox):
                    chest.terkena_pukul(ksatria) 
                    peluru_hancur = True
                    break
            if peluru_hancur:
                if p in daftar_proyektil:
                    daftar_proyektil.remove(p)

        # D. Serangan Spesifik dari Boss ke Ksatria
        if boss_spawn and boss.hidup:
            if stage == 1 and boss.status == "attack" and ksatria.rect.colliderect(boss.hitbox):
                ksatria.terkena_pukul(15, boss.rect)
            elif stage == 2 and boss.status == "attack" and ksatria.rect.colliderect(boss.hitbox):
                ksatria.terkena_pukul(20, boss.rect) 
            elif stage == 3 and boss.status == "attack":
                if 2 <= boss.frame_index <= 5:
                    if ksatria.rect.colliderect(boss.hitbox):
                        ksatria.terkena_pukul(20, boss.rect)

        # --------------------------------------------------------
        # LOGIKA SPAWN BOSS & TANGGA NEXT LEVEL LURUS
        # --------------------------------------------------------
        jumlah_kroco_hidup = len([musuh for musuh in daftar_musuh if musuh.hidup and not musuh.apakah_boss])
        
        if jumlah_kroco_hidup == 0 and not boss_spawn:
            if stage == 1:
                boss = bossFirst(boss_pixel_x, boss_pixel_y, path_boss)
            elif stage == 2:
                boss = bossSecond(boss_pixel_x, boss_pixel_y, path_boss2)
            elif stage == 3:
                boss = bossThird(boss_pixel_x, boss_pixel_y, path_boss3)
            boss.apakah_boss = True
            daftar_musuh.append(boss)
            boss_spawn = True
            
        boss_mati = boss_spawn and len([m for m in daftar_musuh if m.apakah_boss and m.hidup]) == 0
        
        if boss_mati and not tangga_sudah_muncul:
            DUNGEON_MAP[ruangan_boss.center_y][ruangan_boss.center_x] = id_ubin_tangga
            tangga_sudah_muncul = True
            print("Ubin peta telah berubah menjadi tangga!")

        # Hitung koordinat ubin injakan ksatria
        ksatria_row = ksatria.rect.centery // TILE_SIZE
        ksatria_col = ksatria.rect.centerx // TILE_SIZE
        
        # Cek input Ksatria menginjak tangga untuk pindah stage
        if 0 <= ksatria_row < MAP_ROWS and 0 <= ksatria_col < MAP_COLS:
            if DUNGEON_MAP[ksatria_row][ksatria_col] == id_ubin_tangga and keys[pygame.K_e]:
                buat_level_baru()
                stage += 1

    # ========================================================
    # 4. RENDERING TAMPILAN JELAS (JALAN DI LUAR EVENT LOOP)
    # ========================================================
    if game_state == "playing":
        screen.fill((15, 15, 20))
    
        # A. Render Lapisan Ubin Peta Dungeon
        start_col = max(0, camera_x // TILE_SIZE)
        end_col   = min(MAP_COLS, (camera_x + SCREEN_WIDTH) // TILE_SIZE + 1)
        start_row = max(0, camera_y // TILE_SIZE)
        end_row   = min(MAP_ROWS, (camera_y + SCREEN_HEIGHT) // TILE_SIZE + 1)
        
        for row_idx in range(start_row, end_row):
            for col_idx in range(start_col, end_col):
                tile = DUNGEON_MAP[row_idx][col_idx]
                x = col_idx * TILE_SIZE - camera_x
                y = row_idx * TILE_SIZE - camera_y

                if -TILE_SIZE < x < SCREEN_WIDTH and -TILE_SIZE < y < SCREEN_HEIGHT:
                    if tile in MAP_TILES_IMAGE:
                        screen.blit(MAP_TILES_IMAGE[tile], (x, y))
                    else:
                        pygame.draw.rect(screen, (200, 0, 0), (x, y, TILE_SIZE, TILE_SIZE))
                        
        # B. Render Semua Peti Harta Karun (Chest)
        for chest in daftar_chest:
            chest.draw(screen, camera_x, camera_y) 
            
        # C. Render Semua Musuh & Boss yang Hidup
        for musuh in daftar_musuh:
            if musuh.hidup:
                posisi_render_x = musuh.rect.x - camera_x
                posisi_render_y = musuh.rect.y - camera_y
                screen.blit(musuh.image, (posisi_render_x, posisi_render_y))

        # D. Render Semua Objek Proyektil Peluru
        for p in daftar_proyektil:
            p.draw(screen, camera_x, camera_y)

        # E. Render Karakter Utama Ksatria dan Senjatanya
        ksatria.draw(screen, camera_x, camera_y)
        if ksatria.hidup:
            senjata.draw(screen, camera_x, camera_y)
        # F. Render UI Lapisan Atas (Minimap & Pause Menu jika Aktif)
        draw_minimap(screen, DUNGEON_MAP, ksatria)
        if pause_menu.active:
            pause_menu.draw(screen)
        if ksatria.hidup:
            hud.draw(screen, ksatria)
        if ksatria.hp <= 0:
            pygame.mixer.music.stop()  # Hentikan musik saat game over
            screen.fill((0, 0, 0))
            game_over_text = pygame.font.SysFont(None, 72).render("GAME OVER", True, (255, 0, 0))
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(game_over_text, text_rect)
            pygame.display.flip()
            pygame.time.delay(3000)
            pygame.mixer.music.load(path_menu_bgm)
            pygame.mixer.music.play(-1)
            game_state = "menu"
            continue
        
    pygame.display.flip()