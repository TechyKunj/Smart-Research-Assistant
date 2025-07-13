import streamlit as st
import requests
import json
from typing import Dict, Any, List
import time
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from streamlit_option_menu import option_menu
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = "http://localhost:8000"
SUPPORTED_FORMATS = ['.pdf', '.txt', '.docx']


class SmartAssistantUI:
    """Main UI class for the Smart Research Assistant"""

    def __init__(self):
        self.setup_page_config()
        self.initialize_session_state()

    def setup_page_config(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="Smart Research Assistant",
            page_icon="🧠",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # Custom CSS for better styling
        st.markdown("""
       <style>
            body {
                background-color: #e8f5e9;
                font-family: 'Segoe UI', sans-serif;
            }

            .main-header {
                background: linear-gradient(90deg, #43cea2 0%, #185a9d 100%);
                padding: 2rem 1rem;
                border-radius: 12px;
                color: white;
                text-align: center;
                box-shadow: 0 4px 14px rgba(0,0,0,0.15);
            }

            .upload-section {
                background: #f1f8e9;
                padding: 2rem;
                border-radius: 12px;
                border: 2px dashed #66bb6a;
                color: #2e7d32;
                transition: 0.3s ease;
            }

            .upload-section:hover {
                border-color: #388e3c;
            }

            .question-card {
                background: #ffffff;
                border-left: 6px solid #8bc34a;
                padding: 1.5rem;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }

            .answer-card {
                background: #e0f2f1;
                border-left: 6px solid #26a69a;
                padding: 1.5rem;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.08);
                color: #212121 !important;  /* Fix for dark mode */
            }

            .challenge-card {
                background: #fffde7;
                border-left: 6px solid #fbc02d;
                padding: 1.5rem;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.08);
                color: #212121 !important;  /* Dark readable text */
}

            .challenge-settings {
                background: #2e7d32;
                color: white;
                padding: 1.5rem;
                border-radius: 10px;
            }

            .challenge-settings * {
                color: white !important;
            }

            .score-excellent { color: #388e3c; font-weight: bold; }
            .score-good { color: #fbc02d; font-weight: bold; }
            .score-poor { color: #e53935; font-weight: bold; }

            .metric-card {
                background: #ffffff;
                padding: 1rem;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                border-left: 5px solid #66bb6a;
                text-align: center;
            }

            .stButton > button {
                background: linear-gradient(90deg, #66bb6a 0%, #43a047 100%);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0.5rem 1.2rem;
                font-weight: 600;
                box-shadow: 0 3px 8px rgba(102, 187, 106, 0.4);
                transition: all 0.3s ease;
            }

            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 14px rgba(67, 160, 71, 0.5);
            }

            .stButton > button:active {
                transform: translateY(0);
                box-shadow: 0 2px 6px rgba(67, 160, 71, 0.3);
            }

            .insight-card {
                background: #e8f5e9;
                padding: 1.2rem;
                border-radius: 10px;
                border-left: 5px solid #43a047;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                color: #212121
            }

           .evaluation-result {
                color: #212121 !important;
                font-weight: 500;
            }

            .evaluation-result * {
                color: #212121 !important;
                opacity: 1 !important;
            }

            .sidebar .sidebar-content {
                background: linear-gradient(180deg, #43cea2 0%, #185a9d 100%);
            }
        </style>
        """, unsafe_allow_html=True)

    def initialize_session_state(self):
        """Initialize Streamlit session state variables"""
        if 'document_id' not in st.session_state:
            st.session_state.document_id = None
        if 'document_info' not in st.session_state:
            st.session_state.document_info = None
        if 'conversation_history' not in st.session_state:
            st.session_state.conversation_history = []
        if 'challenge_questions' not in st.session_state:
            st.session_state.challenge_questions = []
        if 'current_question_index' not in st.session_state:
            st.session_state.current_question_index = 0
        if 'challenge_scores' not in st.session_state:
            st.session_state.challenge_scores = []
        if 'user_preferences' not in st.session_state:
            st.session_state.user_preferences = {
                'theme': 'light',
                'auto_scroll': True,
                'show_timestamps': True
            }

    def run(self):
        """Main application entry point"""
        # Header
        st.markdown("""
        <div class="main-header">
            <h1>🧠 Smart Research Assistant</h1>
            <p>AI-powered document analysis and intelligent question answering</p>
        </div>
        """, unsafe_allow_html=True)

        # Sidebar navigation
        with st.sidebar:
            st.markdown("### Navigation")
            selected = option_menu(
                menu_title=None,
                options=["📄 Upload Document", "💬 Ask Questions",
                         "🎯 Challenge Mode", "📊 Analytics", "⚙️ Settings"],
                icons=["cloud-upload", "chat-dots",
                       "trophy", "graph-up", "gear"],
                menu_icon="cast",
                default_index=0,
                styles={
                    "container": {"padding": "0!important"},
                    "icon": {"color": "white", "font-size": "18px"},
                    "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
                    "nav-link-selected": {"background-color": "#667eea"},
                }
            )

            # Document info in sidebar
            if st.session_state.document_info:
                st.markdown("---")
                st.markdown("### 📄 Current Document")
                st.write(
                    f"**Filename:** {st.session_state.document_info['filename']}")
                st.write(
                    f"**Type:** {st.session_state.document_info['file_type']}")
                st.write(
                    f"**Words:** {st.session_state.document_info['word_count']:,}")
                st.write(
                    f"**Characters:** {st.session_state.document_info['char_count']:,}")

                # Progress indicators
                st.markdown("### 📈 Progress")
                st.write(
                    f"Questions Asked: {len(st.session_state.conversation_history)}")
                st.write(
                    f"Challenges Completed: {len(st.session_state.challenge_scores)}")

                if st.session_state.challenge_scores:
                    avg_score = sum(s['score'] for s in st.session_state.challenge_scores) / len(
                        st.session_state.challenge_scores)
                    st.write(f"Average Score: {avg_score:.1f}%")

                if st.button("🗑️ Clear Document"):
                    self.clear_session()
                    st.rerun()

            # Quick stats
            st.markdown("---")
            st.markdown("### 📊 Quick Stats")
            st.metric("Session Questions", len(
                st.session_state.conversation_history))
            if st.session_state.challenge_scores:
                avg_score = sum(s['score'] for s in st.session_state.challenge_scores) / \
                    len(st.session_state.challenge_scores)
                st.metric("Avg Challenge Score", f"{avg_score:.1f}%")

        # Main content based on navigation
        if selected == "📄 Upload Document":
            self.upload_document_page()
        elif selected == "💬 Ask Questions":
            self.ask_questions_page()
        elif selected == "🎯 Challenge Mode":
            self.challenge_mode_page()
        elif selected == "📊 Analytics":
            self.analytics_page()
        elif selected == "⚙️ Settings":
            self.settings_page()

    def upload_document_page(self):
        """Document upload interface"""
        st.markdown("## 📄 Upload Your Document")

        if st.session_state.document_info:
            # Show current document summary
            st.success(
                f"✅ Document '{st.session_state.document_info['filename']}' is ready!")

            with st.expander("📄 Document Summary", expanded=True):
                st.write(st.session_state.document_info['summary'])

            # Document statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(
                    "📊 Words", f"{st.session_state.document_info['word_count']:,}")
            with col2:
                st.metric("🔤 Characters",
                          f"{st.session_state.document_info['char_count']:,}")
            with col3:
                st.metric(
                    "📄 Type", st.session_state.document_info['file_type'].upper())
            with col4:
                upload_time = datetime.now().strftime("%H:%M")
                st.metric("⏰ Uploaded", upload_time)

            # Option to upload a new document
            st.markdown("---")
            if st.button("📄 Upload New Document", type="secondary"):
                self.clear_session()
                st.rerun()
        else:
            # Upload interface
            st.markdown("""
            <div class="upload-section">
                <h3>📁 Upload your document to get started</h3>
                <p>Supported formats: PDF, TXT, DOCX (Max 10MB)</p>
                <p>Once uploaded, you can ask questions, take challenges, and view analytics!</p>
            </div>
            """, unsafe_allow_html=True)

            uploaded_file = st.file_uploader(
                "Choose a file",
                type=['pdf', 'txt', 'docx'],
                help="Upload a PDF, TXT, or DOCX file for analysis"
            )

            if uploaded_file is not None:
                # Show file info before processing
                st.info(
                    f"📄 Selected: {uploaded_file.name} ({uploaded_file.size} bytes)")

                if st.button("🚀 Process Document", type="primary"):
                    self.process_uploaded_file(uploaded_file)

    def process_uploaded_file(self, uploaded_file):
        """Process the uploaded file"""
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            status_text.text("📤 Uploading document...")
            progress_bar.progress(25)

            # Prepare file for upload
            files = {"file": (uploaded_file.name,
                              uploaded_file.getvalue(), uploaded_file.type)}

            # Upload to API
            response = requests.post(f"{API_BASE_URL}/upload", files=files)
            response.raise_for_status()

            progress_bar.progress(50)
            status_text.text("🔍 Processing document...")

            result = response.json()

            progress_bar.progress(75)
            status_text.text("💾 Saving document info...")

            # Store document info
            st.session_state.document_id = result['document_id']
            st.session_state.document_info = {
                'filename': result['filename'],
                'file_type': result['file_type'],
                'word_count': result['word_count'],
                'char_count': result['char_count'],
                'summary': result['summary']
            }

            progress_bar.progress(100)
            status_text.text("✅ Document processed successfully!")

            st.success("🎉 Document uploaded and processed successfully!")

            # Display summary
            with st.expander("📄 Document Summary", expanded=True):
                st.write(result['summary'])

            # Show document stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Words", f"{result['word_count']:,}")
            with col2:
                st.metric("🔤 Characters", f"{result['char_count']:,}")
            with col3:
                st.metric("📄 Type", result['file_type'].upper())

            # Auto-navigate suggestion
            st.info(
                "💡 Now you can ask questions about your document or try the challenge mode!")

            time.sleep(2)
            progress_bar.empty()
            status_text.empty()
            st.rerun()

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Error uploading document: {str(e)}")
            logger.error(f"Upload error: {str(e)}")
            progress_bar.empty()
            status_text.empty()
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            logger.error(f"Unexpected error: {str(e)}")
            progress_bar.empty()
            status_text.empty()

    def ask_questions_page(self):
        """Question answering interface"""
        st.markdown("## 💬 Ask Questions")

        if not st.session_state.document_id:
            st.warning("⚠️ Please upload a document first!")
            if st.button("📄 Go to Upload"):
                st.switch_page("📄 Upload Document")
            return

        # Quick question suggestions
        st.markdown("### 💡 Quick Questions")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📝 Summarize this document"):
                st.session_state.quick_question = "Can you provide a comprehensive summary of this document?"

        with col2:
            if st.button("🔍 Key findings"):
                st.session_state.quick_question = "What are the main key findings or conclusions in this document?"

        with col3:
            if st.button("📊 Important data"):
                st.session_state.quick_question = "What important data, statistics, or numbers are mentioned?"

        # Question input
        st.markdown("### 🤔 What would you like to know?")

        # Use quick question if selected
        default_question = getattr(st.session_state, 'quick_question', '')
        if default_question:
            question = st.text_area(
                "Enter your question:",
                value=default_question,
                placeholder="Ask anything about the document...",
                height=100
            )
            # Clear the quick question
            if hasattr(st.session_state, 'quick_question'):
                delattr(st.session_state, 'quick_question')
        else:
            question = st.text_area(
                "Enter your question:",
                placeholder="Ask anything about the document...",
                height=100
            )

        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            ask_button = st.button("🚀 Ask Question", type="primary")
        with col2:
            if st.button("🧹 Clear History"):
                st.session_state.conversation_history = []
                st.rerun()
        with col3:
            if st.button("💾 Export History"):
                self.export_conversation_history()

        if ask_button and question.strip():
            self.process_question(question)

        # Display conversation history
        if st.session_state.conversation_history:
            st.markdown("### 📜 Conversation History")

            # Search through history
            search_term = st.text_input(
                "🔍 Search conversation history:", placeholder="Search questions or answers...")

            filtered_history = st.session_state.conversation_history
            if search_term:
                filtered_history = [
                    exchange for exchange in st.session_state.conversation_history
                    if search_term.lower() in exchange['question'].lower() or
                    search_term.lower() in exchange['answer'].lower()
                ]

            for i, exchange in enumerate(reversed(filtered_history)):
                original_index = len(
                    st.session_state.conversation_history) - len(filtered_history) + i + 1
                with st.expander(f"Q{original_index}: {exchange['question'][:50]}...", expanded=i == 0):
                    st.markdown(f"**❓ Question:** {exchange['question']}")
                    st.markdown(f"**🤖 Answer:** {exchange['answer']}")
                    st.markdown(
                        f"**📖 Justification:** {exchange['justification']}")
                    if exchange.get('snippet'):
                        st.markdown(
                            f"**📝 Relevant Text:** *{exchange['snippet']}*")
                    if st.session_state.user_preferences['show_timestamps']:
                        st.markdown(f"**⏰ Time:** {exchange['timestamp']}")

                    # Rating system
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        rating = st.selectbox(
                            "Rate this answer:",
                            options=[0, 1, 2, 3, 4, 5],
                            format_func=lambda x: "⭐" * x if x > 0 else "Not rated",
                            key=f"rating_{original_index}"
                        )
                    with col2:
                        if st.button(f"💾 Save Answer", key=f"save_{original_index}"):
                            st.success("Answer saved to your notes!")

    def process_question(self, question: str):
        """Process a user question"""
        with st.spinner("🤖 Analyzing question and generating answer..."):
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                status_text.text("🔍 Analyzing question...")
                progress_bar.progress(25)

                # Prepare request
                request_data = {
                    "document_id": st.session_state.document_id,
                    "question": question,
                    # Last 3 exchanges
                    "conversation_history": st.session_state.conversation_history[-3:]
                }

                progress_bar.progress(50)
                status_text.text("🤖 Generating answer...")

                # Send to API
                response = requests.post(
                    f"{API_BASE_URL}/ask", json=request_data)
                response.raise_for_status()

                progress_bar.progress(75)
                status_text.text("📝 Formatting response...")

                result = response.json()

                # Add to conversation history
                exchange = {
                    "question": question,
                    "answer": result['answer'],
                    "justification": result['justification'],
                    "snippet": result.get('snippet', ''),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                st.session_state.conversation_history.append(exchange)

                progress_bar.progress(100)
                status_text.text("✅ Answer ready!")

                # Display the answer
                st.markdown("---")
                st.markdown("### 🤖 Answer")

                with st.container():
                    st.markdown(f"""
                    <div class="answer-card">
                        <h4>💡 Answer:</h4>
                        <p>{result['answer']}</p>
                        
                        <h4>📖 Justification:</h4>
                        <p>{result['justification']}</p>
                        
                        {f"<h4>📝 Relevant Text:</h4><p><em>{result.get('snippet', '')}</em></p>" if result.get('snippet') else ""}
                    </div>
                    """, unsafe_allow_html=True)

                # Auto-scroll to answer if enabled
                if st.session_state.user_preferences['auto_scroll']:
                    st.markdown(
                        """
                        <script>
                            window.scrollTo(0, document.body.scrollHeight);
                        </script>
                        """,
                        unsafe_allow_html=True
                    )

                time.sleep(1)
                progress_bar.empty()
                status_text.empty()
                st.rerun()

            except requests.exceptions.RequestException as e:
                st.error(f"❌ Error processing question: {str(e)}")
                logger.error(f"Question processing error: {str(e)}")
                progress_bar.empty()
                status_text.empty()
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
                logger.error(f"Unexpected error: {str(e)}")
                progress_bar.empty()
                status_text.empty()

    def challenge_mode_page(self):
        """Challenge mode interface"""
        st.markdown("## 🎯 Challenge Mode")

        if not st.session_state.document_id:
            st.warning("⚠️ Please upload a document first!")
            if st.button("📄 Go to Upload"):
                st.switch_page("📄 Upload Document")
            return

        # Challenge mode introduction
        if not st.session_state.challenge_questions:
            st.markdown("""
            <div class="challenge-card">
                <h3>🎯 Welcome to Challenge Mode!</h3>
                <p>Test your understanding of the document with AI-generated questions.</p>
                <ul>
                    <li>📚 Questions are generated based on your document content</li>
                    <li>🎚️ Multiple difficulty levels available</li>
                    <li>📊 Get detailed feedback on your answers</li>
                    <li>🏆 Track your progress and improvement</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

            # Challenge options
            st.markdown("### ⚙️ Challenge Settings")
            col1, col2 = st.columns(2)

            with col1:
                difficulty = st.selectbox(
                    "Select difficulty level:",
                    options=['easy', 'medium', 'hard', 'mixed'],
                    format_func=lambda x: {
                        'easy': '🟢 Easy',
                        'medium': '🟡 Medium',
                        'hard': '🔴 Hard',
                        'mixed': '🌈 Mixed'
                    }[x]
                )

            with col2:
                question_count = st.slider("Number of questions:", 1, 10, 5)

            if st.button("🎲 Generate Challenge Questions", type="primary"):
                self.generate_challenge_questions(question_count, difficulty)

            # Previous challenges
            if st.session_state.challenge_scores:
                st.markdown("---")
                st.markdown("### 📊 Previous Challenges")
                avg_score = sum(s['score'] for s in st.session_state.challenge_scores) / \
                    len(st.session_state.challenge_scores)
                st.metric("Average Score", f"{avg_score:.1f}%")

                if st.button("🎲 Start New Challenge"):
                    st.session_state.challenge_questions = []
                    st.session_state.current_question_index = 0
                    st.session_state.challenge_scores = []
                    st.rerun()

            return

        # Display challenge questions
        st.markdown(
            f"### 🎯 Challenge Questions ({len(st.session_state.challenge_questions)} total)")

        # Progress bar
        progress = (st.session_state.current_question_index + 1) / \
            len(st.session_state.challenge_questions)
        st.progress(progress)

        # Question navigation
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            if st.button("⬅️ Previous") and st.session_state.current_question_index > 0:
                st.session_state.current_question_index -= 1
                st.rerun()
        with col2:
            st.markdown(
                f"**Question {st.session_state.current_question_index + 1} of {len(st.session_state.challenge_questions)}**")
        with col3:
            if st.button("➡️ Next") and st.session_state.current_question_index < len(st.session_state.challenge_questions) - 1:
                st.session_state.current_question_index += 1
                st.rerun()

        # Current question
        current_q = st.session_state.challenge_questions[st.session_state.current_question_index]

        # Difficulty indicator
        difficulty_colors = {
            'easy': '#28a745',
            'medium': '#ffc107',
            'hard': '#dc3545'
        }

        st.markdown(f"""
        <div class="challenge-card">
            <h4>🎯 Question {st.session_state.current_question_index + 1}:</h4>
            <p>{current_q['question']}</p>
            <p><strong>Difficulty:</strong> 
                <span style="color: {difficulty_colors.get(current_q['difficulty'], '#000')}">
                    {current_q['difficulty'].title()}
                </span>
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Answer input
        user_answer = st.text_area(
            "Your answer:",
            placeholder="Enter your answer here...",
            height=100,
            key=f"answer_{st.session_state.current_question_index}"
        )

        # Answer actions
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("✅ Submit Answer", type="primary"):
                if user_answer.strip():
                    self.evaluate_answer(current_q, user_answer)
                else:
                    st.warning("⚠️ Please enter an answer!")

        with col2:
            if st.button("💡 Hint"):
                st.info(
                    f"💡 **Hint:** {current_q.get('hint', 'Think about the main concepts discussed in the document.')}")

        with col3:
            if st.button("⏭️ Skip Question"):
                if st.session_state.current_question_index < len(st.session_state.challenge_questions) - 1:
                    st.session_state.current_question_index += 1
                    st.rerun()
                else:
                    st.info("This is the last question!")

        # Show previous scores for this question
        existing_score = None
        for score in st.session_state.challenge_scores:
            if score['question_index'] == st.session_state.current_question_index:
                existing_score = score
                break

        if existing_score:
            st.markdown("---")
            st.markdown("### 📊 Previous Attempt")
            self.display_evaluation(existing_score)

        # Challenge completion check
        if len(st.session_state.challenge_scores) == len(st.session_state.challenge_questions):
            st.markdown("---")
            st.markdown("### 🏆 Challenge Complete!")
            avg_score = sum(s['score'] for s in st.session_state.challenge_scores) / \
                len(st.session_state.challenge_scores)

            if avg_score >= 80:
                st.balloons()
                st.success(
                    f"🎉 Excellent work! Average score: {avg_score:.1f}%")
            elif avg_score >= 60:
                st.success(f"👍 Good job! Average score: {avg_score:.1f}%")
            else:
                st.info(f"📚 Keep practicing! Average score: {avg_score:.1f}%")

            if st.button("🎲 Start New Challenge"):
                st.session_state.challenge_questions = []
                st.session_state.current_question_index = 0
                st.session_state.challenge_scores = []
                st.rerun()

    def generate_challenge_questions(self, count: int = 5, difficulty: str = 'mixed'):
        """Generate challenge questions"""
        with st.spinner("🎲 Generating challenge questions..."):
            try:
                request_data = {
                    "document_id": st.session_state.document_id,
                    "count": count,
                    "difficulty": difficulty
                }

                response = requests.post(
                    f"{API_BASE_URL}/challenge", json=request_data)
                response.raise_for_status()

                result = response.json()
                st.session_state.challenge_questions = result['questions']
                st.session_state.current_question_index = 0
                st.session_state.challenge_scores = []

                st.success(f"✅ {count} challenge questions generated!")
                st.rerun()

            except requests.exceptions.RequestException as e:
                st.error(f"❌ Error generating questions: {str(e)}")
                logger.error(f"Challenge generation error: {str(e)}")
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
                logger.error(f"Unexpected error: {str(e)}")

    def evaluate_answer(self, question_data: Dict, user_answer: str):
        """Evaluate user's answer"""
        with st.spinner("📊 Evaluating your answer..."):
            try:
                request_data = {
                    "document_id": st.session_state.document_id,
                    "question": question_data['question'],
                    "user_answer": user_answer,
                    "correct_answer": question_data['correct_answer']
                }

                response = requests.post(
                    f"{API_BASE_URL}/evaluate", json=request_data)
                response.raise_for_status()

                result = response.json()

                # Store score
                score_data = {
                    "question_index": st.session_state.current_question_index,
                    "score": result['score'],
                    "feedback": result['feedback'],
                    "reference": result['reference']
                }

                # Update or add score
                existing_score = None
                for i, score in enumerate(st.session_state.challenge_scores):
                    if score['question_index'] == st.session_state.current_question_index:
                        existing_score = i
                        break

                if existing_score is not None:
                    st.session_state.challenge_scores[existing_score] = score_data
                else:
                    st.session_state.challenge_scores.append(score_data)

                # Display evaluation
                self.display_evaluation(result)

            except requests.exceptions.RequestException as e:
                st.error(f"❌ Error evaluating answer: {str(e)}")
                logger.error(f"Answer evaluation error: {str(e)}")
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
                logger.error(f"Unexpected error: {str(e)}")

    def display_evaluation(self, result: Dict):
        """Display answer evaluation"""
        score = result['score']

        # Determine score color and emoji
        if score >= 80:
            score_class = "score-excellent"
            emoji = "🎉"
            message = "Excellent work!"
        elif score >= 60:
            score_class = "score-good"
            emoji = "👍"
            message = "Good job!"
        else:
            score_class = "score-poor"
            emoji = "📚"
            message = "Keep practicing!"

        st.markdown(f"""
        <div class="answer-card">
            <h4>{emoji} Evaluation Result - {message}</h4>
            <p><strong>Score:</strong> <span class="{score_class}">{score}/100</span></p>
            <p><strong>Feedback:</strong> {result['feedback']}</p>
            <p><strong>Reference:</strong> {result['reference']}</p>
        </div>
        """, unsafe_allow_html=True)

    def analytics_page(self):
        """Analytics and progress tracking"""
        st.markdown("## 📊 Analytics")

        if not st.session_state.document_id:
            st.warning("⚠️ Please upload a document first!")
            if st.button("📄 Go to Upload"):
                st.switch_page("📄 Upload Document")
            return

        # Document statistics
        if st.session_state.document_info:
            st.markdown("### 📄 Document Statistics")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(
                    "📊 Words", f"{st.session_state.document_info['word_count']:,}")
            with col2:
                st.metric("🔤 Characters",
                          f"{st.session_state.document_info['char_count']:,}")
            with col3:
                st.metric("💬 Questions Asked", len(
                    st.session_state.conversation_history))
            with col4:
                st.metric("🎯 Challenges Completed", len(
                    st.session_state.challenge_scores))

        # Challenge performance
        if st.session_state.challenge_scores:
            st.markdown("### 🎯 Challenge Performance")

            scores = [s['score'] for s in st.session_state.challenge_scores]
            avg_score = sum(scores) / len(scores)

            col1, col2 = st.columns(2)

            with col1:
                # Score distribution
                fig = go.Figure(data=[go.Bar(
                    x=[f"Q{s['question_index']+1}" for s in st.session_state.challenge_scores],
                    y=scores,
                    marker_color=[
                        '#28a745' if s >= 80 else '#ffc107' if s >= 60 else '#dc3545' for s in scores],
                    text=scores,
                    textposition='auto'
                )])
                fig.update_layout(
                    title="Challenge Question Scores",
                    xaxis_title="Question",
                    yaxis_title="Score",
                    showlegend=False,
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Average score gauge
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=avg_score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Average Score"},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 60], 'color': "lightgray"},
                            {'range': [60, 80], 'color': "yellow"},
                            {'range': [80, 100], 'color': "green"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

            # Performance insights
            st.markdown("### 💡 Performance Insights")

            # Calculate insights
            max_score = max(scores)
            min_score = min(scores)
            score_range = max_score - min_score

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"""
                <div class="insight-card">
                    <h4>📈 Score Analysis</h4>
                    <p><strong>Highest Score:</strong> {max_score}%</p>
                    <p><strong>Lowest Score:</strong> {min_score}%</p>
                    <p><strong>Score Range:</strong> {score_range}%</p>
                    <p><strong>Consistency:</strong> {'High' if score_range < 20 else 'Medium' if score_range < 40 else 'Low'}</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                # Performance trend
                if len(scores) > 1:
                    trend = "improving" if scores[-1] > scores[0] else "declining" if scores[-1] < scores[0] else "stable"
                    trend_emoji = "📈" if trend == "improving" else "📉" if trend == "declining" else "➡️"

                    st.markdown(f"""
                    <div class="insight-card">
                        <h4>{trend_emoji} Performance Trend</h4>
                        <p><strong>Overall Trend:</strong> {trend.title()}</p>
                        <p><strong>First Score:</strong> {scores[0]}%</p>
                        <p><strong>Latest Score:</strong> {scores[-1]}%</p>
                        <p><strong>Improvement:</strong> {scores[-1] - scores[0]:+.1f}%</p>
                    </div>
                    """, unsafe_allow_html=True)

        # Question asking patterns
        if st.session_state.conversation_history:
            st.markdown("### 💬 Question Asking Patterns")

            # Questions over time
            question_times = [datetime.strptime(
                q['timestamp'], "%Y-%m-%d %H:%M:%S") for q in st.session_state.conversation_history]
            question_hours = [t.hour for t in question_times]

            col1, col2 = st.columns(2)

            with col1:
                # Questions by hour
                hour_counts = {}
                for hour in question_hours:
                    hour_counts[hour] = hour_counts.get(hour, 0) + 1

                fig = go.Figure(data=[go.Bar(
                    x=list(hour_counts.keys()),
                    y=list(hour_counts.values()),
                    marker_color='#667eea'
                )])
                fig.update_layout(
                    title="Questions Asked by Hour",
                    xaxis_title="Hour of Day",
                    yaxis_title="Number of Questions",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Question length distribution
                question_lengths = [len(q['question'].split())
                                    for q in st.session_state.conversation_history]

                fig = go.Figure(data=[go.Histogram(
                    x=question_lengths,
                    nbinsx=10,
                    marker_color='#764ba2'
                )])
                fig.update_layout(
                    title="Question Length Distribution",
                    xaxis_title="Words in Question",
                    yaxis_title="Frequency",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)

        # Summary statistics
        st.markdown("### 📊 Session Summary")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            session_duration = "N/A"
            if st.session_state.conversation_history:
                first_question = datetime.strptime(
                    st.session_state.conversation_history[0]['timestamp'], "%Y-%m-%d %H:%M:%S")
                last_question = datetime.strptime(
                    st.session_state.conversation_history[-1]['timestamp'], "%Y-%m-%d %H:%M:%S")
                duration = last_question - first_question
                session_duration = f"{duration.seconds // 60} min"

            st.metric("⏱️ Session Duration", session_duration)

        with col2:
            avg_question_length = 0
            if st.session_state.conversation_history:
                total_words = sum(len(q['question'].split())
                                  for q in st.session_state.conversation_history)
                avg_question_length = total_words / \
                    len(st.session_state.conversation_history)

            st.metric("📝 Avg Question Length",
                      f"{avg_question_length:.1f} words")

        with col3:
            engagement_score = 0
            if st.session_state.document_info:
                questions_per_1000_words = (len(
                    st.session_state.conversation_history) / st.session_state.document_info['word_count']) * 1000
                engagement_score = min(questions_per_1000_words * 10, 100)

            st.metric("📈 Engagement Score", f"{engagement_score:.1f}%")

        with col4:
            learning_progress = 0
            if st.session_state.challenge_scores:
                learning_progress = sum(
                    s['score'] for s in st.session_state.challenge_scores) / len(st.session_state.challenge_scores)

            st.metric("🎓 Learning Progress", f"{learning_progress:.1f}%")

        # Export options
        st.markdown("### 💾 Export Options")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📊 Export Analytics"):
                self.export_analytics()

        with col2:
            if st.button("💬 Export Conversations"):
                self.export_conversation_history()

        with col3:
            if st.button("🎯 Export Challenge Results"):
                self.export_challenge_results()

    def settings_page(self):
        """Settings and preferences page"""
        global API_BASE_URL  # Move this to the top

        st.markdown("## ⚙️ Settings")

        # User preferences
        st.markdown("### 👤 User Preferences")

        col1, col2 = st.columns(2)

        with col1:
            st.session_state.user_preferences['show_timestamps'] = st.checkbox(
                "Show timestamps in conversation history",
                value=st.session_state.user_preferences['show_timestamps']
            )

            st.session_state.user_preferences['auto_scroll'] = st.checkbox(
                "Auto-scroll to new answers",
                value=st.session_state.user_preferences['auto_scroll']
            )

            theme = st.selectbox(
                "Theme",
                options=['light', 'dark', 'auto'],
                index=['light', 'dark', 'auto'].index(
                    st.session_state.user_preferences['theme']),
                format_func=lambda x: {'light': '☀️ Light',
                                       'dark': '🌙 Dark', 'auto': '🤖 Auto'}[x]
            )
            st.session_state.user_preferences['theme'] = theme

        with col2:
            # API settings
            st.markdown("#### 🔧 API Settings")

            new_api_url = st.text_input(
                "API Base URL",
                value=API_BASE_URL,
                help="Change this if your API is running on a different URL"
            )

            if new_api_url != API_BASE_URL:
                if st.button("🔄 Update API URL"):
                    API_BASE_URL = new_api_url
                    st.success("API URL updated!")
                    st.rerun()

            # Test API connection
            if st.button("🔍 Test API Connection"):
                self.test_api_connection()

        # Rest of the method remains the same...
        # Data management
        st.markdown("### 💾 Data Management")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🗑️ Clear All Data", type="secondary"):
                if st.checkbox("I understand this will delete all session data"):
                    self.clear_all_data()
                    st.success("All data cleared!")
                    st.rerun()

        with col2:
            if st.button("💾 Export All Data"):
                self.export_all_data()

        with col3:
            uploaded_data = st.file_uploader(
                "Import Session Data",
                type=['json'],
                help="Upload previously exported session data"
            )

            if uploaded_data is not None:
                if st.button("📥 Import Data"):
                    self.import_session_data(uploaded_data)

        # System information
        st.markdown("### 🔍 System Information")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
            **Session Statistics:**
            - Documents processed: {1 if st.session_state.document_id else 0}
            - Questions asked: {len(st.session_state.conversation_history)}
            - Challenges completed: {len(st.session_state.challenge_scores)}
            - Session started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """)

        with col2:
            st.markdown(f"""
            **System Configuration:**
            - API URL: {API_BASE_URL}
            - Supported formats: {', '.join(SUPPORTED_FORMATS)}
            - Theme: {st.session_state.user_preferences['theme']}
            - Auto-scroll: {st.session_state.user_preferences['auto_scroll']}
            """)

        # About section
        st.markdown("### ℹ️ About")
        st.markdown("""
        **Smart Research Assistant** v1.0
        
        An AI-powered document analysis tool that helps you:
        - 📄 Upload and analyze documents
        - 💬 Ask intelligent questions
        - 🎯 Test your understanding with challenges
        - 📊 Track your learning progress
        
        Built with Streamlit and powered by advanced AI models.
        """)

    def test_api_connection(self):
        """Test API connection"""
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            response.raise_for_status()
            st.success("✅ API connection successful!")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ API connection failed: {str(e)}")
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")

    def clear_session(self):
        """Clear current session data"""
        st.session_state.document_id = None
        st.session_state.document_info = None
        st.session_state.conversation_history = []
        st.session_state.challenge_questions = []
        st.session_state.current_question_index = 0
        st.session_state.challenge_scores = []

    def clear_all_data(self):
        """Clear all session data"""
        for key in list(st.session_state.keys()):
            if key != 'user_preferences':
                del st.session_state[key]
        self.initialize_session_state()

    def export_conversation_history(self):
        """Export conversation history"""
        if not st.session_state.conversation_history:
            st.warning("No conversation history to export!")
            return

        export_data = {
            'document_info': st.session_state.document_info,
            'conversation_history': st.session_state.conversation_history,
            'export_timestamp': datetime.now().isoformat()
        }

        st.download_button(
            label="📥 Download Conversation History",
            data=json.dumps(export_data, indent=2),
            file_name=f"conversation_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

    def export_challenge_results(self):
        """Export challenge results"""
        if not st.session_state.challenge_scores:
            st.warning("No challenge results to export!")
            return

        export_data = {
            'document_info': st.session_state.document_info,
            'challenge_questions': st.session_state.challenge_questions,
            'challenge_scores': st.session_state.challenge_scores,
            'export_timestamp': datetime.now().isoformat()
        }

        st.download_button(
            label="📥 Download Challenge Results",
            data=json.dumps(export_data, indent=2),
            file_name=f"challenge_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

    def export_analytics(self):
        """Export analytics data"""
        if not st.session_state.document_info:
            st.warning("No analytics data to export!")
            return

        # Calculate analytics
        scores = [s['score']
                  for s in st.session_state.challenge_scores] if st.session_state.challenge_scores else []

        analytics_data = {
            'document_info': st.session_state.document_info,
            'session_stats': {
                'questions_asked': len(st.session_state.conversation_history),
                'challenges_completed': len(st.session_state.challenge_scores),
                'average_score': sum(scores) / len(scores) if scores else 0,
                'max_score': max(scores) if scores else 0,
                'min_score': min(scores) if scores else 0
            },
            'export_timestamp': datetime.now().isoformat()
        }

        st.download_button(
            label="📥 Download Analytics",
            data=json.dumps(analytics_data, indent=2),
            file_name=f"analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

    def export_all_data(self):
        """Export all session data"""
        export_data = {
            'document_id': st.session_state.document_id,
            'document_info': st.session_state.document_info,
            'conversation_history': st.session_state.conversation_history,
            'challenge_questions': st.session_state.challenge_questions,
            'challenge_scores': st.session_state.challenge_scores,
            'current_question_index': st.session_state.current_question_index,
            'user_preferences': st.session_state.user_preferences,
            'export_timestamp': datetime.now().isoformat()
        }

        st.download_button(
            label="📥 Download All Session Data",
            data=json.dumps(export_data, indent=2),
            file_name=f"session_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

    def import_session_data(self, uploaded_file):
        """Import session data from file"""
        try:
            data = json.loads(uploaded_file.read().decode('utf-8'))

            # Validate data structure
            required_keys = ['document_info', 'conversation_history',
                             'challenge_questions', 'challenge_scores']

            for key in required_keys:
                if key in data:
                    st.session_state[key] = data[key]

            if 'user_preferences' in data:
                st.session_state.user_preferences.update(
                    data['user_preferences'])

            if 'document_id' in data:
                st.session_state.document_id = data['document_id']

            if 'current_question_index' in data:
                st.session_state.current_question_index = data['current_question_index']

            st.success("✅ Session data imported successfully!")
            st.rerun()

        except json.JSONDecodeError:
            st.error("❌ Invalid JSON file!")
        except Exception as e:
            st.error(f"❌ Error importing data: {str(e)}")


def main():
    """Main application function"""
    app = SmartAssistantUI()
    app.run()


if __name__ == "__main__":
    main()
