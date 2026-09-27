from pathlib import Path
import os

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
# 1. CONFIGURATION — identitas produk & data konten
# ============================================================
# Semua teks & data konten dikumpulkan di satu tempat (single source of
# truth) supaya Beranda, halaman Materi, dan halaman Contoh Pertanyaan
# tidak saling menduplikasi data.

NAMA_APLIKASI = "Primus EduMath Indonesia"
TAGLINE = "Asisten Pembelajaran Matematika di Indonesia"
DESKRIPSI = (
    "Teman belajar berbasis AI untuk membantu memahami informasi dan "
    "pembelajaran matematika berdasarkan sumber yang tersedia."
)
DESKRIPSI_SINGKAT = "Jawaban disusun AI berdasarkan dokumen sumber yang tersedia — bukan dari internet."

# Kategori belajar: dipakai ulang di Beranda (learning cards), halaman
# Contoh Pertanyaan (dikelompokkan per kategori), dan halaman Materi.
KATEGORI_BELAJAR = [
    {
        "kunci": "pembelajaran",
        "ikon": "📊",
        "judul": "Pembelajaran",
        "deskripsi": "Pelajari berbagai informasi mengenai pembelajaran matematika.",
        "pertanyaan": [
            "Apa saja metode pembelajaran matematika yang diterapkan di Indonesia?",
            "Bagaimana penerapan matematika dalam pembelajaran sehari-hari?",
        ],
    },
    {
        "kunci": "konsep",
        "ikon": "🧮",
        "judul": "Konsep Matematika",
        "deskripsi": "Temukan informasi mengenai konsep dan penerapan matematika.",
        "pertanyaan": [
            "Apa saja konsep matematika yang dibahas dalam sumber pembelajaran ini?",
            "Bagaimana konsep matematika dijelaskan dalam dokumen sumber?",
        ],
    },
    {
        "kunci": "pendidikan",
        "ikon": "🎓",
        "judul": "Pendidikan",
        "deskripsi": "Jelajahi informasi mengenai pendidikan matematika di Indonesia.",
        "pertanyaan": [
            "Bagaimana perkembangan pembelajaran matematika di Indonesia?",
            "Apa saja topik pembelajaran yang tersedia dalam dokumen sumber?",
        ],
    },
]

# Kartu ke-4 di Beranda tidak mengajukan pertanyaan, tapi membuka halaman
# Materi — jadi disimpan terpisah dari KATEGORI_BELAJAR.
KARTU_SUMBER = {
    "ikon": "📚",
    "judul": "Sumber Pembelajaran",
    "deskripsi": "Temukan informasi berdasarkan dokumen sumber yang tersedia.",
}

# Pertanyaan cepat = pertanyaan pertama tiap kategori + satu pertanyaan umum.
PERTANYAAN_CEPAT = [(k["ikon"], k["pertanyaan"][0]) for k in KATEGORI_BELAJAR] + [
    ("📖", "Apa saja topik pembelajaran yang tersedia dalam dokumen sumber?")
]


# ============================================================
# 2. PENGATURAN HALAMAN
# ============================================================
# Wajib jadi perintah Streamlit pertama: judul tab browser dan ikonnya.

st.set_page_config(
    page_title=NAMA_APLIKASI,
    page_icon="📐",
    layout="centered",
)


# ============================================================
# 3. CSS — sistem warna, tipografi, dan micro-interaction
# ============================================================
# Semua variabel warna memakai konvensi umum (--primary, --secondary, dst)
# supaya mudah diubah di satu tempat. Kontras teks vs background dijaga:
# --secondary (emas) sengaja HANYA dipakai untuk aksen/tombol/border,
# bukan sebagai warna teks di atas latar terang, karena kontrasnya
# terlalu rendah untuk dibaca nyaman.

_CSS_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

