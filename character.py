import pygame
import math
import os

from abc import ABC, abstractmethod # 1. ABSTRACTION: Import modul ABC
from TileSet import TILE_SIZE, MAP_TILES_IMAGE, get_tile_safely
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
path_senjata1 = os.path.join(BASE_DIR, "assets", "Knight", "WeaponsAsset16x16", "004.png")
path_senjata2 = os.path.join(BASE_DIR, "assets", "Knight", "WeaponsAsset16x16", "104.png")
path_panah = os.path.join(BASE_DIR, "assets", "Knight", "WeaponsAsset16x16", "105.png")
path_senjata3 = os.path.join(BASE_DIR, "assets", "Knight", "WeaponsAsset16x16", "033.png")
path_senjata4 = os.path.join(BASE_DIR, "assets", "Knight", "WeaponsAsset16x16", "295.png")
path_senjata5 = os.path.join(BASE_DIR, "assets", "Knight", "WeaponsAsset16x16", "069.png")
# --- ABSTRACTION ---
# Kelas Karakter murni sebagai Kelas Induk Abstrak
class Karakter(ABC): 
    def __init__ (self, x, y, skala, kecepatan):
        # Tidak ada lagi super().__init__() untuk sprite
        self.skala = skala
        self.kecepatan = kecepatan
        self.status = "idle"
        self.flip = False
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        
        self.anim_idle = []
        self.anim_run = []
        self.animasi_sekarang = []
        
        # --- ENKAPSULASI: Variabel Private ---
        self.__hp = 100 
        self.hidup = True
        
    # --- ENKAPSULASI: Getter & Setter ---
    @property
    def hp(self):
        return self.__hp

    @hp.setter
    def hp(self, nilai_baru):
        if nilai_baru <= 0:
            self.__hp = 0
            self.hidup = False
        else:
            self.__hp = nilai_baru

    # --- POLYMORPHISM (Abstract Method) ---
    # Wajib diisi logika berbeda oleh Ksatria dan Musuh
    @abstractmethod
    def update(self, *args, **kwargs):
        pass

    @abstractmethod
    def terkena_pukul(self, damage):
        pass
    
    # --- INHERITANCE: Method yang otomatis diwariskan ---
    def muat_gambar_folder(self, folder, aksi, jumlah_frame):
        list_sementara = []
        for i in range(jumlah_frame):
            nama_file = f"assets/Knight/knight_m_{aksi}_anim_f{i}.png"
            img = pygame.image.load(nama_file).convert_alpha()
            img = pygame.transform.scale(img, (img.get_width() * self.skala, img.get_height() * self.skala))
            list_sementara.append(img)
        return list_sementara

    def muat_gambar_strip(self, nama_file, jumlah_frame):
        strip_img = pygame.image.load(nama_file).convert_alpha()
        lebar_frame = strip_img.get_width() // jumlah_frame
        tinggi_frame = strip_img.get_height()
        
        list_sementara = []
        for i in range(jumlah_frame):
            frame = strip_img.subsurface((i * lebar_frame, 0, lebar_frame, tinggi_frame))
            frame = pygame.transform.scale(frame , (lebar_frame * self.skala, tinggi_frame * self.skala))
            list_sementara.append(frame)
        return list_sementara
    
    def update_animasi(self):
        ANIMATION_COOLDOWN = 100
        if self.frame_index >= len(self.animasi_sekarang):
            self.frame_index = 0
        
        self.image = self.animasi_sekarang[self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
    
    def draw(self, surface, camera_x=0, camera_y=0):
        gambar_final = pygame.transform.flip(self.image, self.flip, False)
        render_x = self.rect.x - camera_x
        render_y = self.rect.y - camera_y
        surface.blit(gambar_final, (render_x, render_y))

        
class Player(Karakter):
    def __init__(self, x, y):
        super().__init__(x, y, 3, 10)
        self.hit_berjalan = False
        self.waktu_hit = 0
        self.kebal = False
        self.waktu_kebal = 0
        self.masa_kebal = 1000
        self.knockback_dx = 0
        self.knockback_dy = 0
        self.durasi_knockback = 150 
        self.sudut_wajah = 0
        self.inventory = [] 
        self.anim_idle = self.muat_gambar_folder("Knight", "idle", 4)
        self.anim_run = self.muat_gambar_folder("Knight", "run", 4)
        self.anim_hit = self.muat_gambar_folder("Knight", "hit", 1)
        
        self.animasi_sekarang = self.anim_idle
        self.image = self.animasi_sekarang[self.frame_index]
        self.rect = self.image.get_rect(center=(x, y))
        
    def update(self, walls):
        if not self.hidup:
            return
        
        waktu_sekarang = pygame.time.get_ticks()
        if self.kebal:
            if waktu_sekarang - self.waktu_kebal > self.masa_kebal:
                self.kebal = False
                
        if self.hit_berjalan:
            self.status = "hit"
            self.animasi_sekarang = self.anim_hit
            if waktu_sekarang - self.waktu_hit < self.durasi_knockback:
                self.rect.x += self.knockback_dx
                self.check_collision_axis(self.knockback_dx, 0, walls)
                self.rect.y += self.knockback_dy
                self.check_collision_axis(0, self.knockback_dy, walls)
            if waktu_sekarang - self.waktu_hit > 300:
                self.hit_berjalan = False
        else:
            dx, dy = 0, 0
            self.status = "idle"
            keys = pygame.key.get_pressed()
            
            if not self.hit_berjalan:
                if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                    dx = -self.kecepatan
                    self.flip, self.status = True, "run"
                if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    dx = self.kecepatan
                    self.flip, self.status = False, "run"
                if keys[pygame.K_w] or keys[pygame.K_UP]:
                    dy = -self.kecepatan
                    self.status = "run"
                if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                    dy = self.kecepatan
                    self.status = "run"
                
                if dx != 0 or dy != 0:
                    self.sudut_wajah = -math.degrees(math.atan2(dy, dx))
                    
            self.rect.x += dx
            self.check_collision_axis(dx, 0, walls)
            
            # 3. Gerakkan sumbu Y dan langsung cek tabrakan Y
            self.rect.y += dy
            self.check_collision_axis(0, dy, walls)
            self.animasi_sekarang = self.anim_run if self.status == "run" else self.anim_idle
        self.update_animasi()
        
    def terkena_pukul(self, damage, musuh_rect):
        if self.hidup and not self.kebal:
            self.hp -= damage
            print(f"HP Tersisa : {self.hp}")
            
            self.kebal = True
            self.waktu_kebal = pygame.time.get_ticks()
            
            self.hit_berjalan = True
            self.waktu_hit = pygame.time.get_ticks()
            self.frame_index = 0
            
            jarak_x = self.rect.centerx - musuh_rect.centerx
            jarak_y = self.rect.centery - musuh_rect.centery
            
            panjang = (jarak_x**2 + jarak_y**2)**0.5
            
            KEKUATAN_KNOCKBACK = 8
            if panjang != 0:
                self.knockback_dx = (jarak_x/panjang) * KEKUATAN_KNOCKBACK
                self.knockback_dy = (jarak_y/panjang) * KEKUATAN_KNOCKBACK
                
            if self.hp <= 0:
                self.hp = 0
                self.hidup = False
                print("Ksatria Telah Gugur!")
    
    def check_collision_axis(self, dx, dy, walls):
        for wall in walls:
            if self.rect.colliderect(wall):
                if dx > 0: self.rect.right = wall.left
                if dx < 0: self.rect.left = wall.right
                if dy > 0: self.rect.bottom = wall.top
                if dy < 0: self.rect.top = wall.bottom

    def draw(self, surface, camera_x, camera_y):
        gambar_final = pygame.transform.flip(self.image, self.flip, False)
    
        # 2. Ambil rect baru dari gambar yang di-flip agar rotasi/posisi tetap di pusat
        rect_gambar = gambar_final.get_rect(center=self.rect.center)
        
        # 3. Sesuaikan posisi koordinat X dan Y dengan pergerakan kamera
        rect_gambar.x -= camera_x
        rect_gambar.y -= camera_y
        
        # 4. Gambar objek ke layar menggunakan posisi kamera yang baru
        surface.blit(gambar_final, rect_gambar)
        # pygame.draw.rect(surface, (0, 180, 255), (*screen_pos, self.rect.width, self.rect.height))
              
class Proyektil():
    def __init__(self, x, y, arah_x, jenis, damage, skala):
        self.damage = damage
        self.jenis = jenis 
        self.kecepatan = 10 * arah_x
        
        if jenis == "panah":
            try:
                img = pygame.image.load(path_panah).convert_alpha()
                img = pygame.transform.rotate(img, -50)
                if arah_x == -1:
                    img = pygame.transform.flip(img, True, False)
            except FileNotFoundError:
                img = pygame.Surface((15, 3))
                img.fill((139, 69, 19))
                if arah_x == -1:
                    img = pygame.transform.flip(img, True, False)
                    
        elif jenis == "sihir":
            img = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(img, (0, 0, 255), (5, 5), 5)
        else:
            img = pygame.Surface((5, 5))
            img.fill((255, 255, 255))
            
        self.image = pygame.transform.scale(img, (img.get_width() * skala, img.get_height() * skala))
        self.rect = self.image.get_rect(center=(x, y))
        
    def update(self):
        self.rect.x += self.kecepatan
        
    def draw(self, surface, camera_x, camera_y):
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y - camera_y))

