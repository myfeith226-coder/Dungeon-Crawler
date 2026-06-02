# Dungeon-Crawler
Game ini merupakan game 2D dengan genre RPG klasik dimana seorang kesatria menjelajahi lingkungan yang berliku-liku (Dungeon), melawan monster, mencari harta Karun, dan mengalahkan bos.

Kelompok 3
Anggota Kelompok:
- Dandi Dwi Rachmat 
- Ravael Ivander
- Bintang
- Fatah Mushily

Fitur Utama:
- Bergerak dengan menggunakan anak panah keyboard (WASD)
- Menyerang dengan menggunakan tombol spasi
- Ganti senjata dengan menggunakan tombol 1-5

Cara Menjalankan:
1. Klik tombol play pada menu utama
2. Lalu gerakkan karakter player dengan menggunakan tombol (WASD)
3. Gunakan tombol spasi untuk menyerang musuh
4. Jika ingin berganti senjata gunakan tombol 1-5
5. Kalahkan semua musuh untuk melawan bos
6. Kalahkan bos untuk memenangkan setiap level

Implementasi Objek Oriented Programming (OOP):
1. Abstraksi dan Enkapsulasi data melalui Class
program ini menggunakan class untuk membungkus data (attribut) dan perilaku (method) menjadi satu kesatuan objek yang logis.

class Room:
    def __init__(self, x, y, w, h): # Konstruktor untuk inisialisasi objek
        self.x1, self.y1 = x, y
        # ... (enkapsulasi koordinat)
        
    def intersects(self, other): # Perilaku objek
        return (...)

**class Room**
class ini digunakan sebagai template untuk menciptakan ruangan-ruangan di dalam dungeon.
**Atribut(data)**: x1, y1, x2, y2, center_x dan center_y. Attribut ini menyimpan data koordinat dan ukuran dari setiap ruangan secara spesifik.
**Method**: intersects(self, other). Ini adalah fungsi internal milik objek Room untuk mengecek apakah dirinya bertabrakan dengan objek Room lainnya (other).

2. Polimorfisme dan Pewarisan (Inheritance) melalui Pygame Sprite

grup_musuh = pygame.sprite.Group()

grup_musuh.add(musuh_biasa)
grup_musuh.add(boss)

Di dalam Game Loop (Polimorfisme bekerja di sini)
grup_musuh.update(ksatria, tembok_aktif)

Penggunaan pygame.sprite.Group()
Di dalam loop utama, terdapat penggunaan grup_musuh = pygame.sprite.Group()
- Inheritance: Class Musuh merupakan turunan (child class) dari pygame.sprite.Sprite. Oleh karena itu, objek musuh_biasa dan boss mewarisi properti seperti .image dan .rect
- Polimorfisme: Mengelompokkan berbagai musuh (baik musuh biasa maupun boss) ke dalam satu wadah bernama grup_musuh. Saat memanggil grup_musuh_update(...), pygame secara otomatis memanggil method .update() milik masing masing objek di dalamnya tanpa peduli apakah itu musuh biasa atau boss

3. Interaksi Antae Objek (Object Interaction)
Di dalam game loop terjadi interaksi:
- Objek Player(ksatria) dengan lingkungan(walls): ksatria.update(walls) -> Objek ksatria membutuhkan data list walls (kumpulan koordinat pygame.Rect) untuk mendeteksi apakah dirinya menabrak dinding atau tidak.

- Objek Musuh dengan Player: grup_musuh.update(ksatria, walss) -> objek musuh diberikan referensi objek kesatria agar AI musuh mengetahui posisi koordinat pemain untuk di kejar.

- Objek Senjata(pedang) dengan Player: pedang.update(ksatria) -> Objek pedang membaca posisi dan arah dari obhek ksatria agar posisi senjata selalu menempel di tangan karakter.
