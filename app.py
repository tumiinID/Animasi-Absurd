import streamlit as st
from google import genai
import edge_tts
import asyncio
import re

st.set_page_config(page_title="Studio Absurd & Sarkas", layout="wide")
st.title("🎭 Kantor Tim AI: Animasi Absurd & Sarkas")

# Pengaturan di Sidebar
api_key = st.sidebar.text_input("Masukkan Gemini API Key", type="password").strip()
gaya_konten = st.sidebar.selectbox(
    "Pilih Gaya Tim AI:",
    [
        "Animasi Absurd Tanpa Dialog (Komedi Fisik / Slapstick)",
        "Animasi Absurd Pakai Narator (Komedi Gelap / Nyeleneh)",
        "Sarkas Tajam (Kritik Sosial / Sindiran Halus)"
    ]
)
suara_pilihan = st.sidebar.selectbox(
    "Pilih Karakter Suara VO (Jika Pakai Narator):",
    ["id-ID-ArdiNeural (Pria - Tegas/Sarkas)", "id-ID-GadisNeural (Wanita - Santai/Sinis)"]
)

topik = st.text_input("Masukkan Ide Dasar / Masalah:", placeholder="Contoh: 3 anak dinosaurus berebut semangka raksasa")

async def buat_audio(teks, voice, output_file):
    communicate = edge_tts.Communicate(teks, voice)
    await communicate.save(output_file)

if st.button("Jalankan Produksi"):
    if not api_key:
        st.error("⚠️ Masukkan dulu Gemini API Key di menu kiri atas (>>).")
    elif not topik:
        st.error("⚠️ Ketik dulu ide kontennya di kotak di atas.")
    else:
        try:
            client = genai.Client(api_key=api_key)
            MODEL_AI = 'gemini-3.8-flash'
            
            # --- AGEN 1: KONSEP & KELUCUAN ---
            with st.status("🕵️ Agen 1: Merancang kelucuan & alur...", expanded=True) as status:
                prompt_riset = f"""
                Ide dasar: '{topik}'.
                Gaya: {gaya_konten}.
                Kembangkan ide ini menjadi konsep cerita pendek 30-45 detik. Tentukan karakter, situasi konyol, dan kejutan/klimaks yang lucu atau menyindir. Buat dalam 3-4 poin singkat.
                """
                res_riset = client.models.generate_content(
                    model=MODEL_AI,
                    contents=prompt_riset
                )
                hasil_riset = res_riset.text
                st.write(hasil_riset)
                status.update(label="✅ Konsep Selesai!", state="complete", expanded=False)

            # --- AGEN 2: PENULIS NASKAH / SKENARIO ---
            with st.status("✍️ Agen 2: Menyusun skenario & caption...", expanded=True) as status:
                prompt_naskah = f"""
                Berdasarkan konsep berikut:
                {hasil_riset}
                
                Buat skenario video pendek (30-45 detik) dengan gaya {gaya_konten}.
                Aturan wajib:
                - Jika gaya 'Tanpa Dialog': Tulis aksi fisik karakter dan ekspresi wajah yang lucu per detik. Di bagian [NASKAH VO], tulis HANYA kata: TANPA SUARA.
                - Jika memakai narator/sarkas: Gunakan bahasa Indonesia sehari-hari yang tajam, santai, tidak kaku.
                
                Format output wajib persis seperti ini:
                [NASKAH VO]: (Tulis HANYA teks yang dibacakan narator tanpa tanda kurung, atau tulis TANPA SUARA jika tanpa dialog).
                [CAPTION]: (Tulis caption singkat memancing komentar + 5 hashtag).
                """
                res_naskah = client.models.generate_content(
                    model=MODEL_AI,
                    contents=prompt_naskah
                )
                hasil_naskah = res_naskah.text
                st.write(hasil_naskah)
                status.update(label="✅ Skenario & Caption Siap!", state="complete", expanded=False)

            # --- AGEN 3: SUTRADARA ANIMASI (PROMPT VISUAL) ---
            with st.status("🎬 Agen 3: Membuat prompt animasi per adegan...", expanded=True) as status:
                prompt_visual = f"""
                Ubah skenario berikut menjadi 5 adegan visual berurutan (rasio 9:16) untuk generator gambar/video AI (Google Flow / Leonardo AI / Kling):
                {hasil_naskah}
                
                Untuk setiap adegan (Adegan 1 sampai 5), berikan:
                1. Aksi/cerita singkat bahasa Indonesia.
                2. Prompt bahasa Inggris yang sangat detail dan konsisten karakternya. Jika gaya Animasi Absurd, gunakan gaya '3D stylized animation, Pixar meets Larva comedy style, exaggerated funny facial expressions, bright vibrant lighting, dynamic camera'. Jika gaya Sarkas, gunakan 'satirical editorial 3D illustration, moody cinematic lighting'.
                """
                res_visual = client.models.generate_content(
                    model=MODEL_AI,
                    contents=prompt_visual
                )
                hasil_visual = res_visual.text
                st.write(hasil_visual)
                status.update(label="✅ 5 Prompt Visual Siap!", state="complete", expanded=False)

            # --- AGEN 4: PENGISI SUARA OTOMATIS (TTS) ---
            match = re.search(r'\[NASKAH VO\]:(.*?)\[CAPTION\]:', hasil_naskah, re.DOTALL)
            teks_vo = match.group(1).strip() if match else ""
            
            if teks_vo and "TANPA SUARA" not in teks_vo.upper():
                with st.status("🎙️ Agen 4: Merekam suara Voice Over...", expanded=True) as status:
                    voice_code = suara_pilihan.split(" ")[0]
                    file_audio = "hasil_vo.mp3"
                    asyncio.run(buat_audio(teks_vo, voice_code, file_audio))
                    
                    st.audio(file_audio, format="audio/mp3")
                    with open(file_audio, "rb") as f:
                        st.download_button("⬇️ Download File Suara (.mp3)", f, file_name="vo_konten.mp3")
                    status.update(label="✅ Audio Siap Diunduh!", state="complete", expanded=False)
            else:
                st.info("🔇 Mode Tanpa Dialog aktif: Audio narator dilewati, silakan langsung gunakan 5 prompt visual di atas.")

        except Exception as e:
            st.error(f"❌ Terjadi kesalahan dari Google API: {e}")
