# OPPO Indonesia Service Center (SST) — Agent Audit CCTV Otomatis

Repository ini berisi **Custom Skill (`SKILL.md`)**, **Master Prompt (`MASTER_PROMPT.md`)**, **File SOP Resmi (`Marking Sheets - ID.xlsx`)**, serta **Script Otomatisasi (`scripts/audit_helper.py`)** untuk menjalankan **Agent Audit Standarisasi Operasional (6S & Onsite Reception)** dari rekaman CCTV Google Drive ke laporan Google Sheet secara otomatis.

---

## Cara Menggunakan (Untuk Anggota Tim / Pengguna Baru)

Karena percakapan (*chat*) AI bersifat privat untuk masing-masing akun, anggota tim lain dapat menjalankan Agent Audit yang sama persis dengan **2 cara mudah**:

### Cara 1: Menghubungkan Repository GitHub Ini (Direkomendasikan)
1. Buka **Antigravity** di akun masing-masing.
2. Pastikan plugin **Google Drive (`gdrive`)** dan **Google Sheets (`gsheets`)** sudah terhubung (*Connected*).
3. Pilih repository **`chikenbai/oppo-cctv-audit-agent`** sebagai workspace (atau berikan link repo ini di chat https://github.com/chikenbai/oppo-cctv-audit-agent.git).
4. Pada chat pertama, ketik:
   > *"Baca file `SKILL.md` di repository ini lalu simpan sebagai custom skill `oppo-cctv-audit`."*
5. Setelah skill tersimpan sekali, setiap hari Anda cukup mengetik perintah singkat:
   > *"Gunakan skill `oppo-cctv-audit` untuk memeriksa semua CCTV di folder Google Drive [LINK_DRIVE] dan catat temuannya ke Google Sheet [LINK_SHEET] pada periode [First Half / Second Half]."*

### Cara 2: Copy-Paste Tanpa GitHub
Jika pengguna tidak menghubungkan GitHub, cukup buka file [`MASTER_PROMPT.md`](./MASTER_PROMPT.md), salin (*copy*) isinya ke dalam chat baru, lalu ganti bagian `[LINK_FOLDER_GOOGLE_DRIVE]` dan `[LINK_GOOGLE_SHEET]`.

---

## Struktur Repository

- [`SKILL.md`](./SKILL.md) — Definisi lengkap Custom Skill `oppo-cctv-audit` (SOP, aturan pengecualian terbaru, protokol verifikasi `10 fps`, dan format laporan).
- [`MASTER_PROMPT.md`](./MASTER_PROMPT.md) — Template prompt siap *copy-paste* untuk menjalankan audit harian.
- [`Marking Sheets - ID.xlsx`](./Marking%20Sheets%20-%20ID.xlsx) — File Excel SOP resmi (`6S CN`, `6S ENG`, `6S ID`, dan `Onsite ENG`).
- [`scripts/audit_helper.py`](./scripts/audit_helper.py) — Script utilitas Python untuk mengekstrak grid video (`fps=1/2` & `10 fps`), menggambar kotak merah anotasi pelanggaran, mengunggah screenshot ke folder cabang di Google Drive, dan menulis baris laporan dwibahasa (Indonesia & Mandarin) ke Google Sheet.

---

## Cara Merevisi Aturan SOP ke Depannya

Jika di kemudian hari ada perubahan aturan dari manajemen:
1. Anda cukup mengatakan kepada Agent di chat:
   > *"Tolong update skill `oppo-cctv-audit` dan push juga perubahannya ke repo GitHub `oppo-cctv-audit-agent`: mulai sekarang aturan [X] diubah menjadi [Y]."*
2. Agent akan otomatis memperbarui *Custom Skill* di akun Anda sekaligus memperbarui file `SKILL.md` dan `MASTER_PROMPT.md` di GitHub ini agar seluruh anggota tim mendapatkan aturan terbaru.
