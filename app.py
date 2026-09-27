import os
import random

import streamlit as st
from dotenv import load_dotenv

from rag_chatbot import (
    KNOWLEDGE_DIR,
    SYSTEM_PROMPT_PATH,
    TOP_K,
    buat_model,
    muat_dokumen,
    bangun_vectorstore,
    muat_system_prompt,
    buat_rag_chain,
)


# ============================================================
# 1. PENGATURAN HALAMAN
# ============================================================
# Wajib jadi perintah Streamlit pertama: judul tab browser dan ikonnya.

st.set_page_config(
    page_title="Ayo Belajar dengan Mas Primus",
    page_icon=":material/calculate:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 1b. GAYA TAMPILAN
# ============================================================
# Tema "papan tulis & buku kotak-kotak" biar suasananya berasa kelas
# matematika, bukan cuma warna-warni generik.

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* --- Papan tulis di bagian atas halaman --- */
    .primus-hero {
        position: relative;
        overflow: hidden;
        padding: 2.4rem 2.2rem 2rem 2.2rem;
        border-radius: 4px;
        background:
            repeating-linear-gradient(
                0deg, rgba(255,255,255,0.05) 0px, rgba(255,255,255,0.05) 1px,
                transparent 1px, transparent 28px
            ),
            repeating-linear-gradient(
                90deg, rgba(255,255,255,0.05) 0px, rgba(255,255,255,0.05) 1px,
                transparent 1px, transparent 28px
            ),
            #1f3a3d;
        border-bottom: 3px solid #d4a24c;
        color: #f5f1e6;
        margin-bottom: 1.4rem;
    }
    .primus-hero .watermark {
        position: absolute;
        top: -38px;
        right: 12px;
        font-size: 9rem;
        font-family: 'Lora', serif;
        color: #f5f1e6;
        opacity: 0.08;
        transform: rotate(-8deg);
        pointer-events: none;
        user-select: none;
    }
    .primus-hero h1 {
        font-family: 'Lora', serif;
        margin: 0;
        font-size: 2.15rem;
        font-weight: 700;
        color: #f5f1e6;
    }
    .primus-hero p {
        margin-top: 0.5rem;
        font-size: 1.02rem;
        color: #cfe3df;
        max-width: 46ch;
    }

    /* --- Daftar topik di sidebar: gaya catatan pinggir buku --- */
    .topic-item {
        border-left: 3px solid #d4a24c;
        padding: 0.35rem 0 0.35rem 0.7rem;
        margin-bottom: 0.35rem;
        font-size: 0.93rem;
        color: inherit;
    }

    /* --- Catatan fakta: gaya sobekan kertas catatan --- */
    .fun-fact {
        border-left: 3px dashed #d4a24c;
        padding: 0.5rem 0 0.5rem 0.7rem;
        margin-top: 0.9rem;
        font-family: 'Lora', serif;
        font-style: italic;
        font-size: 0.9rem;
    }

    .stButton>button {
        border: 1px solid #3f8ea8;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 2. CEK API KEY
# ============================================================
# Di laptop, GROQ_API_KEY dibaca dari file .env.
# Di Streamlit Cloud, GROQ_API_KEY diisi lewat menu Secrets, dan Streamlit
# otomatis menjadikannya environment variable. Jadi kode yang sama ini
# jalan di dua tempat tanpa perlu diubah.

load_dotenv()
if not os.getenv("GROQ_API_KEY"):
    st.error(
        "Mas Primus belum bisa mulai mengajar — GROQ_API_KEY belum diisi. "
        "Cek file .env (di laptop) atau menu Secrets (di Streamlit Cloud)."
    )
    st.stop()

# ============================================================
# 3. SIAPKAN MESIN CHATBOT (sekali saja, lalu disimpan)
# ============================================================
# Streamlit menjalankan ulang SELURUH file ini dari atas setiap kali
# pengguna berinteraksi (misalnya mengirim pertanyaan).
# @st.cache_resource membuat fungsi di bawah ini cukup dijalankan SEKALI.
# Hasilnya disimpan, lalu dipakai ulang, sehingga dokumen tidak dimuat
# ulang dan vector store tidak dibangun ulang di setiap pertanyaan.

@st.cache_resource(show_spinner="Mas Primus sedang menyiapkan buku dan rumusnya...")
def siapkan_chatbot():
    model = buat_model()
    dokumen = muat_dokumen(KNOWLEDGE_DIR)
    vectorstore = bangun_vectorstore(dokumen)
    retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})
    system_prompt = muat_system_prompt(SYSTEM_PROMPT_PATH)
    return buat_rag_chain(retriever, model, system_prompt)