:root {
    --primary: #1F3A5F;         /* navy: identitas utama, heading, ikon */
    --primary-dark: #142136;    /* navy gelap: latar sidebar */
    --secondary: #D9A62E;       /* emas: aksen, tombol aktif, border */
    --background: #F5F6F2;      /* latar utama, mirip kertas grafik */
    --surface: #FFFFFF;         /* latar card & bubble */
    --text: #1B2230;
    --muted: #5B6472;
    --border: #E1E4DC;
    --success: #2F8F80;
    --warning: #B4740E;
    --error: #C0392B;
}

html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
h1, h2, h3 { font-family: 'Fraunces', serif; letter-spacing: -0.01em; color: var(--primary); }

.stApp {
    background-color: var(--background);
    background-image:
        linear-gradient(rgba(31, 58, 95, 0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(31, 58, 95, 0.05) 1px, transparent 1px);
    background-size: 34px 34px;
}
.block-container { max-width: 780px; padding-top: 2rem; padding-bottom: 3rem; }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] { background-color: var(--primary-dark); }
[data-testid="stSidebar"] * { color: #EDEFEF; }
[data-testid="stSidebar"] .stButton > button {
    background-color: transparent;
    border: 1px solid rgba(255, 255, 255, 0.14);
    color: #EDEFEF;
    justify-content: flex-start;
    border-radius: 8px;
    transition: background-color 0.15s ease, border-color 0.15s ease, color 0.15s ease;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background-color: rgba(217, 166, 46, 0.15);
    border-color: var(--secondary);
    color: var(--secondary);
}
/* Sorotan menu aktif — progressive enhancement lewat class st-key- */
.st-key-nav___AKTIF___ .stButton > button {
    background-color: var(--secondary) !important;
    border-color: var(--secondary) !important;
    color: var(--primary-dark) !important;
    font-weight: 600 !important;
}
.peduam-brand {
    display: flex; flex-direction: column; align-items: flex-start; gap: 2px;
    padding: 0.25rem 0 1.25rem 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.14);
    margin-bottom: 1rem;
}
.peduam-brand-icon { font-size: 1.8rem; }
.peduam-brand-name { font-family: 'Fraunces', serif; font-size: 1.15rem; font-weight: 600; color: #FFFFFF; }
.peduam-brand-tag { font-size: 0.8rem; color: rgba(255, 255, 255, 0.65); }

/* ---------- Hero / Header ---------- */
.peduam-hero { text-align: center; padding: 1.25rem 0 1.75rem 0; }
.peduam-hero-icon { font-size: 2.3rem; }
.peduam-hero-title { font-size: 2rem; font-weight: 600; margin: 0.3rem 0 0.15rem 0; color: var(--primary); }
.peduam-hero-tagline { font-size: 1rem; font-weight: 500; color: var(--muted); margin-bottom: 0.6rem; }
.peduam-hero-desc { max-width: 500px; margin: 0 auto; color: var(--muted); line-height: 1.6; }
.peduam-hero-rule { width: 42px; height: 3px; background: var(--secondary); margin: 0.7rem auto 0 auto; border-radius: 2px; }

.peduam-header-ringkas {
    display: flex; align-items: center; gap: 0.7rem;
    padding-bottom: 1rem; margin-bottom: 1rem; border-bottom: 1px solid var(--border);
}
.peduam-header-icon { font-size: 1.6rem; }
.peduam-header-title { font-size: 1.15rem; font-weight: 600; color: var(--primary); }
.peduam-header-tagline { font-size: 0.82rem; color: var(--muted); }

/* ---------- Empty state (Percakapan tanpa riwayat) ---------- */
.peduam-empty { text-align: center; padding: 1rem 0 1.25rem 0; }
.peduam-empty-icon { font-size: 2rem; }
.peduam-empty h3 { margin: 0.4rem 0 0.3rem 0; }
.peduam-empty-desc { color: var(--muted); font-size: 0.9rem; max-width: 460px; margin: 0 auto; }

/* ---------- Tombol & kartu umum ---------- */
.stButton > button { border-radius: 8px; transition: transform 0.12s ease, box-shadow 0.12s ease; }
.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 10px rgba(31, 58, 95, 0.12); }
.stButton > button:active { transform: translateY(0); }

