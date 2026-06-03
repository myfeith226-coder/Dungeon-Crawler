import os

path_target = r"e:\py\hloges\assets\Maps\map.png"
folder_maps = r"e:\py\hloges\assets\Maps"

print("=== HASIL INVESTIGASI ===")
print(f"1. Apakah file map.png benar-benar ada? -> {os.path.exists(path_target)}")

if os.path.exists(folder_maps):
    print(f"2. Folder 'Maps' ditemukan. Berikut adalah ISI ASLI di dalamnya:")
    print(os.listdir(folder_maps))
else:
    print("2. Folder 'Maps' JUSTRU TIDAK DITEMUKAN oleh sistem!")