# Setup Lanjutan SuperIsland (Fork Lokal)

Repo original: https://github.com/shobhit99/SuperIsland
Lokasi lokal: `/Volumes/MyDisk-aldy-uhaa/Projects-App/superisland-rebuild`

## Status Saat Ini
- ✅ Repo berhasil di-clone & di-duplicate (full history terjaga)
- ✅ Remote `upstream` = repo original (untuk pull update kalau kreator update lagi)
- ⏳ Remote `origin` = belum di-set (punya kamu sendiri)

## Langkah Selanjutnya (Wajib)

### 1. Buat repo baru di GitHub kamu
1. Buka https://github.com/new
2. Nama contoh: `superisland-rebuild` atau `SuperIsland` (bebas)
3. Jangan centang "Initialize with README" (biar kosong)
4. Create

### 2. Hubungkan repo lokal ke GitHub kamu
```bash
cd /Volumes/MyDisk-aldy-uhaa/Projects-App/superisland-rebuild
git remote add origin https://github.com/USERNAME-KAMU/superisland-rebuild.git
git branch -M main
git push -u origin main
```

> Ganti `USERNAME-KAMU` dengan username GitHub kamu.

### 3. Install dependencies untuk build
```bash
brew install xcodegen    # generate .xcodeproj dari project.yml
# Node 18+ hanya kalau mau ngoprek Extensions
```

Butuh **Xcode 15+** (macOS 14 Sonoma ke atas). Saat ini di Mac ini Xcode belum terdeteksi — install dari App Store dulu.

### 4. Generate & Run
```bash
cd /Volumes/MyDisk-aldy-uhaa/Projects-App/superisland-rebuild
xcodegen generate
open SuperIsland.xcodeproj
```
Pilih scheme `SuperIsland` → Run (⌘R).

Build DMG lokal (tanpa signing):
```bash
./scripts/build-dmg.sh
```

## Struktur Project Penting
- `SuperIsland/Modules/` → Battery, Calendar, NowPlaying, Weather, Notifications, dll
- `SuperIsland/Views/` → UI island
- `ExtensionHost/` + `Extensions/` → sistem extension (JS)
- `project.yml` → konfigurasi XcodeGen
- `scripts/` → build & release

## Cara Narik Update dari Repo Original (kalau kreator push lagi)
```bash
git fetch upstream
git merge upstream/main
```

## Ide Fitur Lanjutan (TODO dari repo original)
- Custom home screen (user bisa pilih 2 item lain dari Settings)
- Tray icon top-left untuk drag file / Airdrop shelf
- Lihat `TODO.md` untuk list lengkap

## Lisensi
Cek `LICENSE` / `README` di repo original sebelum publish ulang. Tetap cantumkan credit ke shobhit99.
