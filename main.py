import streamlit as st
from PIL import Image
import numpy as np
import wave
import io

# --- Settings ---
RESIZE = (16,16)
NOTE_DURATION_SCALE = 100
OCTAVE_BASE = 1
SAMPLE_RATE = 44100
NOTE_FREQUENCIES = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88]  # C D E F G A B

st.title("🎵 Image to Music Converter")
uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

def pixel_to_note(r, g, b, l):
    duration = int((r / 255) * NOTE_DURATION_SCALE) + 50
    octave = OCTAVE_BASE + int((g / 255) * 11)
    note_index = int((b / 255) * (len(NOTE_FREQUENCIES) - 1))
    freq = NOTE_FREQUENCIES[note_index] * (2 ** (octave - 4))
    volume = (l / 255) * 0.3  # lower = quieter
    return freq, duration, volume

def generate_wave(freq, duration_ms, volume):
    duration_sec = duration_ms / 1000.0
    t = np.linspace(0, duration_sec, int(SAMPLE_RATE * duration_sec), False)
    wave_data = np.sin(freq * t * 2 * np.pi)
    audio = wave_data * (32767 * volume)
    return audio.astype(np.int16)

def image_to_audio_data(img):
    img = img.convert("RGB").resize(RESIZE)
    img = img.transpose(Image.Transpose.ROTATE_270).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    data = np.array(img)

    audio_data = np.array([], dtype=np.int16)
    for x in range(data.shape[1]):
        for y in range(data.shape[0]):
            r, g, b = data[y, x]
            l = int(0.299 * r + 0.587 * g + 0.114 * b)
            freq, duration, volume = pixel_to_note(r, g, b, l)
            tone = generate_wave(freq, duration, volume)
            audio_data = np.concatenate((audio_data, tone))
    return audio_data

def save_wave_file(audio_data):
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_data.tobytes())
    buffer.seek(0)
    return buffer


#streamlit funtion
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Resized Preview", width=256)

    if st.button("🎶 Generate Music"):
        with st.spinner("Synthesizing..."):
            audio_data = image_to_audio_data(image)
            wave_buffer = save_wave_file(audio_data)

            st.success("Done! Use the player below to listen 👇")
            st.audio(wave_buffer.getvalue(), format='audio/wav')

            st.download_button(
                label="⬇️ Download Music (WAV)",
                data=wave_buffer.getvalue(),
                file_name="output_music.wav",
                mime="audio/wav"
            )
