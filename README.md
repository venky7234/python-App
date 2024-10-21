# python-App
This project is a "Video Audio Correction App" that allows users to upload a video with poor audio quality (such as grammar mistakes or filler words like 'um' and 'hmm'). The app performs three key steps:

Transcription: Extracts and transcribes the audio from the uploaded video using Google’s Speech-to-Text service.
Correction: The transcription is passed to OpenAI’s GPT-4o model to fix grammatical errors and remove unwanted filler words.
Audio Generation: Google’s Text-to-Speech service then generates clean, corrected audio from the improved text, which is synced back with the video.
This tool helps create polished, AI-enhanced audio for videos, improving clarity and quality.
