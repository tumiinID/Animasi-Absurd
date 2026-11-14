import streamlit as st
from google import genai
from google.genai import types
import edge_tts
import asyncio
import re

st.set_page_config(page_title="Studio Absurd & Sarkas", layout="wide")
st.title("🎭 Kantor Tim AI: Animasi Absurd & Sarkas")

# Pengaturan di Sidebar
api_key = st.sidebar.text_input("Masukkan Gemini API Key", type="password")
gaya_konten = st.sidebar.selectbox(
    "Pilih Gaya Tim AI:",
    ["Animasi Absurd (Komedi Gelap / Nyeleneh)", "Sarkas Tajam (Kritik Sosial / Sindiran Halus)"]
)
suara_pilihan = st.sidebar.selectbox(
    "Pilih Karakter Suara VO:",
    ["id-ID-ArdiNeural (Pria - Tegas/Sarkas)", "id-ID-GadisNeural (Wanita - Santai/Sinis)"]
)

topik = st.text_input("Masukkan Ide Dasar / Masalah:", placeholder="Contoh: Rapat pejabat bahas solusi macet tapi naik helikopter")

# Fungsi untuk membuat audio MP3
async def buat_audio(teks, voice, output_file):
    communicate = edge_tts.Communicate(teks, voice)
    await communicate.save(output_file)

if st.button("Jalankan Produksi") and api_key and topik:
    client = genai.Client(api_key=api_key)
    
    # --- AGEN 1: RISET & SUDUT PANDANG NYELENEH ---
    with st.status("🕵️ Agen 1: Mencari celah kelucuan & fakta...", expanded=True) as status:
        prompt_riset = f"""
        Topik: '{topik}'.
        Gaya: {gaya_konten}.
        Cari fakta nyata atau fenomena umum terkait topik ini menggunakan Google Search, lalu temukan ironi, kontradiksi, atau sisi paling absurd yang bisa dijadikan bahan komedi/sindiran tajam. Buat dalam 3-4 poin singkat.
        """
        res_riset = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_riset,
            config=types.GenerateContentConfig(tools=[{"google_search": {}}])
        )
        hasil_riset = res_riset.text
        st.write(hasil_riset)
        status.update(label="✅ Sudut Pandang Ditemukan!", state="complete", expanded=False)

    # --- AGEN 2: PENULIS NASKAH ABSURD / SARKAS ---
    with st.status("✍️ Agen 2: Menulis naskah & dialog...", expanded=True) as status:
        prompt_naskah = f"""
        Berdasarkan ironi berikut:
        {hasil_riset}
        
        Buat naskah video pendek (durasi 30-45 detik) dengan gaya {gaya_konten}.
        Aturan wajib:
        - Hindari bahasa baku/kaku ala AI. Gunakan bahasa sehari-hari Indonesia yang tajam, punchy, dan tidak tertebak.
        - Jika Absurd: Masukkan elemen visual atau logika yang di luar nalar tapi nyambung dengan realita.
        - Jika Sarkas: Gunakan pujian palsu yang menohok atau analogi kehidupan sehari-hari yang bikin penonton merasa tersindir.
        
        Format output:
        [NASKAH VO]: (Tulis HANYA teks yang akan dibacakan oleh pengisi suara, tanpa keterangan musik atau ekspresi dalam kurung, agar bisa langsung diubah jadi audio).
        [CAPTION]: (Tulis caption singkat memancing komentar + 5 hashtag).
        """
        res_naskah = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_naskah
        )
        hasil_naskah = res_naskah.text
        st.write(hasil_naskah)
        status.update(label="✅ Naskah Selesai!", state="complete", expanded=False)

    # --- AGEN 3: SUTRADARA ANIMASI (PROMPT VISUAL) ---
    with st.status("🎬 Agen 3: Merancang prompt animasi...", expanded=True) as status:
        prompt_visual = f"""
        Ubah naskah berikut menjadi 5 adegan visual (rasio 9:16) untuk generator gambar/video AI (seperti Google Flow / Leonardo AI / Kling):
        {hasil_naskah}
        
        Untuk setiap adegan, berikan:
        1. Potongan kalimat naskahnya.
        2. Prompt bahasa Inggris yang sangat detail. Jika gaya Absurd, gunakan gaya visual seperti '3D surreal animation, exaggerated facial expressions, Pixar meets Adult Swim style, vibrant lighting, absurd comedy'. Jika gaya Sarkas, gunakan 'satirical editorial illustration style, moody cinematic lighting, dramatic camera angle'.
        """
        res_visual = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_visual
        )
        hasil_visual = res_visual.text
        st.write(hasil_visual)
        status.update(label="✅ Storyboard & Prompt Siap!", state="complete", expanded=False)

    # --- AGEN 4: PENGISI SUARA OTOMATIS (TTS) ---
    with st.status("🎙️ Agen 4: Merekam suara Voice Over...", expanded=True) as status:
        # Mengambil bagian [NASKAH VO] saja untuk dibacakan
        match = re.search(r'\[NASKAH VO\]:(.*?)\[CAPTION\]:', hasil_naskah, re.DOTALL)
        teks_vo = match.group(1).strip() if match else hasil_naskah
        
        voice_code = suara_pilihan.split(" ")[0]
        file_audio = "hasil_vo.mp3"
        asyncio.run(buat_audio(teks_vo, voice_code, file_audio))
        
        st.audio(file_audio, format="audio/mp3")
        with open(file_audio, "rb") as f:
            st.download_button("⬇️ Download File Suara (.mp3)", f, file_name="vo_konten.mp3")
        status.update(label="✅ Audio Siap Diunduh!", state="complete", expanded=False)