rag_chain = siapkan_chatbot()


# ============================================================
# 4. BUKU CATATAN PERCAKAPAN
# ============================================================
# st.session_state adalah tempat menyimpan data yang tidak ikut hilang
# saat file ini dijalankan ulang. Di sini dipakai untuk mencatat riwayat
# percakapan: siapa yang bicara ("user" atau "assistant") dan isinya.
# Sama saja dengan menjaga percakapan terus muncul di atas chat baru

if "riwayat" not in st.session_state:
    st.session_state.riwayat = []

AVATAR_USER = "🙋"
AVATAR_ASISTEN = "🧑‍🏫"

FAKTA_MATEMATIKA = [
    "Angka nol pertama kali dipakai secara formal oleh matematikawan India sekitar abad ke-5.",
    "Kata \"statistik\" berasal dari kata Latin status, yang awalnya berarti mendata kondisi suatu negara.",
    "Bilangan pi (π) sudah dihitung hingga triliunan digit, meski 39 digit saja cukup untuk menghitung keliling alam semesta.",
    "Kurva distribusi normal disebut \"kurva lonceng\" karena bentuknya menyerupai lonceng.",
    "Konsep rata-rata (mean) sudah dipakai sejak zaman Babilonia kuno untuk keperluan astronomi.",
]

# ============================================================
# 5. TAMPILAN
# ============================================================

with st.sidebar:
    st.markdown("### Tentang Mas Primus")
    st.write(
        "Mas Primus adalah asisten belajar yang menjawab pertanyaan "
        "berdasarkan materi metode pembelajaran matematika, analisis, "
        "dan statistika yang sudah disiapkan."
    )
    st.caption("Jawaban hanya diambil dari dokumen sumber, bukan dari internet.")

    st.markdown("### Topik yang bisa ditanyakan")
    topik_list = [
        ("➕", "Aljabar & Persamaan"),
        ("📈", "Kalkulus & Limit"),
        ("📊", "Statistika & Analisis Data"),
        ("🎲", "Peluang"),
        ("📐", "Geometri"),
    ]
    for icon, nama in topik_list:
        st.markdown(
            f'<div class="topic-item">{icon}&nbsp;&nbsp;{nama}</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        f'<div class="fun-fact">Tahukah kamu? {random.choice(FAKTA_MATEMATIKA)}</div>',
        unsafe_allow_html=True,
    )

    st.write("")
    if st.button("Mulai sesi belajar baru", use_container_width=True):
        st.session_state.riwayat = []

st.markdown(
    """
    <div class="primus-hero">
        <div class="watermark">∑</div>
        <h1>Ayo Belajar dengan Mas Primus</h1>
        <p>Teman belajarmu untuk memahami metode pembelajaran matematika,
        analisis, dan statistika — langkah demi langkah.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Salam pembuka, selalu tampil paling atas.
with st.chat_message("assistant", avatar=AVATAR_ASISTEN):
    st.markdown(
        "Halo! Aku Mas Primus 👋 Yuk, tanya apa saja seputar metode "
        "pembelajaran matematika, analisis, atau statistika. Contoh: "
        "*Bagaimana cara menghitung rata-rata dan simpangan baku pada data kelompok?*"
    )

# Tampilkan ulang seluruh riwayat percakapan dari buku catatan.
for pesan in st.session_state.riwayat:
    avatar = AVATAR_USER if pesan["role"] == "user" else AVATAR_ASISTEN
    with st.chat_message(pesan["role"], avatar=avatar):
        st.markdown(pesan["isi"])


# ============================================================
# 6. TANYA JAWAB
# ============================================================

pertanyaan = st.chat_input("Tulis pertanyaanmu seputar matematika di sini...")

if pertanyaan:
    # Tampilkan pertanyaan, lalu catat ke buku catatan.
    with st.chat_message("user", avatar=AVATAR_USER):
        st.markdown(pertanyaan)
    st.session_state.riwayat.append({"role": "user", "isi": pertanyaan})

    # Minta jawaban ke mesin RAG. .stream() + st.write_stream() membuat
    # jawaban muncul bertahap, kata demi kata, seperti sedang diketik.
    with st.chat_message("assistant", avatar=AVATAR_ASISTEN):
        with st.spinner("Mas Primus sedang menghitung jawabannya..."):
            jawaban = st.write_stream(rag_chain.stream(pertanyaan))
    st.session_state.riwayat.append({"role": "assistant", "isi": jawaban})