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
2. **Anti-False-Positive (Wajib Verifikasi Multi-FPS):**
   - **Tahap 1 (Overview Scan):** Ekstrak grid seluruh durasi video dengan `fps=1/2` (1 frame tiap 2 detik) untuk memetakan seluruh alur kedatangan user, penerimaan, penyajian air/snack, penyerahan dokumen/HP, dan perpisahan.
   - **Tahap 2 (High-Speed Verification — `10 fps`):** Untuk setiap kandidat pelanggaran interaksi cepat—khususnya **`A2` (Air/Snack)** dan **`C3` (Serah-Terima 2 Tangan)**—**DILARANG** menyimpulkan pelanggaran hanya dari grid 2 detik atau `2 fps`. Wajib ekstrak grid close-up pada **`10 fps` (setiap `0,1` detik)** mulai dari **2 detik SEBELUM kontak hingga 2 detik SESUDAH kontak** untuk memastikan:
     - **Arah Serah-Terima (*Direction of Transfer*):** Siapa yang memegang objek di awal (apakah *User → Staf* atau *Staf → User*).
     - **Kontak Awal (*Initial Contact*):** Apakah kedua tangan staf menyentuh/memegang objek saat momen serah-terima. Jika staf sudah menyerahkan atau menerima dengan 2 tangan pada momen kontak, namun salah satu tangannya turun lebih dulu sepersekian detik saat user mengambil barang, itu **SESUAI SOP (bukan pelanggaran)**.
     - **A2 (Air/Snack):** Periksa apakah staf mengambil air/snack dari laci bawah meja atau nampan dan menawarkannya kepada user (meskipun user menolak dan staf menaruhnya kembali ke laci). Jika sudah ditawarkan, maka **`A2` SESUAI SOP**.
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
  - Catat sebagai pelanggaran jika user bangkit meninggalkan meja resepsionis tetapi staf tetap duduk dan tidak berdiri sama sekali.
- **`B1` s/d `B5` — High-Frequency Complaint Problems (Inspeksi fisik HP, konfirmasi data/harga/garansi):**
  - **SKIP** untuk audit berbasis CCTV.
- **`C1` & `C2` — Grooming & Attitude:**
  - Pakaian rapi, kartu nama (*name tag*), rambut rapi, tidak berdebat dengan user.
- **`C3` — Two-Handed Service Posture (Serah-Terima 2 Tangan):**
  - Saat menerima HP/dokumen dari user atau menyerahkan HP/dokumen/pena kepada user, staf wajib menggunakan **2 tangan**.
  - **Wajib cek dengan `10 fps`** (2 detik sebelum s/d 2 detik sesudah kontak). Catat sebagai pelanggaran hanya jika dari awal hingga akhir serah-terima staf benar-benar hanya menggunakan 1 tangan sementara tangan satunya diam di meja/mouse/saku.
- **`C4` (Duplikat `C5` digabung jadi 1x penilaian di `C4`) — Postur Santai/Malas Saat Ada User:**
  - Saat ada user di Service Center, staf tidak boleh melipat tangan di dada, bertopang dagu, bersandar malas, atau tiduran di meja selama **> 30 detik**, serta tidak boleh bermain HP/menonton video/bermain game yang tidak terkait pekerjaan.
- **`D1` — Handover Report (Formulir Serah-Terima & Tanda Tangan User):**
  - Mencetak formulir tanda terima (*handover report*) dan menyerahkannya kepada user untuk ditandatangani.

### B. Kategori `6S` (Standarisasi Cabang — Dicatat Jika Terlihat di CCTV)
- **`6S No. 2` — Seragam & Jas Anti-Statik:**
  - **ATURAN PENTING:** Baju kaos berwarna **krem / *beige*** adalah **seragam resmi OPPO saat ini (SESUAI SOP, BUKAN pelanggaran)**.
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
  1. Ekstrak frame Full-HD (`1920x1080`) yang bersih (gunakan filter `trim=start=<detik>:duration=0.2,setpts=PTS-STARTPTS` pada `ffmpeg` agar tidak terkena artefak I-frame HEVC abu-abu).
  2. Gambar **kotak merah tebal (`width=5`)** yang melingkari/mengotaki area pelanggaran, tambahkan **label teks berlatar merah** di dekat kotak, serta **banner bawah berlatar hitam** berisi `Kode Cabang | Kode SOP | Penjelasan Singkat | Timestamp`.
  3. Unggah gambar ke Google Drive menggunakan `gdrive mutate upload <path>` lalu pindahkan file gambar tersebut ke dalam **folder Google Drive cabang yang bersangkutan** menggunakan `gdrive mutate mv <FILE_ID> <BRANCH_FOLDER_ID>` agar otomatis mewarisi izin akses `anyoneWithLink`.
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
