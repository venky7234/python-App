import streamlit as st
import openai
import moviepy.editor as mp
import os
import tempfile
from google.cloud import texttospeech
from google.cloud import speech

# Set your OpenAI API key and endpoint
openai.api_type = "azure"
openai.api_key = "22ec84421ec24230a3638d1b51e3a7dc"  # Your OpenAI API key
openai.api_base = "https://internshala.openai.azure.com/"
openai.api_version = "2024-08-01-preview"

# Google Cloud TTS setup
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\hp\\Downloads\\python-1-439317-091fa9bd26a6.json"  # Update with your path

# Function to correct transcription using OpenAI API
def correct_transcription(transcription):
    response = openai.ChatCompletion.create(
        engine="gpt-4o",  # Specify the deployment name for the Azure OpenAI service
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Correct the grammar and remove filler words like 'um', 'hmm'. Here is the text: " + transcription}
        ]
    )
    corrected_transcription = response['choices'][0]['message']['content']
    return corrected_transcription

# Function to transcribe audio from video
def transcribe_audio(video_file):
    # Save the uploaded video file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
        temp_video_file.write(video_file.read())  # Save the video to a temporary file
        video_file_path = temp_video_file.name

    # Load the video file and extract audio
    video = mp.VideoFileClip(video_file_path)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
        video.audio.write_audiofile(temp_audio_file.name)
        audio_file_path = temp_audio_file.name

    # Use Google Speech-to-Text to transcribe audio
    client = speech.SpeechClient()
    with open(audio_file_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    response = client.recognize(config=config, audio=audio)
    
    transcription = ""
    for result in response.results:
        transcription += result.alternatives[0].transcript + " "
    
    return transcription.strip()

# Function to generate audio from text using Google TTS
def generate_audio(text):
    client = texttospeech.TextToSpeechClient()
    input_text = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Wavenet-D"  # Choose an appropriate voice
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )

    # Save the audio to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
        temp_audio_file.write(response.audio_content)
        audio_file_path = temp_audio_file.name
    
    return audio_file_path

# Streamlit app layout
st.title("Video Audio Correction App")
st.write("Upload a video file with poor audio quality for correction.")

uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    # Step 1: Transcribe the audio from the video
    with st.spinner("Transcribing audio..."):
        transcription = transcribe_audio(uploaded_file)
        st.write("Transcription:")
        st.write(transcription)

    # Step 2: Correct the transcription using OpenAI
    with st.spinner("Correcting transcription..."):
        corrected_transcription = correct_transcription(transcription)
        st.write("Corrected Transcription:")
        st.write(corrected_transcription)

    # Step 3: Generate new audio from the corrected transcription
    with st.spinner("Generating audio..."):
        audio_file_path = generate_audio(corrected_transcription)
        st.write("Audio generated successfully!")

        # Provide the new audio for playback
        st.audio(audio_file_path)

        # Provide download link for the new audio
        with open(audio_file_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
            st.download_button(label="Download the audio file", data=audio_bytes, file_name="corrected_audio.mp3", mime="audio/mp3")