[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 12px !important;
    transition: box-shadow 0.15s ease, border-color 0.15s ease;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: var(--secondary) !important;
    box-shadow: 0 6px 14px rgba(31, 58, 95, 0.10);
}
.peduam-card-icon { font-size: 1.5rem; margin-bottom: 0.15rem; }

/* ---------- Chat ---------- */
[data-testid="stChatMessage"] {
    border-radius: 16px;
    padding: 0.5rem 0.85rem;
    margin-bottom: 0.7rem;
    border: 1px solid var(--border);
    background-color: var(--surface);
}
/* User: compact, digeser ke kanan. Assistant: penuh, sedikit ber-aksen. */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    max-width: 78%;
    margin-left: auto;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    max-width: 100%;
    border-left: 3px solid var(--secondary);
    background-color: rgba(31, 58, 95, 0.03);
}
[data-testid="stChatInput"] textarea { border-radius: 12px; }

/* ---------- Footer ---------- */
.peduam-footer {
    text-align: center; margin-top: 2.5rem; padding-top: 1.2rem;
    border-top: 1px solid var(--border); color: var(--muted);
    font-size: 0.85rem; line-height: 1.5;
}
.peduam-footer-kecil { font-size: 0.75rem; opacity: 0.8; }

/* ---------- Reset percakapan cepat (muncul di header ringkas saat mobile,
   karena sidebar bisa tersembunyi di layar kecil) ---------- */
.peduam-reset-inline { margin-left: auto; }
.peduam-reset-inline .stButton > button {
    font-size: 0.78rem;
    padding: 0.25rem 0.65rem;
    background-color: transparent;
    border: 1px solid var(--border);
    color: var(--muted);
}
.peduam-reset-inline .stButton > button:hover {
    border-color: var(--secondary);
    color: var(--primary);
}

/* ---------- Aksesibilitas: fokus keyboard harus selalu terlihat ---------- */
.stButton > button:focus-visible,
[data-testid="stChatInput"] textarea:focus-visible {
    outline: 2px solid var(--secondary) !important;
    outline-offset: 2px;
}

/* ---------- Hormati preferensi "reduced motion" pengguna ---------- */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.001ms !important;
        transition-duration: 0.001ms !important;
    }
    .stButton > button:hover,
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: none !important;
    }
}

