# Ayo Belajar dengan Mas Primus

Aplikasi chatbot berbasis Retrieval-Augmented Generation (RAG) untuk membantu pengguna mempelajari metode pembelajaran matematika, analisis, dan statistika. Jawaban chatbot diambil dari dokumen sumber yang telah disiapkan, bukan dari pencarian internet.

## Struktur Proyek

```
.
├── app.py                # Antarmuka Streamlit
├── rag_chatbot.py        # Logika RAG (model, vector store, chain)
├── requirements.txt      # Daftar pustaka Python yang dibutuhkan
├── .env                  # Berkas konfigurasi kunci API (tidak diunggah ke repo)
├── knowledge/            # Dokumen sumber materi matematika (KNOWLEDGE_DIR)
└── system_prompt.txt     # Berkas system prompt (SYSTEM_PROMPT_PATH)
```

Nama dan lokasi berkas `knowledge/` serta `system_prompt.txt` mengikuti nilai `KNOWLEDGE_DIR` dan `SYSTEM_PROMPT_PATH` yang didefinisikan pada `rag_chatbot.py`. Sesuaikan struktur di atas apabila nilai tersebut berbeda pada implementasi Anda.

## Persyaratan

- Python 3.10 atau lebih baru
- Kunci API Groq (`GROQ_API_KEY`)
- Pustaka Python sesuai `requirements.txt`, termasuk Streamlit dan `python-dotenv`, ditambah pustaka yang digunakan pada `rag_chatbot.py` (model bahasa, vector store, dan embedding)

## Langkah Instalasi

1. Salin proyek ke komputer lokal.

   ```bash
   git clone <url-repository>
   cd <nama-folder-proyek>
   ```

2. Buat dan aktifkan virtual environment.

   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

3. Pasang seluruh dependensi.

   ```bash
   pip install -r requirements.txt
   ```

4. Buat berkas `.env` di direktori utama, kemudian isi dengan kunci API Groq.

   ```
   GROQ_API_KEY=isi_dengan_kunci_api_anda
   ```

5. Siapkan dokumen sumber materi matematika, analisis, dan statistika, lalu simpan pada direktori yang sesuai dengan nilai `KNOWLEDGE_DIR`.

6. Siapkan berkas system prompt sesuai nilai `SYSTEM_PROMPT_PATH`.

## Menjalankan Aplikasi

Jalankan perintah berikut dari direktori utama proyek:

```bash
streamlit run app.py
```

Aplikasi akan terbuka pada peramban dengan alamat default `http://localhost:8501`.

## Menjalankan di Streamlit Cloud

1. Unggah proyek ke repositori GitHub.
2. Hubungkan repositori tersebut pada Streamlit Cloud.
3. Buka menu **Secrets** pada pengaturan aplikasi, kemudian tambahkan:

   ```
   GROQ_API_KEY = "isi_dengan_kunci_api_anda"
   ```

4. Pastikan direktori `knowledge/` dan berkas system prompt turut disertakan dalam repositori.

## Catatan Penggunaan

- Tombol "Mulai sesi belajar baru" pada sidebar akan menghapus riwayat percakapan yang sedang berjalan.
- Proses pemuatan dokumen dan pembuatan vector store hanya berjalan satu kali per sesi server berkat `st.cache_resource`. Jika dokumen sumber diperbarui, hentikan dan jalankan ulang aplikasi agar perubahan terbaca.
- Cakupan jawaban chatbot terbatas pada isi dokumen di `KNOWLEDGE_DIR`. Pertanyaan di luar cakupan materi kemungkinan tidak akan terjawab dengan akurat.