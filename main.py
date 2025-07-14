import streamlit as st
from PIL import Image
from pydub.generators import Sine
from pydub import AudioSegment
import numpy as np
import io
import os

# --- Settings ---
RESIZE = (32, 32)
NOTE_DURATION_SCALE = 100
OCTAVE_BASE = 1
MAX_VOLUME = -5
MIN_VOLUME = -35
NOTE_FREQUENCIES = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88]  # C D E F G A B

st.title("🎵 Image to Music Converter")
st.markdown("Upload an image. Each pixel becomes a note!")

uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

def pixel_to_note(r, g, b, l):
    duration = int((r / 255) * NOTE_DURATION_SCALE) + 50
    octave = OCTAVE_BASE + int((g / 255) * 11)
    note_index = int((b / 255) * (len(NOTE_FREQUENCIES) - 1))
    freq = NOTE_FREQUENCIES[note_index] * (2 ** (octave - 4))
    volume = MAX_VOLUME - (1 - (l / 255)) * (MAX_VOLUME - MIN_VOLUME)
    return freq, duration, volume

def image_to_audio(img: Image.Image) -> AudioSegment:
    img = img.convert("RGB").resize(RESIZE)
    img = img.transpose(Image.Transpose.ROTATE_270).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    data = np.array(img)

    audio = AudioSegment.silent(duration=0)
    for x in range(data.shape[1]):
        for y in range(data.shape[0]):
            r, g, b = data[y, x]
            l = int(0.299 * r + 0.587 * g + 0.114 * b)
            freq, duration, volume = pixel_to_note(r, g, b, l)
            tone = Sine(freq).to_audio_segment(duration=duration).apply_gain(volume)
            audio += tone
    return audio

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Resized preview below:", width=256)

    if st.button("Generate Music 🎶"):
        with st.spinner("Synthesizing audio..."):
            audio = image_to_audio(image)

            buffer = io.BytesIO()
            audio.export(buffer, format="wav")
            st.audio(buffer.getvalue(), format="audio/wav")

            st.download_button(
                label="Download WAV File",
                data=buffer.getvalue(),
                file_name="output_music.wav",
                mime="audio/wav"
            )