/* ---------- Penyesuaian untuk layar kecil ---------- */
@media (max-width: 640px) {
    .block-container { padding-top: 1.1rem; }
    .peduam-hero { padding: 0.75rem 0 1.25rem 0; }
    .peduam-hero-icon { font-size: 1.9rem; }
    .peduam-hero-title { font-size: 1.5rem; }
    .peduam-hero-desc { max-width: 100%; }
}
</style>
"""


def muat_css(tampilan_aktif: str):
    """Suntikkan CSS kustom. Nama tampilan aktif dipakai untuk menyorot
    menu sidebar yang sedang dipilih (lihat class st-key- di atas)."""
    st.markdown(_CSS_TEMPLATE.replace("___AKTIF___", tampilan_aktif), unsafe_allow_html=True)


# ============================================================
# 4. CEK API KEY
# ============================================================
# Di laptop, GROQ_API_KEY dibaca dari file .env. Di Streamlit Cloud,
# GROQ_API_KEY diisi lewat menu Secrets dan otomatis jadi environment
# variable — kode yang sama berjalan di dua tempat tanpa perlu diubah.

load_dotenv()
if not os.getenv("GROQ_API_KEY"):
    st.error(
        "GROQ_API_KEY belum diisi. Cek file .env (di laptop) "
        "atau menu Secrets (di Streamlit Cloud)."
    )
    st.stop()


# ============================================================
# 5. BACKEND INITIALIZATION (lazy — baru berjalan saat dibutuhkan)
# ============================================================
# @st.cache_resource membuat fungsi ini cukup dijalankan SEKALI seumur
# hidup server: dokumen tidak dimuat ulang, vector store tidak dibangun
# ulang, model tidak dibuat ulang di setiap pertanyaan.
#
# PENTING: fungsi ini TIDAK dipanggil di top-level file. Ia baru dipanggil
# dari dapatkan_rag_chain(), yaitu saat pengguna benar-benar mengirim
# pertanyaan pertama (lihat proses_pertanyaan()). Dengan begitu sidebar,
# navigasi, dan Beranda langsung tampil tanpa menunggu vector store
# selesai dibangun — mencegah halaman kosong/loading di awal.

@st.cache_resource(show_spinner="Menyiapkan Primus EduMath Indonesia...")
def siapkan_chatbot():
    model = buat_model()
    dokumen = muat_dokumen(KNOWLEDGE_DIR)
    vectorstore = bangun_vectorstore(dokumen)
    retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})
    system_prompt = muat_system_prompt(SYSTEM_PROMPT_PATH)
    return buat_rag_chain(retriever, model, system_prompt)


def dapatkan_rag_chain():
    """Titik masuk tunggal ke mesin RAG — dipanggil hanya saat pertanyaan
    benar-benar diproses (lazy initialization)."""
    return siapkan_chatbot()


# ============================================================
# 6. SESSION STATE
# ============================================================
# - riwayat            : histori percakapan (list of {"role","isi"})
# - tampilan_aktif      : halaman yang sedang dibuka (nav state)
# - pertanyaan_tertunda : pertanyaan dari card/tombol yang menunggu diproses

if "riwayat" not in st.session_state:
    st.session_state.riwayat = []
if "tampilan_aktif" not in st.session_state:
    st.session_state.tampilan_aktif = "beranda"
if "pertanyaan_tertunda" not in st.session_state:
    st.session_state.pertanyaan_tertunda = None


def ajukan_pertanyaan(teks: str):
    """Dipanggil oleh card / tombol pertanyaan: pertanyaan langsung
    disiapkan untuk diproses begitu tampilan Percakapan terbuka."""
    st.session_state.pertanyaan_tertunda = teks
    st.session_state.tampilan_aktif = "percakapan"


def buka_materi():
    st.session_state.tampilan_aktif = "materi"


def mulai_percakapan_baru():
    """CHAT -> WELCOME: hapus riwayat, reset state, kembali ke Beranda."""
    st.session_state.riwayat = []
    st.session_state.pertanyaan_tertunda = None
    st.session_state.tampilan_aktif = "beranda"


muat_css(st.session_state.tampilan_aktif)


# ============================================================
# 7. SIDEBAR & NAVIGASI
# ============================================================
# Setiap item menu benar-benar mengubah tampilan_aktif (bukan dekorasi).

MENU_NAVIGASI = [
    ("beranda", "🏠", "Beranda"),
    ("percakapan", "💬", "Percakapan"),
    ("materi", "📚", "Materi"),
    ("contoh", "💡", "Contoh Pertanyaan"),
    ("tentang", "ℹ️", "Tentang"),
]


def render_sidebar():
    with st.sidebar:
        st.markdown(
            f"""
            <div class="peduam-brand">
                <span class="peduam-brand-icon">📐</span>
                <span class="peduam-brand-name">{NAMA_APLIKASI}</span>
                <span class="peduam-brand-tag">{TAGLINE}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for kunci, ikon, label in MENU_NAVIGASI:
            if st.button(f"{ikon}  {label}", key=f"nav_{kunci}", use_container_width=True):
                st.session_state.tampilan_aktif = kunci
                st.session_state.pertanyaan_tertunda = None

        st.markdown("<br/>", unsafe_allow_html=True)
        if st.button("🗑️  Percakapan Baru", key="btn_percakapan_baru", use_container_width=True):
            mulai_percakapan_baru()

        jumlah_tanya = len([p for p in st.session_state.riwayat if p["role"] == "user"])
        if jumlah_tanya > 0:
            st.caption(f"💬 {jumlah_tanya} pertanyaan pada sesi ini")

        st.markdown("---")
        st.caption("Powered by AI & RAG")


