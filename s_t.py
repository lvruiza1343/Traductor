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

imagen = Image.open('lenguaje.jpg')
# Estilo CSS para centrar elementos
st.markdown(
    """
    <style>
    .centered {
        text-align: center;
    }
    .centered-image {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<h1 class='centered'>CONVERSOR DE IDIOMAS</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='centered'>¡Dile al mundo lo que piensas!</h3>", unsafe_allow_html=True)

st.image(imagen, width=300)
with st.sidebar:
    st.subheader("Asistente de Idiomas")
    st.write("Pulsa el botón, espera la señal auditiva, "
             "expresa tu mensaje y selecciona el idioma "
             "de destino.")

st.write("¡Habla ahora y traduce al instante!")

boton_escuchar = Button(label=" Activar Micrófono ️", width=300, height=50)

boton_escuchar.js_on_event("button_click", CustomJS(code="""
    setTimeout(function(){
        var reconocimiento = new webkitSpeechRecognition();
        reconocimiento.continuous = false;
        reconocimiento.interimResults = false;
        reconocimiento.lang = 'es-ES';

        reconocimiento.onresult = function(e) {
            var valor = e.results[0][0].transcript;
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: valor}));
        }
        reconocimiento.start();
    }, 500); // Pequeña pausa para la señal auditiva
"""))

resultado = streamlit_bokeh_events(
    boton_escuchar,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

if resultado:
    if "GET_TEXT" in resultado:
        texto_escuchado = resultado.get("GET_TEXT")
        st.write("Texto detectado: ", texto_escuchado)

        col1, col2 = st.columns(2)
        idioma_origen = col1.selectbox("Idioma de origen", ["es", "en", "fr", "de", "it"])
        idioma_destino = col2.selectbox("Idioma de destino", ["en", "es", "fr", "de", "it"])

        if st.button("Traducir"):
            traductor = Translator()
            traduccion = traductor.translate(texto_escuchado, src=idioma_origen, dest=idioma_destino)
            st.write("Traducción: ", traduccion.text)

            tts = gTTS(traduccion.text, lang=idioma_destino)
            tts.save("traduccion.mp3")
            audio_file = open("traduccion.mp3", "rb")
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format="audio/mp3", start_time=0)

            # Limpiar archivos de audio después de reproducirlos
            archivos_audio = glob.glob("traduccion.mp3")
            for archivo in archivos_audio:
                os.remove(archivo)
