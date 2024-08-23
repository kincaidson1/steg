import streamlit as st
import numpy as np
import cv2
import wave
from PIL import Image
from pydub import AudioSegment
import io

def msgtobinary(msg):
    if type(msg) == str:
        return ''.join([format(ord(i), "08b") for i in msg])
    elif type(msg) in {bytes, np.ndarray}:
        return [format(i, "08b") for i in msg]
    elif type(msg) in {int, np.uint8}:
        return format(msg, "08b")
    else:
        raise TypeError("Input type not supported")

def encode_img_data(img, data):
    data += '*^*^*'
    binary_data = msgtobinary(data)
    length_data = len(binary_data)
    
    st.write(f"The string after binary conversion :- {binary_data}")
    st.write(f"Length of binary after conversion :- {length_data}")

    data_index = 0
    for values in img:
        for pixel in values:
            r, g, b = msgtobinary(pixel)
            if data_index < length_data:
                pixel[0] = int(r[:-1] + binary_data[data_index], 2)
                data_index += 1
            if data_index < length_data:
                pixel[1] = int(g[:-1] + binary_data[data_index], 2)
                data_index += 1
            if data_index < length_data:
                pixel[2] = int(b[:-1] + binary_data[data_index], 2)
                data_index += 1
            if data_index >= length_data:
                break

    return img

def decode_img_data(img):
    binary_data = ""
    for values in img:
        for pixel in values:
            r, g, b = msgtobinary(pixel)
            binary_data += r[-1]
            binary_data += g[-1]
            binary_data += b[-1]
    all_bytes = [binary_data[i: i + 8] for i in range(0, len(binary_data), 8)]
    decoded_data = ""
    for byte in all_bytes:
        decoded_data += chr(int(byte, 2))
        if decoded_data[-5:] == "*^*^*":
            return decoded_data[:-5]
    return ""

def convert_mp3_to_wav(mp3_file):
    audio = AudioSegment.from_mp3(mp3_file)
    wav_file = io.BytesIO()
    audio.export(wav_file, format="wav")
    wav_file.seek(0)
    return wav_file

def encode_aud_data(file, data):
    # Convert MP3 to WAV if necessary
    if file.name.endswith('.mp3'):
        file = convert_mp3_to_wav(file)
    
    song = wave.open(file, mode='rb')
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))
    
    data = data + '*^*^*'
    binary_data = msgtobinary(data)
    length_data = len(binary_data)
    
    st.write(f"The string after binary conversion :- {binary_data}")
    st.write(f"Length of binary after conversion :- {length_data}")

    data_index = 0
    for i in range(len(frame_bytes)):
        if data_index < length_data:
            frame_bytes[i] = (frame_bytes[i] & 254) | int(binary_data[data_index])
            data_index += 1
        if data_index >= length_data:
            break

    return frame_bytes, song.getparams()

def decode_aud_data(file):
    # Convert MP3 to WAV if necessary
    if file.name.endswith('.mp3'):
        file = convert_mp3_to_wav(file)
    
    song = wave.open(file, mode='rb')
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))
    
    extracted = [frame_bytes[i] & 1 for i in range(len(frame_bytes))]
    binary_data = ''.join(map(str, extracted))
    all_bytes = [binary_data[i: i + 8] for i in range(0, len(binary_data), 8)]
    decoded_data = ""
    for byte in all_bytes:
        decoded_data += chr(int(byte, 2))
        if decoded_data[-5:] == "*^*^*":
            return decoded_data[:-5]
    return ""

def main():
    st.title("Steganography Framework Built using Python")

    pages = ["Home", "Image Steganography", "Audio Steganography"]
    choice = st.sidebar.selectbox("Choose Page", pages)
    
    if choice == "Home":
        st.subheader("Welcome to the Steganography Framework")
        st.write("This application allows you to encode and decode messages within images and audio files using steganography techniques.")
        st.write("Use the sidebar to navigate to the Image Steganography or Audio Steganography sections.")
    
    elif choice == "Image Steganography":
        st.subheader("Image Steganography")
        option = st.selectbox("Choose an option", ["Encode", "Decode"])
        
        if option == "Encode":
            image_file = st.file_uploader("Upload an image", type=["jpg", "png", "tiff"])
            if image_file:
                img = Image.open(image_file)
                img = np.array(img)
                data = st.text_area("Enter the data to be encoded")
                if st.button("Encode"):
                    encoded_img = encode_img_data(img, data)
                    st.image(encoded_img, caption='Encoded Image', use_column_width=True)
                    result = Image.fromarray(encoded_img)
                    result.save("encoded_image.png")
                    st.success("Image saved as encoded_image.png")

        elif option == "Decode":
            image_file = st.file_uploader("Upload an image", type=["jpg", "png", "tiff"])
            if image_file:
                img = Image.open(image_file)
                img = np.array(img)
                if st.button("Decode"):
                    decoded_data = decode_img_data(img)
                    st.success(f"The encoded data hidden in the image was: {decoded_data}")
    
    elif choice == "Audio Steganography":
        st.subheader("Audio Steganography")
        option = st.selectbox("Choose an option", ["Encode", "Decode"])
        
        if option == "Encode":
            audio_file = st.file_uploader("Upload an audio file", type=["wav","mp3"])
            if audio_file:
                data = st.text_area("Enter the data to be encoded")
                if st.button("Encode"):
                    frame_bytes, params = encode_aud_data(audio_file, data)
                    with wave.open("encoded_audio.wav", 'wb') as fd:
                        fd.setparams(params)
                        fd.writeframes(frame_bytes)
                    st.success("Audio saved as encoded_audio.wav")

        elif option == "Decode":
            audio_file = st.file_uploader("Upload an audio file", type=["wav", "mp3"])
            if audio_file:
                if st.button("Decode"):
                    decoded_data = decode_aud_data(audio_file)
                    st.success(f"The encoded data hidden in the audio was: {decoded_data}")