class Senjata():
    def __init__(self, skala):
        self.skala = skala
        
        self.daftar_senjata = [
            {"nama": "Pedang", "path": path_senjata1, "damage": 15, "durasi": 150, "tipe": "swing"},
            {"nama": "Panah", "path": path_senjata2, "damage": 10, "durasi": 300, "tipe": "ranged", "jenis_proyektil": "panah"},
            {"nama": "Golok", "path": path_senjata3, "damage": 25, "durasi": 300, "tipe": "swing"},
            {"nama": "Tongkat Sihir", "path": path_senjata4, "damage": 12, "durasi": 1000, "tipe": "ranged", "jenis_proyektil": "sihir"},
            {"nama": "Tombak", "path": path_senjata5, "damage": 18, "durasi": 200, "tipe": "thrust"}
        ]
        
        self.indeks_aktif = 0
        self.menyerang = False
        self.waktu_serang = 0
        self.sudah_kena = False
        self.sudah_nembak = False
        self.muat_senjata()

    def muat_senjata(self):
        senjata = self.daftar_senjata[self.indeks_aktif]
        self.damage = senjata["damage"]
        self.durasi_serang = senjata["durasi"]
        self.tipe_serangan = senjata["tipe"]
        self.jenis_proyektil = senjata.get("jenis_proyektil", None)
        
        try:
            img = pygame.image.load(senjata["path"]).convert_alpha()
        except FileNotFoundError:
            img = pygame.Surface((6, 20))
            img.fill((150, 150, 150))
            
        self.gambar_asli = pygame.transform.scale(img, (img.get_width() * self.skala, img.get_height() * self.skala))
        self.image = self.gambar_asli
        self.rect = self.image.get_rect()
        print(f"Senjata Diganti: {senjata['nama']} | Tipe: {self.tipe_serangan}")

    def ganti_senjata(self, indeks):
        if not self.menyerang and indeks != self.indeks_aktif:
            self.indeks_aktif = indeks
            self.muat_senjata()

    def update(self, player, daftar_proyektil):
        if not player.hidup:
            return
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and not self.menyerang:
            self.menyerang = True
            self.waktu_serang = pygame.time.get_ticks()
            self.sudah_kena = False
            self.sudah_nembak = False 
            
        if self.menyerang:
            if pygame.time.get_ticks() - self.waktu_serang > self.durasi_serang:
                self.menyerang = False
        
        OFFSET_Y_DIAM = 18 
        if not self.menyerang:
            OFFSET_X_DIAM = 22 
            if not player.flip:
                self.image = self.gambar_asli
                self.rect = self.image.get_rect()
                self.rect.centerx = player.rect.centerx + OFFSET_X_DIAM
            else:
                self.image = pygame.transform.flip(self.gambar_asli, True, False)
                self.rect = self.image.get_rect()
                self.rect.centerx = player.rect.centerx - OFFSET_X_DIAM
            self.rect.centery = player.rect.centery + OFFSET_Y_DIAM

        else:
            if self.tipe_serangan == "ranged" and not self.sudah_nembak:
                arah_x = -1 if player.flip else 1
                proyektil = Proyektil(self.rect.centerx, self.rect.centery - 10, arah_x, self.jenis_proyektil, self.damage, self.skala)
                daftar_proyektil.append(proyektil)
                self.sudah_nembak = True

            if self.tipe_serangan == "swing":
                OFFSET_X_SERANG = 35  
                OFFSET_Y_SERANG = 45 
                if not player.flip:
                    self.image = pygame.transform.rotate(self.gambar_asli, -90)
                    self.rect = self.image.get_rect()
                    self.rect.centerx = player.rect.centerx + OFFSET_X_SERANG
                else:
                    gambar_flip = pygame.transform.flip(self.gambar_asli, True, False)
                    self.image = pygame.transform.rotate(gambar_flip, 90)
                    self.rect = self.image.get_rect()
                    self.rect.centerx = player.rect.centerx - OFFSET_X_SERANG
                self.rect.centery = player.rect.centery + OFFSET_Y_SERANG

            elif self.tipe_serangan == "thrust":
                OFFSET_X_SERANG = 45  
                if not player.flip:
                    self.image = pygame.transform.rotate(self.gambar_asli, -45) 
                    self.rect = self.image.get_rect()
                    self.rect.centerx = player.rect.centerx + OFFSET_X_SERANG
                else:
                    gambar_flip = pygame.transform.flip(self.gambar_asli, True, False)
                    self.image = pygame.transform.rotate(gambar_flip, 45)
                    self.rect = self.image.get_rect()
                    self.rect.centerx = player.rect.centerx - OFFSET_X_SERANG
                self.rect.centery = player.rect.centery + OFFSET_Y_DIAM

            elif self.tipe_serangan == "ranged":
                OFFSET_X_SERANG = 25
                if not player.flip:
                    self.image = self.gambar_asli
                    self.rect = self.image.get_rect()
                    self.rect.centerx = player.rect.centerx + OFFSET_X_SERANG
                else:
                    self.image = pygame.transform.flip(self.gambar_asli, True, False)
                    self.rect = self.image.get_rect()
                    self.rect.centerx = player.rect.centerx - OFFSET_X_SERANG
                self.rect.centery = player.rect.centery + OFFSET_Y_DIAM

    def draw(self, surface, camera_x, camera_y):
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y - camera_y))
        
