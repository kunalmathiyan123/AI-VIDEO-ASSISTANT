# 🎥 AI Video Assistant

> Transform YouTube videos and local recordings into intelligent meeting insights using **Whisper AI**, **LangChain**, and **Retrieval-Augmented Generation (RAG)**.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![LangChain](https://img.shields.io/badge/LangChain-RAG-green)
![Whisper](https://img.shields.io/badge/OpenAI-Whisper-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🚀 Overview

AI Video Assistant is a GenAI-powered meeting intelligence platform that automatically converts YouTube videos and local audio/video files into structured knowledge.

The application performs:

- 🎙️ Speech-to-Text Transcription
- 📝 AI Meeting Summarization
- ✅ Action Item Extraction
- 📌 Key Decision Detection
- ❓ Open Question Identification
- 💬 Interactive RAG Chat with Meeting Content

Whether you're analysing meetings, lectures, interviews, podcasts, or webinars, AI Video Assistant helps you quickly understand and interact with the content.

---

# ✨ Features

### 🎥 Multiple Input Sources

- YouTube URLs
- MP4 Videos
- MP3 Audio
- WAV Files
- M4A Audio
- MKV Videos
- MOV Videos

---

### 🌍 Multilingual Transcription

Supports Whisper multilingual transcription with:

- Auto Language Detection
- English
- Hindi
- French
- German
- Japanese
- Korean
- Spanish
- Portuguese
- Arabic
- 90+ additional languages

---

### 📝 AI Meeting Summary

Automatically generates:

- Executive Summary
- Key Highlights
- Important Topics
- Concise Meeting Notes

---

### 📌 Meeting Intelligence

Extracts:

- Action Items
- Key Decisions
- Open Questions
- Important Discussion Points

---

### 💬 RAG Chat

Ask questions like:

- What was discussed?
- What decisions were made?
- What are my action items?
- Summarize the marketing discussion.
- Who is responsible for deployment?

The chatbot answers using only the uploaded meeting context.

---

### ⚡ Audio Processing Pipeline

- Download YouTube Audio
- Audio Conversion
- Audio Normalization
- Smart Chunking
- Whisper Transcription
- Vector Embedding
- Knowledge Base Creation

---

# 🏗️ Architecture

```
            YouTube / Local File
                     │
                     ▼
          Audio Download & Conversion
                     │
                     ▼
            Whisper Speech-to-Text
                     │
                     ▼
              Transcript Generation
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
    AI Summarization      Information Extraction
         │                       │
         └───────────┬───────────┘
                     ▼
             Chroma Vector Store
                     │
                     ▼
              LangChain RAG Chat
                     │
                     ▼
              Streamlit Dashboard
```

---

# 🛠️ Tech Stack

## Frontend

- Streamlit
- HTML/CSS
- Custom UI Components

## Backend

- Python

## AI & NLP

- OpenAI Whisper
- LangChain
- Hugging Face Embeddings

## Vector Database

- ChromaDB

## Audio Processing

- yt-dlp
- FFmpeg
- PyDub

## Utilities

- NumPy
- Pandas
- Python Dotenv

---

# 📂 Project Structure

```
AI-VIDEO-ASSISTANT/

│
├── app.py
├── main.py
├── requirements.txt
├── .env
│
├── core/
│   ├── transcriber.py
│   ├── summarizer.py
│   ├── extractor.py
│   ├── rag_engine.py
│
├── utils/
│   └── audio_processor.py
│
├── downloads/
│
└── README.md
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/AI-VIDEO-ASSISTANT.git

cd AI-VIDEO-ASSISTANT
```

---

## Create Virtual Environment (uv)

```bash
uv venv
```

Activate

Windows

```bash
.venv\Scripts\activate
```

Linux/macOS

```bash
source .venv/bin/activate
```

---

## Install Dependencies

```bash
uv sync
```

or

```bash
uv pip install -r requirements.txt
```

---

## Install FFmpeg

Windows

```bash
winget install Gyan.FFmpeg
```

Verify

```bash
ffmpeg -version
```

---

## Configure Environment

Create a `.env` file.

```env
MISTRAL_API_KEY=your_api_key

TAVILY_API_KEY=your_api_key
```

---

## Run Application

```bash
streamlit run app.py
```

or

```bash
uv run streamlit run app.py
```

---

# 📸 Screenshots

Add screenshots here.

```
images/home.png

images/result.png

images/chat.png
```

---

# 🎯 Workflow

```
Upload Video

↓

Audio Processing

↓

Whisper Transcription

↓

Meeting Summary

↓

Action Item Extraction

↓

Vector Embeddings

↓

RAG Knowledge Base

↓

Interactive AI Chat
```

---

# 🌟 Future Improvements

- Speaker Diarization
- PDF Export
- DOCX Export
- Email Meeting Summary
- Live Meeting Transcription
- Cloud Deployment
- Team Workspace
- Authentication
- Meeting History
- Multiple LLM Support

---

# 🤝 Contributing

Contributions are welcome.

1. Fork the repository

2. Create a feature branch

```bash
git checkout -b feature-name
```

3. Commit changes

```bash
git commit -m "Added feature"
```

4. Push

```bash
git push origin feature-name
```

5. Create a Pull Request

---

# 👨‍💻 Author

**Uday Singh**

B.Tech CSE Student

Passionate about AI, Generative AI, Full Stack Development, and Machine Learning.

GitHub: https://github.com/udaydhaila1926


---

# ⭐ Support

If you like this project, please consider giving it a ⭐ on GitHub!
