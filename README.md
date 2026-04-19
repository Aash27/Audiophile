# Audiophile — Pitch Detection and Feedback System

## Live Demo
Access the application here: https://huggingface.co/spaces/aashle/AudioPhile/edit/main/feedback.py
---

## Overview
Audiophile is a web-based application that analyzes musical pitch from audio input and provides structured feedback to help users improve their performance. The system supports both uploaded audio and real-time recording, detects pitch, and generates feedback using a language model.

The application is deployed on Hugging Face Spaces and integrates signal processing with AI-based feedback generation.

---

## Features
- Audio input via upload or recording  
- Pitch detection and note identification  
- Accuracy and consistency evaluation  
- Timeline-based pitch analysis  
- AI-generated feedback using Groq  
- Feedback adapted based on age group  
- Support for multiple instruments  

---

## System Workflow
1. Select instrument and age group  
2. Upload or record audio  
3. Audio is processed and normalized  
4. Pitch is detected frame-by-frame  
5. Accuracy and consistency are calculated  
6. Data is sent to Groq for feedback generation  
7. Feedback is displayed in structured format  

---
## Project Structure
audiophile/  
│  
├── app.py  
├── feedback.py  
├── pitch_utils.py  
├── instruments.py  
├── requirements.txt 

---

## Deployment (Hugging Face Spaces)

This project runs on Hugging Face Spaces using Gradio.

### Steps to Run
1. Create a new Space on Hugging Face  
2. Upload all project files  
3. Add the required API key 
4. Restart the Space  

### Required Files
- app.py  
- feedback.py  
- pitch_utils.py  
- instruments.py  
- requirements.txt  

---

## Groq API Setup

### Create API Key
1. Go to https://console.groq.com  
2. Sign in or create an account  
3. Generate a new API key  

### Add API Key to Hugging Face
1. Open your Space  
2. Go to Settings → Secrets  
3. Add:  
   Key: GROQ_API_KEY  
   Value: your_api_key_here  
4. Restart the Space  

---

## Requirements
Install dependencies listed in requirements.txt.

Main libraries used:
- gradio  
- librosa  
- numpy  
- groq  
- soundfile  

---

## Project Structure
audiophile/  
│  
├── app.py  
├── feedback.py  
├── pitch_utils.py  
├── instruments.py  
├── requirements.txt  

---

## Feedback System
The system uses Groq to generate feedback based on:
- Detected note and frequency  
- Pitch deviation (cents)  
- Accuracy percentage  
- Consistency score  
- Selected age group  

Output includes:
- Summary of performance  
- Positive aspects  
- Areas for improvement  

---
## Collaborators
- [John Thornton](https://github.com/thorntonjb)
- [Eric Tang](https://github.com/er1c84)
- [Max Kogan](https://github.com/MaxKoganUNCC)