class Musuh(Karakter):
    def __init__(self, x, y, file_strip, jmlframe):
        super().__init__(x, y, 2, 2)
        
        self.anim_run = self.muat_gambar_strip(file_strip, jmlframe)
        self.animasi_sekarang = self.anim_run
        self.image = self.animasi_sekarang[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.hitbox = self.rect.inflate(-100, -60)
        
        self.arah = 1
        self.waktu_patroli = pygame.time.get_ticks()
        
        self.hp = 3
        self.melihat_pemain = False
        self.waktu_melihat = 0
        self.waktu_reaksi = 600
    
    def terkena_pukul(self,damage):
        if self.hidup:
            self.hp -= damage
            print(f"HP Musuh Tersisa: {self.hp}")
    
    def check_collision_axis(self, dx, dy, walls):
        for wall in walls:
            if self.rect.colliderect(wall):
                if dx > 0: self.rect.right = wall.left
                if dx < 0: self.rect.left = wall.right
                if dy > 0: self.rect.bottom = wall.top
                if dy < 0: self.rect.top = wall.bottom
                
    def update(self, player, walls):
        if not self.hidup: # Cegah musuh bergerak kalau sudah mati
            return
            
        if not player.hidup:
            jarak_total = 999
        else:
            jarak_x = player.rect.centerx - self.rect.centerx
            jarak_y = player.rect.centery - self.rect.centery
            jarak_total = (jarak_x**2 + jarak_y**2) ** 0.5
            
        JARAK_DETEKSI = 200
        dx, dy = 0, 0
        # ==========================================
        # LOGIKA REAKSI & PENGEJARAN
        # ==========================================
        if jarak_total < JARAK_DETEKSI:
            # 1. Saat pertama kali melihat Ksatria
            if not self.melihat_pemain:
                self.melihat_pemain = True
                self.waktu_melihat = pygame.time.get_ticks() # Catat waktu kaget
                
            # 2. Hanya kejar JIKA waktu kaget sudah lewat
            if pygame.time.get_ticks() - self.waktu_melihat > self.waktu_reaksi:
                if jarak_x > 0:
                    dx = self.kecepatan # Masukkan ke variabel dx, jangan langsung rect.x
                    self.flip = False
                elif jarak_x < 0:
                    dx = -self.kecepatan
                    self.flip = True
                    
                if jarak_y > 0:
                    dy = self.kecepatan # Masukkan ke variabel dy, jangan langsung rect.y
                elif jarak_y < 0:
                    dy = -self.kecepatan      
        else: 
            # Jika Ksatria kabur menjauh, reset status melihat
            self.melihat_pemain = False
            
            # Logika patroli biasa
            if pygame.time.get_ticks() - self.waktu_patroli > 2000:
                self.arah *= -1
                self.flip = not self.flip
                self.waktu_patroli = pygame.time.get_ticks()
                
            dx = self.kecepatan * self.arah
            dy = 0
            
            
        self.rect.x += dx
        self.check_collision_axis(dx, 0, walls)

        self.rect.y += dy
        self.check_collision_axis(0, dy, walls)

        self.hitbox.center = self.rect.center
        self.update_animasi()
class bossFirst(Musuh):
    def __init__(self, x, y, folder_boss):
        super().__init__(x, y, f"{folder_boss}/FLYING.png", 4)
        self.skala = 3
        self.hp = 150
        self.kecepatan = 2
        
        self.anim_idle = self.muat_gambar_strip(f"{folder_boss}/IDLE.png", 4)
        self.anim_run = self.muat_gambar_strip(f"{folder_boss}/FLYING.png", 4)
        self.anim_attack = self.muat_gambar_strip(f"{folder_boss}/ATTACK.png", 8)
        self.anim_death = self.muat_gambar_strip(f"{folder_boss}/DEATH.png", 7)
        self.anim_hurt = self.muat_gambar_strip(f"{folder_boss}/HURT.png", 4)
        
        self.status = "idle"
        self.animasi_sekarang = self.anim_idle
        
        self.hitbox = self.rect.inflate(-40, 15)
        self.hilang = False
        
        self.waktu_hurt = 0
    
    def terkena_pukul(self, damage):
        if self.hidup:
            self.hp -= damage
            print(f"HP Boss Tersisa : {self.hp}")
            if self.hp <= 0:
                self.hidup = False
                self.status = "death"
                self.animasi_sekarang = self.anim_death
                self.frame_index = 0
                print("Boss Berhasil Dikalahkan")
            else:
                self.status = "hurt"
                self.animasi_sekarang = self.anim_hurt
                self.frame_index = 0
                self.waktu_hurt = pygame.time.get_ticks()
    def check_collision_axis(self, dx, dy, walls):
        for wall in walls:
            if self.rect.colliderect(wall):
                if dx > 0: self.rect.right = wall.left
                if dx < 0: self.rect.left = wall.right
                if dy > 0: self.rect.bottom = wall.top
                if dy < 0: self.rect.top = wall.bottom
                
    def update(self, player,walls):
        if not self.hidup:  
            if self.status == "death":      
                if self.frame_index < len(self.anim_death) - 1:
                    self.update_animasi()
                else:
                    self.hilang = True
            return
    
                    
        DURASI_HURT_ANIMATION = 300
        if self.status == "hurt":
            if pygame.time.get_ticks() - self.waktu_hurt > DURASI_HURT_ANIMATION:
                self.status = "idle"
            else:
                self.update_animasi()
                return
        if not player.hidup:
            jarak_total = 999
        else:
            jarak_x = player.rect.centerx - self.rect.centerx
            jarak_y = player.rect.centery - self.rect.centery 
            jarak_total = (jarak_x**2 + jarak_y**2) ** 0.5
        JARAK_DETEKSI = 300
        JARAK_SERANG = 90   
        
        if jarak_total < JARAK_DETEKSI:
            if jarak_total < JARAK_SERANG:
                self.status = "attack"
                self.animasi_sekarang = self.anim_attack
            else: 
                self.status = "run"
                self.animasi_sekarang = self.anim_run
                if jarak_x > 0: self.rect.x += self.kecepatan; self.flip = True
                elif jarak_x < 0: self.rect.x -= self.kecepatan; self.flip = False
                if jarak_y > 0: self.rect.y += self.kecepatan
                elif jarak_y < 0: self.rect.y -= self.kecepatan
        else:
            self.status = "idle"
            self.animasi_sekarang = self.anim_idle
        
        self.hitbox.center = self.rect.center
        self.update_animasi()
        
class bossSecond(Musuh):
    def __init__(self, x, y, folder_boss):
        super().__init__(x, y, f"{folder_boss}/hooded knight idle.png", 8)
        self.skala = 2
        self.hp = 200
        self.kecepatan = 1.5
        
        self.post_x = float(x)
        self.post_y = float(y)
        
        self.anim_idle = self.muat_gambar_strip(f"{folder_boss}/hooded knight idle.png", 8)
        self.anim_attack = self.muat_gambar_strip(f"{folder_boss}/hooded knight attack.png", 17)
        self.anim_powerup = self.muat_gambar_strip(f"{folder_boss}/hooded knight powerup.png", 19)
        self.anim_run = self.anim_idle
        
        self.status = "idle"
        self.animasi_sekarang = self.anim_idle
        
        self.hitbox = self.rect.inflate(-80, -40)
        self.hilang = False
        self.fase_powerup = False
    def check_collision_axis(self, dx, dy, walls):
        for wall in walls:
            if self.rect.colliderect(wall):
                if dx > 0: self.rect.right = wall.left
                if dx < 0: self.rect.left = wall.right
                if dy > 0: self.rect.bottom = wall.top
                if dy < 0: self.rect.top = wall.bottom  
                 
    def update(self, player,walls):
        if not self.hidup:
            self.hilang = True
            return

        jarak_x = player.rect.centerx - self.rect.centerx
        jarak_y = player.rect.centery - self.rect.centery 
        jarak_total = (jarak_x**2 + jarak_y**2) ** 0.5
        
        if self.hp < 100 and not self.fase_powerup:
            if self.status != "powerup":
                self.status = "powerup"
                self.animasi_sekarang = self.anim_powerup
                self.frame_index = 0
            if self.frame_index >= len(self.anim_powerup) - 1:
                self.fase_powerup = True
                self.kecepatan = 2
                self.status = "idle"
        elif jarak_total < 350:
            if jarak_total < 120:
                if self.status != "attack":
                    self.status = "attack"
                    self.animasi_sekarang = self.anim_attack
                    self.frame_index = 0
            else:
                self.status = "run"
                self.animasi_sekarang = self.anim_idle
                if jarak_x > 0: self.post_x += self.kecepatan; self.flip = False
                elif jarak_x < 0: self.post_x -= self.kecepatan; self.flip = True
                if jarak_y > 0: self.post_y += self.kecepatan
                elif jarak_y < 0: self.post_y -= self.kecepatan
                self.rect.x = int(self.post_x)
                self.rect.y = int(self.post_y)
        else:
            self.status = "idle"
            self.animasi_sekarang = self.anim_idle

        self.hitbox.center = self.rect.center
        self.update_animasi()

class bossThird(Musuh):
    def __init__(self, x, y, folder_boss):
        super().__init__(x, y, f"{folder_boss}/idle.png", 5)
        self.skala = 2.5
        self.hp = 250
        self.kecepatan = 1.5
        
        self.post_x = float(x)
        self.post_y = float(y)
        
        self.anim_idle = self.muat_gambar_strip(f"{folder_boss}/idle.png", 5)[:4]
        self.anim_run = self.anim_idle
        self.anim_attack = self.muat_gambar_grid(f"{folder_boss}/attacking.png", cols=6, rows=3, total_frames=13)
        self.anim_death = self.muat_gambar_grid(f"{folder_boss}/death.png", cols=10, rows=2, total_frames=18)
        
        self.status = "idle"
        self.animasi_sekarang = self.anim_idle
        self.rect = self.animasi_sekarang[0].get_rect(center=(x, y))
        self.hitbox = self.rect.inflate(-60, -20)
        self.hilang = False
    
    def muat_gambar_grid(self, path, cols, rows, total_frames):
        sheet = pygame.image.load(path).convert_alpha()
        
        frame_w = sheet.get_width() // cols
        frame_h = sheet.get_height() // rows
        
        frames = []
        for i in range(total_frames):
            col = i % cols      
            row = i // cols     
            
            rect = pygame.Rect(col * frame_w, row * frame_h, frame_w, frame_h)
            image = sheet.subsurface(rect)
            
            image = pygame.transform.scale(image, (int(frame_w * self.skala), int(frame_h * self.skala)))
            frames.append(image)
            
        return frames

    def terkena_pukul(self, damage):
        if self.hidup:
            self.hp -= damage
            print(f"HP Boss 3 Tersisa : {self.hp}")
            if self.hp <= 0:
                self.hidup = False
                self.status = "death"
                self.animasi_sekarang = self.anim_death
                self.frame_index = 0
    def check_collision_axis(self, dx, dy, walls):
        for wall in walls:
            if self.rect.colliderect(wall):
                if dx > 0: self.rect.right = wall.left
                if dx < 0: self.rect.left = wall.right
                if dy > 0: self.rect.bottom = wall.top
                if dy < 0: self.rect.top = wall.bottom
    def update(self, player, walls):
        if not self.hidup:
            if self.status == "death":
                if self.frame_index < len(self.anim_death) - 1:
                    self.update_animasi()
                else:
                    self.hilang = True
            return

        jarak_x = player.rect.centerx - self.rect.centerx
        jarak_y = player.rect.centery - self.rect.centery 
        jarak_total = (jarak_x**2 + jarak_y**2) ** 0.5
        
        if self.status == "attack":
            if self.frame_index >= len(self.anim_attack): 
                self.status = "idle"
                self.animasi_sekarang = self.anim_idle
                self.frame_index = 0
        else:
            if jarak_total < 400:
                if jarak_total < 120:
                    self.status = "attack"
                    self.animasi_sekarang = self.anim_attack
                    self.frame_index = 0
                else:
                    self.status = "run"
                    self.animasi_sekarang = self.anim_run
                    
                    if jarak_x > 0: self.post_x += self.kecepatan; self.flip = False
                    elif jarak_x < 0: self.post_x -= self.kecepatan; self.flip = True
                    if jarak_y > 0: self.post_y += self.kecepatan
                    elif jarak_y < 0: self.post_y -= self.kecepatan
                    
                    self.rect.x = int(self.post_x)
                    self.rect.y = int(self.post_y)
            else:
                self.status = "idle"
                self.animasi_sekarang = self.anim_idle

        self.update_animasi()
        self.hitbox.midbottom = self.rect.midbottom

    def update_animasi(self):
        ANIMATION_COOLDOWN = 100
        
        if self.frame_index >= len(self.animasi_sekarang):
            self.frame_index = 0
            
        posisi_kaki = self.rect.midbottom
        
        self.image = self.animasi_sekarang[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.midbottom = posisi_kaki
        
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
class Chest:
    def __init__(self, x, y, skala=4):
        self.skala = skala
        path_tutup = os.path.join(BASE_DIR, "assets", "Maps", "Chest_Closed.png")
        path_buka  = os.path.join(BASE_DIR, "assets", "Maps", "Chest_Opened.png")
        try:
            img_tutup = pygame.image.load(path_tutup).convert_alpha()
            img_buka  = pygame.image.load(path_buka).convert_alpha()
            
            # Ubah ukuran skala gambar agar pas dengan ukuran game Anda
            self.img_tertutup = pygame.transform.scale(img_tutup, (img_tutup.get_width() * skala, img_tutup.get_height() * skala))
            self.img_terbuka  = pygame.transform.scale(img_buka, (img_buka.get_width() * skala, img_buka.get_height() * skala))
        except FileNotFoundError:
            print(f" ERROR: File gambar chest tidak ditemukan di: {path_tutup}. Menggunakan kotak warna cadangan.")
            # Cadangan kotak warna jika file gambar belum ditaruh di folder assets
            self.img_tertutup = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.img_tertutup.fill((139, 69, 19)) # Cokelat tua
            self.img_terbuka = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.img_terbuka.fill((210, 105, 30)) # Cokelat muda
        self.image = self.img_tertutup
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = self.rect
        self.sudah_terbuka = False 

    def terkena_pukul(self, player):
        if not self.sudah_terbuka:
            self.sudah_terbuka = True  
            self.image = self.img_terbuka # Ganti gambar ke versi terbuka
            print("Peti berhasil dibuka! Potion langsung masuk ke tas.")
            
            # Masukkan item ke inventory player secara PBO
            item_baru = Potion()
            player.inventory.append(item_baru)
            
    def draw(self, surface, camera_x, camera_y):
        render_x = self.rect.x - camera_x
        render_y = self.rect.y - camera_y
        surface.blit(self.image, (render_x, render_y))
                                
class Potion:
    def __init__(self, nama="Ramuan Penyembuh", efek_heal=30):
        self.nama = nama
        self.efek_heal = efek_heal

    def gunakan(self, player):
        """Fungsi untuk mengonsumsi potion dari tas"""
        player.hp += self.efek_heal
        if player.hp > 100:
            player.hp = 100
        print(f"Menggunakan {self.nama}! HP bertambah {self.efek_heal}. Sisa HP: {player.hp}")