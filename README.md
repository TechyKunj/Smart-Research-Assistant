# 🤖 Smart Research Assistant

**Smart Research Assistant** is an AI-powered document analysis tool that enables intelligent comprehension, contextual Q&A, and knowledge testing using Google Gemini AI and LangChain.

---

## 🌟 Features

### Core Functionality

- 📄 **Document Upload**: PDF and TXT files up to 10MB
- 🤖 **Auto-Summary**: Generates concise 150-word summaries
- 💬 **Ask Anything**: Question answering using Gemini with document context
- 🎯 **Challenge Mode**: Comprehension questions with evaluation
- 📚 **Reference Citations**: Includes document excerpts as evidence

### Advanced Capabilities

- 🧠 **Contextual Understanding**: Vector embeddings + semantic search
- 📊 **Analytics**: Word frequencies, document stats
- 🔍 **Source Highlighting**: Shows exact supporting text
- 📈 **Confidence Scoring**: Rates answers by confidence
- 💾 **Conversation Memory**: Retains user chat history
- 🎨 **Modern UI**: Responsive and styled Streamlit app

---

## 🏗️ Architecture

**System Flow**:  
Document Upload → Text Extraction → Embedding → Gemini AI → Answer → Streamlit UI

**Components**:

- `document_processor.py` – File extraction and cleanup
- `ai_assistant.py` – Core reasoning using Gemini + LangChain
- `utils.py` – Helper utilities
- `app.py` – Streamlit frontend

---

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8+
- Google Gemini API Key
- Git

### Installation

```bash
git clone https://github.com/TechyKunj/Smart-Research-Assistant.git
cd Smart-Research-Assistant

python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt

# Create .env file with:
GEMINI_API_KEY=your_api_key_here
```

### Run App

```bash
streamlit run app.py
uvicorn backend.main:app --reload
```

Visit [http://localhost:8501](http://localhost:8501)

---

## 📁 Project Structure

```
Smart-Research-Assistant/
├── app.py
├── src/
│   ├── document_processor.py
│   ├── ai_assistant.py
│   ├── utils.py
├── .streamlit/
│   └── config.toml
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🎯 Use Cases

- **Academic**: Summarize research papers, test comprehension
- **Business**: Extract insights from reports, generate training materials
- **Legal**: Summarize contracts, identify clauses

---

## 🛠️ Developer Guide

- Modify AI behavior in `src/ai_assistant.py`
- Customize frontend in `app.py`
- Run tests:
```bash
pip install pytest
pytest tests/
```

---

## 🔒 Security & Privacy

- All processing is local (no file storage)
- API key is stored in `.env`
- HTTPS-secured communication with Gemini

---

## 📝 License

MIT License

---

## 🙌 Acknowledgements

- Google AI Studio (Gemini)
- LangChain
- Streamlit

Made with ❤️ by [@TechyKunj](https://github.com/TechyKunj)
