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

# Configuración de la página
st.set_page_config(page_title="Traductor de Voz", page_icon="")

# Imagen de inicio
image = Image.open('lenguaje.jpg')  # Reemplaza con tu imagen
st.image(image, width=300)

# Barra lateral con instrucciones
with st.sidebar:
    st.subheader("Instrucciones")
    st.write("Presiona el botón 'Escuchar' y habla cuando escuches la señal. Luego, selecciona los idiomas.")

# Título y subtítulo
st.title("Traductor de Voz ")
st.markdown("### ¡Di algo y lo traduciré!")

# Botón de escuchar
stt_button = Button(label="Escuchar ", width=300, height=50, button_type="primary")

# JavaScript modificado para iniciar el reconocimiento de voz correctamente
stt_button.js_on_event("button_click", CustomJS(code="""
    setTimeout(function(){
        var recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'es-ES'; //idioma de reconocimiento inicial
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
    }, 500); // Espera 500 milisegundos antes de iniciar el reconocimiento
"""))

# Evento de reconocimiento de voz
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

if result:
    if "GET_TEXT" in result:
        texto_original = result.get("GET_TEXT")
        st.write(f"Texto original: {texto_original}")

        # Creación del directorio temporal
        try:
            os.makedirs("temp", exist_ok=True)
        except OSError as e:
            st.error(f"Error al crear el directorio temporal: {e}")

        # Traducción y conversión a audio
        translator = Translator()

        col1, col2, col3 = st.columns(3)

        with col1:
            input_lang_name = st.selectbox("Idioma de entrada", ["Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"])
        with col2:
            output_lang_name = st.selectbox("Idioma de salida", ["Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"])
        with col3:
            accent = st.selectbox("Acento", ["Defecto", "Español", "Reino Unido", "Estados Unidos", "Canadá", "Australia", "Irlanda", "Sudáfrica"])

        lang_codes = {
            "Inglés": "en",
            "Español": "es",
            "Bengali": "bn",
            "Coreano": "ko",
            "Mandarín": "zh-cn",
            "Japonés": "ja"
        }

        tld_codes = {
            "Defecto": "com",
            "Español": "com.mx",
            "Reino Unido": "co.uk",
            "Estados Unidos": "com",
            "Canadá": "ca",
            "Australia": "com.au",
            "Irlanda": "ie",
            "Sudáfrica": "co.za"
        }

        input_lang = lang_codes[input_lang_name]
        output_lang = lang_codes[output_lang_name]
        tld = tld_codes[accent]

        def text_to_speech(input_language, output_language, text, tld):
            translation = translator.translate(text, src=input_language, dest=output_language)
            trans_text = translation.text
            tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
            try:
                my_file_name = text[0:20]
            except:
                my_file_name = "audio"
            tts.save(f"temp/{my_file_name}.mp3")
            return my_file_name, trans_text

        display_output_text = st.checkbox("Mostrar texto traducido")

        if st.button("Convertir"):
            result_file, translated_text = text_to_speech(input_lang, output_lang, texto_original, tld)
            audio_file = open(f"temp/{result_file}.mp3", "rb")
            audio_bytes = audio_file.read()
            st.markdown("### Audio traducido:")
            st.audio(audio_bytes, format="audio/mp3", start_time=0)

            if display_output_text:
                st.markdown("### Texto traducido:")
                st.write(translated_text)

        def remove_files(n):
            mp3_files = glob.glob("temp/*.mp3")
            if mp3_files:
                now = time.time()
                n_days = n * 86400
                for f in mp3_files:
                    if os.stat(f).st_mtime < now - n_days:
                        os.remove(f)
                        print(f"Deleted {f}")

        remove_files(7)

