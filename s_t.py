import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
from gtts import gTTS
from googletrans import Translator

# 🌍 TÍTULO DEL APLICATIVO
st.title("🌟 Traductor de Voz en Tiempo Real 🎤")
st.markdown("Convierte tu voz en texto y tradúcelo a diferentes idiomas. ¡Presiona el botón y comienza a hablar!")

# 📸 CARGAR IMAGEN 
image = Image.open("lenguaje.jpg")
st.image(image, width=300)

# 📌 SIDEBAR
with st.sidebar:
    st.subheader("📖 Instrucciones")
    st.write("1️⃣ Presiona el botón de grabar y habla el texto que deseas traducir.")
    st.write("2️⃣ Elige el idioma de entrada y salida.")
    st.write("3️⃣ Convierte el texto en audio con un solo clic.")

# 🎙️ BOTÓN PARA RECONOCIMIENTO DE VOZ
st.markdown("### 🎧 Presiona el botón y habla:")
stt_button = Button(label="🎤 Escuchar", width=300, height=50)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if ( value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))

# 🚀 PROCESO DE OBTENCIÓN DE TEXTO
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

if result and "GET_TEXT" in result:
    text = result.get("GET_TEXT")
    st.success(f"✅ **Texto detectado:** {text}")

    # 📌 SELECCIÓN DE IDIOMA
    idiomas = {
        "Inglés": "en", "Español": "es", "Bengali": "bn",
        "Coreano": "ko", "Mandarín": "zh-cn", "Japonés": "ja"
    }

    st.markdown("### 🌎 Selecciona los idiomas")
    in_lang = st.selectbox("🗣️ Idioma de entrada", list(idiomas.keys()))
    out_lang = st.selectbox("🔊 Idioma de salida", list(idiomas.keys()))

    input_language = idiomas[in_lang]
    output_language = idiomas[out_lang]

    # 🎙️ SELECCIÓN DE ACENTO
    acentos = {
        "Defecto": "com", "Español": "com.mx", "Reino Unido": "co.uk",
        "Estados Unidos": "com", "Canadá": "ca", "Australia": "com.au",
        "Irlanda": "ie", "Sudáfrica": "co.za"
    }

    english_accent = st.selectbox("🎭 Selecciona el acento", list(acentos.keys()))
    tld = acentos[english_accent]

    # 🔊 FUNCIÓN DE TEXTO A AUDIO
    def text_to_speech(input_language, output_language, text, tld):
        translator = Translator()
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        filename = f"temp/audio.mp3"
        tts.save(filename)
        return filename, trans_text

    # 🎵 BOTÓN PARA CONVERTIR TEXTO A AUDIO
    if st.button("🎼 Convertir a Audio"):
        result_audio, output_text = text_to_speech(input_language, output_language, text, tld)
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

        
    


