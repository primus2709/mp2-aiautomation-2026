# 📐 Primus EduMath Indonesia

**Asisten Pembelajaran Matematika di Indonesia** — sebuah AI Learning Assistant berbasis *Retrieval-Augmented Generation* (RAG) yang dibangun dengan Streamlit. Aplikasi ini menjawab pertanyaan seputar matematika hanya berdasarkan dokumen sumber yang tersedia, bukan dari internet secara bebas.

---

## 📋 Daftar Isi

1. [Ringkasan Aplikasi](#-ringkasan-aplikasi)
2. [Fitur Utama](#-fitur-utama)
3. [Tumpukan Teknologi](#-tumpukan-teknologi)
4. [Struktur Proyek](#-struktur-proyek)
5. [Prasyarat](#-prasyarat)
6. [Instalasi & Menjalankan Secara Lokal](#-instalasi--menjalankan-secara-lokal)
7. [Konfigurasi Environment Variable](#-konfigurasi-environment-variable)
8. [Menyiapkan Dokumen Sumber (Knowledge Base)](#-menyiapkan-dokumen-sumber-knowledge-base)
9. [Tema Visual (`.streamlit/config.toml`)](#-tema-visual-streamlitconfigtoml)
10. [Halaman & Navigasi](#-halaman--navigasi)
11. [Cara Kerja RAG di Balik Layar](#-cara-kerja-rag-di-balik-layar)
12. [Alur State & Session Streamlit](#-alur-state--session-streamlit)
13. [Deployment ke Streamlit Community Cloud](#-deployment-ke-streamlit-community-cloud)
14. [Troubleshooting](#-troubleshooting)

---

## 🧮 Ringkasan Aplikasi

Primus EduMath Indonesia adalah teman belajar berbasis AI yang membantu memahami konsep dan informasi matematika berdasarkan dokumen sumber yang sudah disiapkan sebelumnya. Pengguna dapat:

- Bertanya bebas lewat chat, atau memilih pertanyaan contoh yang sudah disediakan.
- Menjelajahi kategori materi (Pembelajaran, Konsep Matematika, Pendidikan) dan melihat daftar dokumen sumber yang menjadi rujukan.
- Mendapatkan jawaban yang di-*streaming* secara real-time, disusun oleh model AI hanya dari potongan dokumen yang relevan (bukan dikarang).

## ✨ Fitur Utama

| Fitur | Penjelasan |
|---|---|
| **Chat interaktif** | Streaming jawaban real-time dengan `st.chat_message` + `st.write_stream`. |
| **Welcome screen** | Learning card yang benar-benar mengisi pertanyaan ke chat saat diklik, bukan sekadar dekorasi. |
| **Contoh Pertanyaan** | Dikelompokkan per kategori, satu klik langsung mengirim ke chatbot. |
| **Materi** | Menampilkan kategori belajar + daftar dokumen sumber yang dibaca langsung dari folder pengetahuan backend. |
| **Reset percakapan** | Tombol "Percakapan Baru" di sidebar *dan* di header chat (untuk pengguna mobile yang sidebar-nya tersembunyi). |
| **Lazy initialization** | Model, vector store, dan embedding baru dibangun saat pertanyaan pertama dikirim — bukan saat aplikasi dibuka. |
| **Error handling manusiawi** | Kegagalan backend ditampilkan sebagai pesan yang ramah, bukan traceback teknis. |
| **Aksesibilitas** | Focus ring untuk navigasi keyboard, serta menghormati preferensi `prefers-reduced-motion`. |
| **Responsif** | Menyesuaikan diri di desktop, tablet, dan mobile. |

## 🛠️ Tumpukan Teknologi

- **[Streamlit](https://streamlit.io/)** — antarmuka aplikasi.
- **[LangChain](https://www.langchain.com/)** — orkestrasi RAG (retriever + chain).
- **[ChromaDB](https://www.trychroma.com/)** — vector database untuk penyimpanan embedding dokumen.
- **[Groq](https://groq.com/)** — penyedia model LLM yang digunakan untuk menyusun jawaban.
- **python-dotenv** — memuat variabel environment dari file `.env` saat pengembangan lokal.

> Detail implementasi RAG (pemuatan dokumen, pembuatan vector store, dan chain) berada di modul backend `rag_chatbot.py` yang sudah Anda miliki sebelumnya dan **tidak diubah** oleh redesain UI ini — `app.py` hanya mengonsumsi fungsi-fungsi yang diekspornya.

## 📁 Struktur Proyek

Struktur berikut mengasumsikan tata letak proyek yang umum untuk kontrak yang dipakai `app.py`. Sesuaikan nama file/folder dengan apa yang sudah Anda gunakan di `rag_chatbot.py`:

```
primus-edumath-indonesia/
├── app.py                     # Antarmuka Streamlit (UI/UX) — file utama yang dijalankan
├── rag_chatbot.py             # Modul backend RAG (buat_model, muat_dokumen, dst.) — TIDAK diubah
├── requirements.txt           # Daftar dependency Python
├── .env                       # GROQ_API_KEY (jangan di-commit ke Git)
├── .streamlit/
│   └── config.toml            # Tema warna aplikasi
├── knowledge_base/            # Folder dokumen sumber yang dipakai RAG (nama sesuai KNOWLEDGE_DIR)
│   ├── dokumen-1.pdf
│   └── dokumen-2.txt
└── system_prompt.txt          # Isi system prompt untuk model (sesuai SYSTEM_PROMPT_PATH)
```

`app.py` mengimpor kontrak berikut dari `rag_chatbot.py` — pastikan modul tersebut menyediakannya:

```python
from rag_chatbot import (
    KNOWLEDGE_DIR,        # path folder dokumen sumber
    SYSTEM_PROMPT_PATH,   # path file system prompt
    TOP_K,                # jumlah dokumen relevan yang diambil retriever
    buat_model,           # -> mengembalikan instance model Groq
    muat_dokumen,         # (folder) -> daftar dokumen yang sudah di-load
    bangun_vectorstore,   # (dokumen) -> instance ChromaDB vector store
    muat_system_prompt,   # (path) -> teks system prompt
    buat_rag_chain,       # (retriever, model, system_prompt) -> chain siap distream
)
```

## ✅ Prasyarat

- **Python 3.10+** (disarankan 3.11).
- **Akun Groq** dan API key aktif — daftar di [console.groq.com](https://console.groq.com/).
- Dokumen sumber matematika yang ingin dijadikan basis pengetahuan (PDF/teks).
- Git (opsional, untuk deployment ke Streamlit Cloud).

## 🚀 Instalasi & Menjalankan Secara Lokal

**1. Clone atau salin proyek**

```bash
git clone <url-repo-anda>
cd primus-edumath-indonesia
```

**2. Buat virtual environment**

```bash
python -m venv venv

# Aktifkan (Windows)
venv\Scripts\activate

# Aktifkan (macOS/Linux)
source venv/bin/activate
```

**3. Pasang dependency**

Jika belum punya `requirements.txt`, buat dengan isi minimal berikut lalu sesuaikan dengan yang benar-benar dipakai `rag_chatbot.py`:

```
streamlit>=1.38
python-dotenv>=1.0
langchain>=0.3
langchain-groq
langchain-chroma
chromadb
```

Lalu pasang:

```bash
pip install -r requirements.txt
```

**4. Siapkan file `.env`**

```
GROQ_API_KEY=isi_dengan_api_key_groq_anda
```

**5. Jalankan aplikasi**

```bash
streamlit run app.py
```

Aplikasi akan terbuka otomatis di browser pada `http://localhost:8501`.

## 🔐 Konfigurasi Environment Variable

| Variabel | Wajib | Keterangan |
|---|---|---|
| `GROQ_API_KEY` | ✅ | Dibaca lewat `.env` (lokal) atau menu **Secrets** (Streamlit Cloud). Tanpa ini, `app.py` akan menghentikan eksekusi (`st.stop()`) dan menampilkan pesan error yang jelas. |

`KNOWLEDGE_DIR`, `SYSTEM_PROMPT_PATH`, dan `TOP_K` **bukan** environment variable — ketiganya adalah konstanta yang didefinisikan langsung di `rag_chatbot.py` dan diimpor oleh `app.py`.

## 📚 Menyiapkan Dokumen Sumber (Knowledge Base)

1. Masukkan dokumen (PDF, teks, dsb.) ke dalam folder yang ditunjuk oleh `KNOWLEDGE_DIR`.
2. Saat pertanyaan pertama dikirim, `muat_dokumen()` akan membaca isi folder tersebut dan `bangun_vectorstore()` akan meng-index-nya ke ChromaDB — proses ini di-cache (`@st.cache_resource`) sehingga hanya berjalan sekali per sesi server.
3. Halaman **📚 Materi** secara otomatis menampilkan daftar file yang ada di `KNOWLEDGE_DIR` — jika Anda menambah/menghapus dokumen, restart aplikasi (atau jalankan ulang deployment) agar index dibangun ulang dan daftar di halaman Materi ikut ter-update.

> Jika folder `KNOWLEDGE_DIR` kosong atau belum dibuat, halaman Materi akan menampilkan info yang jujur ("belum ditemukan"), bukan data karangan.

## 🎨 Tema Visual (`.streamlit/config.toml`)

Palet warna (navy `#1F3A5F` + emas `#D9A62E`) sebagian besar diatur lewat CSS kustom di dalam `app.py`, tetapi widget bawaan Streamlit (kode blok, info box, dsb.) mengikuti tema di `.streamlit/config.toml`:

```toml
[theme]
base = "light"
primaryColor = "#D9A62E"
backgroundColor = "#F5F6F2"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#1B2230"
font = "sans serif"
```

Letakkan file ini di `.streamlit/config.toml` (folder tersembunyi sejajar dengan `app.py`).

## 🧭 Halaman & Navigasi

| Halaman | Ikon | Fungsi |
|---|---|---|
| **Beranda** | 🏠 | Welcome screen — hero, learning card interaktif, quick questions. |
| **Percakapan** | 💬 | Area chat utama. Menampilkan empty state jika belum ada riwayat, atau histori + input jika sudah. |
| **Materi** | 📚 | Kategori belajar + daftar dokumen sumber (dinamis dari `KNOWLEDGE_DIR`). |
| **Contoh Pertanyaan** | 💡 | Pertanyaan siap pakai, dikelompokkan per kategori, sekali klik langsung terkirim ke chat. |
| **Tentang** | ℹ️ | Penjelasan singkat tentang aplikasi dan pendekatan RAG yang dipakai. |

Setiap item navigasi mengubah `st.session_state.tampilan_aktif`, yang lalu dipetakan lewat dictionary `_HALAMAN` ke fungsi `render_*()` yang sesuai — tidak ada menu yang hanya dekoratif.

## ⚙️ Cara Kerja RAG di Balik Layar

```
Pertanyaan pengguna
        │
        ▼
retriever.get_relevant_documents()   ← mencari potongan dokumen paling relevan (TOP_K)
        │
        ▼
rag_chain (system_prompt + konteks + pertanyaan)
        │
        ▼
rag_chain.stream()  →  st.write_stream()   ← jawaban muncul kata demi kata
```

Model, dokumen, vector store, dan chain hanya dibangun **sekali** lewat `siapkan_chatbot()` yang dibungkus `@st.cache_resource`, dan baru dipanggil saat pertanyaan pertama benar-benar dikirim (bukan saat halaman pertama kali dibuka) — sehingga sidebar dan Beranda langsung tampil tanpa jeda loading.

## 🔄 Alur State & Session Streamlit

Tiga variabel `session_state` menjaga seluruh alur aplikasi:

- **`riwayat`** — daftar pasangan pesan user/assistant di sesi berjalan.
- **`tampilan_aktif`** — halaman yang sedang dibuka (`beranda`, `percakapan`, `materi`, `contoh`, `tentang`).
- **`pertanyaan_tertunda`** — jembatan saat pengguna mengklik card/tombol contoh: pertanyaan disimpan di sini, halaman berpindah ke Percakapan, lalu diproses otomatis pada render berikutnya (tanpa perlu klik dua kali).

Menekan **🗑️ Percakapan Baru** (di sidebar maupun header chat) mengosongkan `riwayat`, membatalkan `pertanyaan_tertunda`, dan mengembalikan `tampilan_aktif` ke `beranda`.

## ☁️ Deployment ke Streamlit Community Cloud

1. Push seluruh proyek (kecuali `.env` dan `venv/`) ke repository GitHub.
2. Buat file `.gitignore` yang mengecualikan `.env`, `venv/`, `__pycache__/`, dan folder database Chroma jika disimpan lokal.
3. Buka [share.streamlit.io](https://share.streamlit.io/), pilih **New app**, arahkan ke repo dan `app.py`.
4. Di menu **Secrets**, tambahkan:
   ```toml
   GROQ_API_KEY = "isi_dengan_api_key_anda"
   ```
5. Deploy. `load_dotenv()` di `app.py` tidak akan menemukan file `.env` di Streamlit Cloud — namun itu tidak masalah, karena `os.getenv("GROQ_API_KEY")` akan otomatis membaca dari Secrets tanpa perubahan kode apa pun.

## 🩹 Troubleshooting

| Gejala | Kemungkinan Penyebab | Solusi |
|---|---|---|
| `GROQ_API_KEY belum diisi` | File `.env` tidak ada/salah nama variabel, atau Secrets belum diisi di Cloud. | Cek ejaan `GROQ_API_KEY`, pastikan file `.env` sejajar dengan `app.py`. |
| Halaman Materi menampilkan "Daftar dokumen sumber belum ditemukan" | `KNOWLEDGE_DIR` kosong atau path salah. | Pastikan dokumen benar-benar ada di folder yang ditunjuk `KNOWLEDGE_DIR` di `rag_chatbot.py`. |
| Muncul pesan "Maaf, terjadi kendala saat memproses pertanyaan" | Ada exception di `rag_chain.stream()` (mis. API key invalid, kuota Groq habis, format dokumen tidak didukung). | Jalankan lokal dengan `st.exception()` sementara untuk melihat traceback asli saat debugging, lalu hapus lagi sebelum deploy. |
| Aplikasi lambat saat pertanyaan pertama | Ini normal — vector store & model baru dibangun sekali di sini (lazy init). Pertanyaan berikutnya akan jauh lebih cepat. | Tidak perlu tindakan; jika ingin mempercepat, kurangi jumlah/ukuran dokumen atau gunakan model embedding yang lebih ringan. |
| Riwayat chat hilang saat pindah halaman | Seharusnya tidak terjadi — riwayat disimpan di `session_state`. | Pastikan tidak ada kode tambahan yang me-reset `session_state.riwayat` di luar `mulai_percakapan_baru()`. |

---

*Dibangun dengan Streamlit, LangChain, ChromaDB, dan Groq.*
