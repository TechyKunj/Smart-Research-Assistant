# 🔬 Smart Research Assistant

A sophisticated AI-powered document analysis tool that enables intelligent comprehension, contextual Q&A, and knowledge testing using Google Gemini AI and LangChain.

---

## 🌟 Features

### Core Functionality
- 📄 Document Upload (PDF, TXT up to 10MB)
- 🤖 Auto-Summary (~150 words)
- 💬 Ask Anything (Gemini-powered contextual Q&A)
- 🎯 Challenge Mode (Comprehension questions)
- 📚 Reference Citations (Supports answers with source text)

### Advanced Features
- 🧠 Semantic Search using FAISS
- 📊 Document Analytics: word frequency & stats
- 🔍 Source Highlighting for answers
- 📈 Confidence Scoring
- 💾 Conversation Memory
- 🎨 Streamlit UI with animations

---

## 🏗️ Architecture

**Flow:** Document Upload → Text Extraction → Vector Embedding → Gemini LLM → Streamlit UI

**Key Components:**
- `backend/` – FastAPI backend and core logic
  - `main.py` – FastAPI server
  - `config.py` – Environment configuration
  - `document_processor.py` – PDF/TXT handling
  - `llm_service.py` – Gemini API logic
  - `api_models.py` – Request/response models
- `fronted/` – Streamlit frontend
  - `app.py` – Main UI logic

---

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.8+
- Google Gemini API Key
- Git

### 1. Clone the repository
```bash
git clone https://github.com/TechyKunj/Smart-Research-Assistant.git
cd Smart-Research-Assistant
```

### 2. Create and activate virtual environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your API key
Create a file named `.env` in the root and add:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 🚀 Running the App

### Start FastAPI backend
```bash
cd backend
uvicorn main:app --reload
```

### Start Streamlit frontend
```bash
cd fronted
streamlit run app.py
```

Access the app at: [http://localhost:8501](http://localhost:8501)

---

## 📁 Directory Overview

```
Smart-Research-Assistant/
├── .venv/
├── backend/
│   ├── api_models.py
│   ├── config.py
│   ├── document_processor.py
│   ├── llm_service.py
│   └── main.py
├── fronted/
│   └── app.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🛡️ Security & Privacy

- No permanent document storage
- `.env` file is ignored from version control
- API communication is HTTPS-secured

---

## 📝 License

MIT License

---

## 🙌 Acknowledgements

- [Google Gemini API](https://ai.google.dev)
- [LangChain](https://www.langchain.com/)
- [Streamlit](https://streamlit.io/)

Made with ❤️ by [@TechyKunj](https://github.com/TechyKunj)

---

## 🎬 Demo Video

Watch the full walkthrough here:  
📺 [Smart Research Assistant - YouTube Demo](https://youtu.be/kCn1rpg3iHE)

