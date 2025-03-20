import os
import streamlit as st
import speech_recognition as sr
from gtts import gTTS
from googletrans import Translator
from PIL import Image
import time
import glob

# 🌍 TÍTULO DEL APLICATIVO
st.title("🌟 Traductor de Voz en Tiempo Real 🎤")
st.markdown("Convierte tu voz en texto y tradúcelo a diferentes idiomas. ¡Presiona el botón y comienza a hablar!")

# 📸 CARGAR IMAGEN
image = Image.open("lenguaje.jpg")
st.image(image, width=300)

# 📌 SIDEBAR - INSTRUCCIONES
with st.sidebar:
    st.subheader("📖 Instrucciones")
    st.write("1️⃣ Presiona el botón de grabar y habla el texto que deseas traducir.")
    st.write("2️⃣ Elige el idioma de entrada y salida.")
    st.write("3️⃣ Convierte el texto en audio con un solo clic.")

# 🔴🎙️ BOTÓN DE GRABACIÓN MEJORADO
st.markdown(
    """
    <style>
        .stButton>button {
            background-color: #ff4b4b;
            color: white;
            border-radius: 10px;
            padding: 10px;
            font-size: 18px;
            width: 100%;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("### 🎧 Presiona el botón y habla:")

if st.button("🎤 Grabar Voz"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Escuchando... Habla ahora")
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio, language="es-ES")
            st.success(f"✅ **Texto detectado:** {text}")
        except sr.UnknownValueError:
            st.error("⚠️ No se pudo reconocer el audio. Intenta nuevamente.")
            text = ""
        except sr.RequestError:
            st.error("⚠️ Error de conexión con el servicio de reconocimiento de voz.")
            text = ""

# 📌 SELECCIÓN DE IDIOMA
idiomas = {
    "Inglés": "en", "Español": "es", "Bengalí": "bn",
    "Coreano": "ko", "Mandarín": "zh-cn", "Japonés": "ja"
}

st.markdown("### 🌎 Selecciona los idiomas")
in_lang = st.selectbox("🗣️ Idioma de entrada", list(idiomas.keys()), index=1)
out_lang = st.selectbox("🔊 Idioma de salida", list(idiomas.keys()), index=0)

input_language = idiomas[in_lang]
output_language = idiomas[out_lang]

# 🔊 FUNCIÓN DE TEXTO A AUDIO
def text_to_speech(input_language, output_language, text):
    translator = Translator()
    translation = translator.translate(text, src=input_language, dest=output_language)
    trans_text = translation.text
    tts = gTTS(trans_text, lang=output_language, slow=False)
    filename = "temp/audio.mp3"
    tts.save(filename)
    return filename, trans_text

# 🎵 BOTÓN PARA CONVERTIR TEXTO A AUDIO
convertir_audio = st.button("🎼 Convertir a Audio")
if text and convertir_audio:
    result_audio, output_text = text_to_speech(input_language, output_language, text)
    audio_file = open(result_audio, "rb")
    audio_bytes = audio_file.read()
    st.markdown("### 🎶 Audio generado:")
    st.audio(audio_bytes, format="audio/mp3")

    if st.checkbox("📖 Mostrar texto traducido"):
        st.markdown(f"### ✍️ Texto traducido:")
        st.write(output_text)

# 🗑️ LIMPIEZA AUTOMÁTICA DE AUDIOS ANTIGUOS
def remove_old_files(days=7):
    mp3_files = glob.glob("temp/*.mp3")
    now = time.time()
    for f in mp3_files:
        if os.stat(f).st_mtime < now - (days * 86400):
            os.remove(f)

remove_old_files()



