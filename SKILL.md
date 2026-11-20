---
name: oppo-cctv-audit
description: Audit rekaman CCTV cabang OPPO Indonesia Service Center (SST) dari Google Drive terhadap SOP 6S dan Onsite Reception (Marking Sheets - ID), buat screenshot beranotasi kotak merah, unggah ke Google Drive, dan catat temuan dwibahasa (Indonesia & Mandarin) ke Google Sheet laporan.
---

# OPPO Indonesia Service Center (SST) — CCTV Operational Standardization Audit Skill

Gunakan skill ini setiap kali pengguna meminta pemeriksaan/audit rekaman CCTV Service Center OPPO dari Google Drive dan pencatatan hasilnya ke Google Sheet.

---

## 0. Aturan Sinkronisasi Otomatis Saat Ada Revisi SOP (Wajib)
Setiap kali pengguna meminta revisi atau tambahan aturan SOP, Agent WAJIB memperbarui kedua tempat ini secara bersamaan: (1) Custom Skill `oppo-cctv-audit` di Antigravity (`update_skill`), dan (2) Repo GitHub `chikenbai/oppo-cctv-audit-agent` (`SKILL.md`, `MASTER_PROMPT.md`, & `README.md`). **Jangan** mengunggah atau menyimpan file skill/prompt ke Google Drive.

1. **Update Custom Skill (`oppo-cctv-audit`):** Segera perbarui skill `oppo-cctv-audit` agar perubahan tersimpan permanen di akun Antigravity pengguna.
2. **Update GitHub Repository (`chikenbai/oppo-cctv-audit-agent`):** Segera perbarui file `SKILL.md` dan `MASTER_PROMPT.md` di repo `chikenbai/oppo-cctv-audit-agent` lalu jalankan `git commit` dan `git push origin main` (atau via GitHub Contents API jika repo belum di-clone).

---

## 1. Prinsip & Batasan Utama
1. **Bukti Nyata (Strict Visual Evidence):** Nilai hanya tindakan yang benar-benar terlihat jelas di rekaman CCTV. Jangan menebak niat, percakapan, atau kejadian di luar kamera.
2. **Anti-False-Positive & Fast Multi-FPS Verification (Wajib Gunakan `audit_helper.py`):**
   - **Tahap 1 (Auto-Timestamped Overview Scan — `fps=1/2`):** Ekstrak contact sheet seluruh durasi video menggunakan `audit_helper.extract_overview_grids()` (`fps=1/2`, dengan *burned-in timestamp* `t=...s (HH:MM:SS)` pada setiap tile dan `-threads 0`) untuk memetakan secara presisi detik kedatangan user, penerimaan, penyajian air/snack, penyerahan dokumen/HP, dan perpisahan.
   - **Tahap 2 (High-Res `4x4` Close-Up Verification — DILARANG Pakai Grid `8x10` / `10x10`):**
     - **ATURAN RESOLUSI GRID:** Saat mengekstrak grid close-up verifikasi (`audit_helper.extract_10fps_verification_grid`), **WAJIB gunakan `tile='4x4'` (maksimal 16 frame per gambar, resolusi tiap kotak `450x400` = `1800x1600` total)**. **DILARANG KERAS** membuat grid `6x10`, `8x10`, atau `10x10` (60–100 frame dalam 1 gambar) karena sistem penglihatan AI akan mengecilkan gambar (*downscale*) sehingga gerakan tangan kosong di atas meja terlihat buram seperti serah-terima barang!
     - **Bukti Transfer Objek Fisik (`C3`):** Sebelum menyebut pelanggaran `C3`, **wajib pastikan ada objek fisik nyata (HP, formulir, pena, kotak) yang berpindah tangan antara User dan Staf** (pada awal aksi barang dipegang pihak A, dan pada akhir aksi barang dipegang pihak B). Gerakan tangan staf sendiri di meja (menggeser mouse, memberi stempel kertas sendiri, merapikan kertas di mejanya sendiri, atau gestur tangan berbicara tanpa menyentuh tangan/barang user) **BUKAN serah-terima (`C3`)**.
     - **Kontak Awal (*Initial Contact*):** Jika staf sudah menyerahkan atau menerima barang dengan 2 tangan pada momen kontak, namun salah satu tangannya turun lebih dulu sepersekian detik saat user mengambil barang, itu **SESUAI SOP (bukan pelanggaran)**.
     - **A2 (Air/Snack):** Periksa secara menyeluruh hingga akhir video penerimaan apakah staf mengambil air/snack (botol/gelas/nampan) dan memberikannya kepada user. Jangan terlewat momen singkat (1–2 detik) saat staf menaruh botol air di meja user.