render_sidebar()


# ============================================================
# 8. HEADER / HERO
# ============================================================

def render_header(ringkas: bool, tampilkan_reset: bool = False):
    if ringkas:
        if tampilkan_reset:
            # Di layar kecil sidebar sering tersembunyi di balik menu hamburger,
            # jadi tombol reset juga disediakan di sini agar tetap mudah dijangkau.
            kolom_kiri, kolom_kanan = st.columns([5, 2])
            with kolom_kiri:
                st.markdown(
                    f"""
                    <div class="peduam-header-ringkas" style="border-bottom: none; margin-bottom: 0; padding-bottom: 0;">
                        <span class="peduam-header-icon">📐</span>
                        <div>
                            <div class="peduam-header-title">{NAMA_APLIKASI}</div>
                            <div class="peduam-header-tagline">{TAGLINE}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with kolom_kanan:
                st.markdown('<div class="peduam-reset-inline">', unsafe_allow_html=True)
                if st.button("🗑️ Baru", key="btn_reset_inline", use_container_width=True):
                    mulai_percakapan_baru()
                st.markdown("</div>", unsafe_allow_html=True)
            st.markdown(
                '<hr style="margin: 0 0 1rem 0; border: none; border-top: 1px solid var(--border);" />',
                unsafe_allow_html=True,
            )
            return
        st.markdown(
            f"""
            <div class="peduam-header-ringkas">
                <span class="peduam-header-icon">📐</span>
                <div>
                    <div class="peduam-header-title">{NAMA_APLIKASI}</div>
                    <div class="peduam-header-tagline">{TAGLINE}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="peduam-hero">
                <div class="peduam-hero-icon">📐</div>
                <h1 class="peduam-hero-title">{NAMA_APLIKASI}</h1>
                <p class="peduam-hero-tagline">{TAGLINE}</p>
                <p class="peduam-hero-desc">{DESKRIPSI}</p>
                <div class="peduam-hero-rule"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# 9. QUICK QUESTIONS — dipakai ulang di Beranda & Percakapan (empty state)
# ============================================================

def render_quick_questions(konteks: str):
    st.markdown("###### 💡 Mulai dengan pertanyaan")
    kolom = st.columns(2)
    for i, (ikon, teks) in enumerate(PERTANYAAN_CEPAT):
        with kolom[i % 2]:
            if st.button(f"{ikon} {teks}", key=f"quick_{konteks}_{i}", use_container_width=True):
                ajukan_pertanyaan(teks)


# ============================================================
# 10. BERANDA (WELCOME SCREEN)
# ============================================================

def render_kartu(ikon: str, judul: str, deskripsi: str, label_tombol: str, aksi):
    with st.container(border=True):
        st.markdown(f"<div class='peduam-card-icon'>{ikon}</div>", unsafe_allow_html=True)
        st.markdown(f"**{judul}**")
        st.caption(deskripsi)
        if st.button(label_tombol, key=f"card_{judul}", use_container_width=True):
            aksi()


def render_welcome():
    render_header(ringkas=False)

    st.markdown("#### Selamat datang 👋 — belajar matematika dengan cara yang lebih interaktif.")

    kartu_kategori = [
        (k["ikon"], k["judul"], k["deskripsi"], f"Tanyakan {k['judul'].lower()}", (lambda p=k["pertanyaan"][0]: ajukan_pertanyaan(p)))
        for k in KATEGORI_BELAJAR
    ]
    kartu_kategori.append(
        (KARTU_SUMBER["ikon"], KARTU_SUMBER["judul"], KARTU_SUMBER["deskripsi"], "Lihat daftar sumber", buka_materi)
    )

    kolom = st.columns(2)
    for i, (ikon, judul, deskripsi, label_tombol, aksi) in enumerate(kartu_kategori):
        with kolom[i % 2]:
            render_kartu(ikon, judul, deskripsi, label_tombol, aksi)

    render_quick_questions("beranda")


# ============================================================
# 11. PERCAKAPAN (CHAT) — empty state & conversation mode
# ============================================================

def render_chat_empty_state():
    """DISCOVERY MODE: belum ada riwayat. Tampilkan ajakan bertanya yang
    jelas, bukan halaman kosong."""
    st.markdown(
        f"""
        <div class="peduam-empty">
            <div class="peduam-empty-icon">🧮</div>
            <h3>Bagaimana saya bisa membantu belajar matematika hari ini?</h3>
            <p class="peduam-empty-desc">{DESKRIPSI_SINGKAT}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_quick_questions("chat")

    st.markdown("###### Atau jelajahi kategori berikut:")
    kolom = st.columns(len(KATEGORI_BELAJAR))
    for i, kat in enumerate(KATEGORI_BELAJAR):
        with kolom[i]:
            st.markdown(f"**{kat['ikon']} {kat['judul']}**")
            st.caption(kat["deskripsi"])


def proses_pertanyaan(pertanyaan: str):
    """Mengirim satu pertanyaan ke mesin RAG dan menampilkan pasangan
    bubble user + assistant. Mekanisme streaming asli dipertahankan
    apa adanya: rag_chain.stream(...) + st.write_stream(...)."""
    with st.chat_message("user", avatar="👤"):
        st.markdown(pertanyaan)
    st.session_state.riwayat.append({"role": "user", "isi": pertanyaan})

    with st.chat_message("assistant", avatar="🤖"):
        try:
            with st.spinner("🤖 Sedang mencari informasi..."):
                rag_chain = dapatkan_rag_chain()
                jawaban = st.write_stream(rag_chain.stream(pertanyaan))
        except Exception:
            jawaban = "Maaf, terjadi kendala saat memproses pertanyaan. Silakan coba lagi."
            st.error(jawaban)
    st.session_state.riwayat.append({"role": "assistant", "isi": jawaban})


def render_chat():
    ada_riwayat = len(st.session_state.riwayat) > 0
    ada_pertanyaan_tertunda = st.session_state.pertanyaan_tertunda is not None

    render_header(ringkas=True, tampilkan_reset=ada_riwayat)

    # CONVERSATION MODE tampil begitu ada riwayat ATAU sebuah pertanyaan
    # baru saja diajukan dari card/tombol contoh.
    if not ada_riwayat and not ada_pertanyaan_tertunda:
        render_chat_empty_state()
    else:
        for pesan in st.session_state.riwayat:
            avatar = "👤" if pesan["role"] == "user" else "🤖"
            with st.chat_message(pesan["role"], avatar=avatar):
                st.markdown(pesan["isi"])

        if ada_pertanyaan_tertunda:
            pertanyaan = st.session_state.pertanyaan_tertunda
            st.session_state.pertanyaan_tertunda = None
            proses_pertanyaan(pertanyaan)

    pertanyaan_baru = st.chat_input("💬 Tanyakan sesuatu tentang pembelajaran matematika...")
    if pertanyaan_baru:
        proses_pertanyaan(pertanyaan_baru)


# ============================================================
# 12. MATERI — kartu kategori + daftar sumber dinamis dari backend
# ============================================================

def render_materi():
    render_header(ringkas=True)
    st.markdown("### 📚 Materi Pembelajaran")
    st.write(
        "Primus EduMath Indonesia menjawab pertanyaan berdasarkan dokumen "
        "sumber yang sudah disiapkan sebelumnya. Berikut cakupan materi "
        "dan sumber yang menjadi rujukan chatbot ini:"
    )

    kolom = st.columns(len(KATEGORI_BELAJAR))
    for i, kat in enumerate(KATEGORI_BELAJAR):
        with kolom[i]:
            with st.container(border=True):
                st.markdown(f"<div class='peduam-card-icon'>{kat['ikon']}</div>", unsafe_allow_html=True)
                st.markdown(f"**{kat['judul']}**")
                st.caption(kat["deskripsi"])
                if st.button("Tanyakan ini", key=f"materi_{kat['kunci']}", use_container_width=True):
                    ajukan_pertanyaan(kat["pertanyaan"][0])

    st.markdown("#### 📄 Dokumen Sumber")
    # Daftar ini dibaca langsung dari folder pengetahuan backend (KNOWLEDGE_DIR),
    # bukan data karangan — jika folder belum tersedia, tampilkan info jujur.
    try:
        berkas = sorted(p.name for p in Path(KNOWLEDGE_DIR).glob("**/*") if p.is_file())
    except Exception:
        berkas = []

    if berkas:
        for nama in berkas:
            st.markdown(f"- 📄 {nama}")
    else:
        st.info("Daftar dokumen sumber belum ditemukan di folder pengetahuan.")

    st.caption("Jawaban chatbot hanya diambil dari dokumen di atas, bukan dari internet.")

    if st.button("💬 Mulai bertanya sekarang", key="btn_materi_tanya", use_container_width=True):
        st.session_state.tampilan_aktif = "percakapan"


# ============================================================
# 13. CONTOH PERTANYAAN — dikelompokkan per kategori
# ============================================================

def render_contoh():
    render_header(ringkas=True)
    st.markdown("### 💡 Contoh Pertanyaan")
    st.write("Klik salah satu pertanyaan di bawah ini untuk langsung menanyakannya ke chatbot.")

    for kat in KATEGORI_BELAJAR:
        st.markdown(f"###### {kat['ikon']} {kat['judul']}")
        for i, teks in enumerate(kat["pertanyaan"]):
            if st.button(teks, key=f"contoh_{kat['kunci']}_{i}", use_container_width=True):
                ajukan_pertanyaan(teks)


# ============================================================
# 14. TENTANG
# ============================================================

def render_tentang():
    render_header(ringkas=True)
    st.markdown("### ℹ️ Tentang Primus EduMath Indonesia")
    st.write(DESKRIPSI)
    st.markdown(
        """
Primus EduMath Indonesia menggunakan pendekatan *Retrieval-Augmented
Generation* (RAG): setiap pertanyaan dicocokkan dengan bagian paling
relevan dari dokumen sumber, lalu jawabannya disusun oleh model AI
berdasarkan bagian tersebut saja.

- 🔍 Jawaban diambil dari dokumen sumber, bukan dari internet.
- 🤖 Model AI digunakan untuk menyusun jawaban yang mudah dipahami.
- 📚 Cakupan topik terbatas pada apa yang tersedia di dokumen sumber.
        """
    )
    st.caption("Dibangun dengan Streamlit, LangChain, ChromaDB, dan Groq.")


# ============================================================
# 15. FOOTER
# ============================================================

def render_footer():
    st.markdown(
        f"""
        <div class="peduam-footer">
            <strong>{NAMA_APLIKASI}</strong><br/>
            <span>{TAGLINE}</span><br/>
            <span class="peduam-footer-kecil">Powered by AI &amp; RAG</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# 16. ROUTING TAMPILAN UTAMA
# ============================================================

_HALAMAN = {
    "materi": render_materi,
    "contoh": render_contoh,
    "tentang": render_tentang,
    "percakapan": render_chat,
}

_HALAMAN.get(st.session_state.tampilan_aktif, render_welcome)()
render_footer()