3. **Kerahasiaan Data CCTV:** Simpan file video `.mp4` dan frame mentah sementara hanya di `/tmp/audit_<cabang>/` dan **wajib hapus (`rm -rf`)** segera setelah pemeriksaan cabang tersebut selesai.

---

## 2. Daftar SOP & Aturan Kalibrasi Lapangan (Wajib Diikuti)

### A. Kategori `Onsite Reception` (Fokus Utama CCTV)
- **`A1` — Greet & Welcome (Menyambut User):**
  - Saat user masuk/datang ke area resepsionis, staf yang sedang tidak melayani user wajib berdiri, tersenyum/memandang user, dan memberi isyarat mempersilakan duduk.
  - **Toleransi Lapangan:** Selama staf sudah berdiri menyambut user, selisih waktu duduk beberapa detik antara staf dan user (misalnya staf duduk 3–4 detik lebih dulu saat user sedang menarik kursi) **TIDAK MASALAH (jangan dicatat sebagai pelanggaran)**. Catat sebagai pelanggaran hanya jika staf yang menganggur **sama sekali tidak berdiri** saat user datang/menghampiri meja.
- **`A2` — Provide Water & Snacks (Menyajikan Air Minum & Camilan):**
  - Setelah user duduk di meja layanan, staf menyajikan/menawarkan air minum dan snack kepada user dengan 2 tangan.
  - **Toleransi Lapangan:** Jika staf sudah mengambil minuman/snack (termasuk dari laci meja) dan menawarkannya kepada user namun user menolak, itu **SESUAI SOP**.
- **`A3` — Farewell (Perpisahan / Mengarahkan ke Area Tunggu):**
  - Saat layanan selesai atau saat user bangkit dari meja resepsionis untuk pindah ke area tunggu (*rest area*), staf wajib berdiri untuk mengarahkan lokasi area tunggu atau mengucapkan salam perpisahan.
  - **ATURAN PENTING (`A3`):** Jika staf menunjuk arah ruang tunggu saat **user MASIH DUDUK**, lalu beberapa detik kemudian saat **user benar-benar berdiri meninggalkan kursi**, staf **ikut berdiri**, maka itu **SESUAI SOP (BUKAN pelanggaran)**. Selalu cek frame pada detik **saat user benar-benar berdiri dari kursi hingga berjalan pergi (+5 detik)**. Catat sebagai pelanggaran hanya jika saat user sudah berdiri dan melangkah pergi dari meja, staf tetap duduk dan tidak berdiri sama sekali.
- **`B1` s/d `B5` — High-Frequency Complaint Problems (Inspeksi fisik HP, konfirmasi data/harga/garansi):**
  - **SKIP** untuk audit berbasis CCTV.
- **`C1` & `C2` — Grooming & Attitude:**
  - Pakaian rapi, kartu nama (*name tag*), rambut rapi, tidak berdebat dengan user.
- **`C3` — Two-Handed Service Posture (Serah-Terima 2 Tangan):**
  - Saat menerima HP/dokumen dari user atau menyerahkan HP/dokumen/pena kepada user, staf wajib menggunakan **2 tangan**.
  - **Wajib cek dengan grid `4x4` resolusi tinggi (`450x400` per tile)**. Pastikan benar-benar terjadi perpindahan barang antara tangan staf dan tangan user (bukan staf memindahkan kertas/stempel/mouse di mejanya sendiri). Catat sebagai pelanggaran hanya jika dari awal hingga akhir serah-terima barang dengan user, staf benar-benar hanya menggunakan 1 tangan sementara tangan satunya diam di meja/mouse/keyboard/saku.
- **`C4` (Duplikat `C5` digabung jadi 1x penilaian di `C4`) — Postur Santai/Malas Saat Ada User:**
  - Saat ada user di Service Center, staf tidak boleh melipat tangan di dada, bertopang dagu, bersandar malas, atau tiduran di meja selama **> 30 detik**, serta tidak boleh bermain HP/menonton video/bermain game yang tidak terkait pekerjaan.
- **`D1` — Handover Report (Formulir Serah-Terima & Tanda Tangan User):**
  - Mencetak formulir tanda terima (*handover report*) dan menyerahkannya kepada user untuk ditandatangani.

### B. Kategori `6S` (Standarisasi Cabang — Dicatat Jika Terlihat di CCTV)
- **`6S No. 2` — Seragam & Jas Anti-Statik:**
  - **ATURAN PENTING:** Baju kaos berwarna **krem / *beige*** adalah **seragam resmi OPPO saat ini (SESUAI SOP, BUKAN pelanggaran)**. Catat sebagai pelanggaran hanya jika staf memakai pakaian bebas/kaos non-seragam (misalnya kaos hitam polos biasa).
  - **Jas Anti-Statik (*Anti-static coat*):** Saat ini **sudah tidak wajib digunakan (SKIP)**.
- **`6S No. 17` — Kerapian Meja Resepsionis:**
  - Meja penerimaan pelanggan harus bersih dan rapi, tidak boleh ada tumpukan kardus/barang berantakan yang tidak seharusnya di atas meja resepsionis atau di atas printer samping meja.
- **`6S No. 18` — Meninggalkan Meja Resepsionis Tanpa Papan "CLOSED" (`暂停服务`):**
  - **ATURAN PENTING:**
    1. Jika staf meninggalkan meja karena **sedang dalam proses melayani user** (misalnya mengambil unit/sparepart/dokumen untuk user yang sedang dilayani), **TIDAK PERLU** membalikkan papan *CLOSED* (bukan pelanggaran).
    2. Batas toleransi waktu meninggalkan meja kosong tanpa papan *CLOSED* adalah **10 menit**. Jika meninggalkan meja **di bawah 10 menit**, tidak masalah jika tidak membalikkan papan.
- **`6S No. 60–62` — Mesin Antrean (*Queuing Machine*):**
  - **SKIP** (Service Center sudah tidak menggunakan mesin nomor antrean).

---

## 3. Format Pencatatan ke Google Sheet Laporan

- **1 Baris = 1 Masalah (1 Temuan):** Jika 1 cabang memiliki 2 masalah, tulis menjadi 2 baris terpisah. Jika 1 cabang tidak memiliki pelanggaran, tidak perlu ditulis di daftar kesalahan.
- **Pemisahan Bagian di Sheet:**
  - Temuan `6S` ditulis pada blok **`6s`** -> **`上半月 first half month`** (atau `下半月 second half month` sesuai periode folder Drive).
  - Temuan `Onsite Reception` ditulis pada blok **`Onsite Reception`** -> **`上半月 first half month`** (atau `下半月 second half month` sesuai periode folder Drive).
  - Jika jumlah baris yang tersedia di blok tersebut penuh, gunakan `gsheets mutate insert-rows` sebelum baris `下半月 second half month`.
- **Kolom C (`门店代码 SC code`):** Kode beserta nama cabang, contoh: `ID003006 - SC Jambi`.
- **Kolom D (`不合格项照片 failed items photo`):**
  1. Ekstrak frame Full-HD (`1920x1080`) yang bersih menggunakan `audit_helper.extract_clean_frame()` (*pre-seek* `-ss <detik-4>` sebelum `-i` + `-vf trim=start=4:duration=0.2,setpts=PTS-STARTPTS` agar cepat dan bebas artefak I-frame HEVC abu-abu).
  2. Gambar **kotak merah tebal (`width=5`)** yang melingkari/mengotaki area pelanggaran, tambahkan **label teks berlatar merah** di dekat kotak, serta **banner bawah berlatar hitam** berisi `Kode Cabang | Kode SOP | Penjelasan Singkat | Timestamp` menggunakan `audit_helper.annotate_violation()`.
  3. Unggah gambar langsung ke dalam **folder Google Drive cabang yang bersangkutan** dalam 1 langkah menggunakan `gdrive mutate upload <path> --parent <BRANCH_FOLDER_ID>` (`audit_helper.upload_to_branch_folder()`) agar otomatis mewarisi izin akses `anyoneWithLink`.
  4. Tulis rumus berikut di Kolom D:
     `=IMAGE("https://drive.google.com/thumbnail?id=<FILE_ID>&sz=w1000")`
- **Kolom E (`不合格项文字描述 Description of the unqualified item`):**
  Wajib menggunakan **2 bahasa (Bahasa Indonesia & Bahasa Mandarin)** dalam 1 sel (dipisahkan newline `\n`), dengan menyertakan kode SOP, nama video, dan timestamp CCTV:
  ```text
  [<Kode SOP> - <Kategori> | <Nama Video> <Menit:Detik> / CCTV <HH:MM:SS>]
  Cabang <Nama SC>: <Deskripsi faktual pelanggaran dalam Bahasa Indonesia>.
  <Nama SC>服务中心：<Deskripsi faktual pelanggaran dalam Bahasa Mandarin>。
  ```
- **Gunakan `gsheets mutate batch`** dengan file JSON (`{"op": "write", "range": "...", "data": [[...]]}`) saat menulis ke Google Sheet agar karakter koma `,` dan baris baru `\n` di dalam Kolom E tidak terpotong menjadi kolom/baris baru.
- Atur tinggi baris (`pixelSize: 160`) dan aktifkan `--wrap` agar foto dan teks dwibahasa tampil rapi.
