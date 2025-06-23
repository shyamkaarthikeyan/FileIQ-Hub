import streamlit as st
import google.generativeai as genai
from utils import extract_text_from_pdf, extract_text_from_txt, get_summary_prompt, get_ask_prompt, get_challenge_prompt, get_evaluate_prompt
import re

st.set_page_config(page_title="FileIQ Hub: Summarize, Ask, and Challenge", layout="centered", page_icon="📄")
st.title("FileIQ Hub: Summarize, Ask, and Challenge")
st.write("Upload a PDF or TXT file, get a summary, ask questions, or challenge yourself!")

genai.configure(api_key="AIzaSyBfkcl6TUjyWLfsl5g0_v-Q_NAmjTmNiSE")
model = genai.GenerativeModel('gemini-1.5-flash')

# --- Session State Initialization ---
if "step" not in st.session_state:
    st.session_state["step"] = 0
if "doc_text" not in st.session_state:
    st.session_state["doc_text"] = None
if "summary" not in st.session_state:
    st.session_state["summary"] = None
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "challenge_started" not in st.session_state:
    st.session_state["challenge_started"] = False
if "challenge_questions" not in st.session_state:
    st.session_state["challenge_questions"] = []
if "challenge_index" not in st.session_state:
    st.session_state["challenge_index"] = 0
if "challenge_answers" not in st.session_state:
    st.session_state["challenge_answers"] = []
if "challenge_results" not in st.session_state:
    st.session_state["challenge_results"] = []

def reset_all():
    st.session_state["summary"] = None
    st.session_state["chat_history"] = []
    st.session_state["challenge_started"] = False
    st.session_state["challenge_questions"] = []
    st.session_state["challenge_index"] = 0
    st.session_state["challenge_answers"] = []
    st.session_state["challenge_results"] = []

# --- Step 0: File Upload ---
if st.session_state["step"] == 0:
    st.header("Upload a File")
    st.write("Supported formats: PDF, TXT. After upload, you'll get a summary and can interact with your file.")
    if st.session_state["doc_text"]:
        st.info("A file is already uploaded. Remove it to upload a new one.")
        if st.button("Remove File"):
            st.session_state["doc_text"] = None
            reset_all()
            st.rerun()
    else:
        uploaded_file = st.file_uploader("Choose a PDF or TXT file", type=["pdf", "txt"])
        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                doc_text = extract_text_from_pdf(uploaded_file)
            else:
                doc_text = extract_text_from_txt(uploaded_file)
            # No truncation
            st.session_state["doc_text"] = doc_text
            reset_all()
            st.session_state["step"] = 1
            st.rerun()

# --- Step 1: Auto Summary ---
elif st.session_state["step"] == 1:
    st.header("File Summary")
    if not st.session_state.get("doc_text"):
        st.warning("No file found. Please upload a file first.")
        st.session_state["step"] = 0
        st.rerun()
    if st.session_state.get("summary") is None:
        with st.spinner("Generating summary..."):
            prompt = get_summary_prompt(st.session_state["doc_text"])
            response = model.generate_content(prompt)
            summary = response.text.strip()
            st.session_state["summary"] = summary
    st.write(st.session_state["summary"])
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Back"):
            st.session_state["step"] = 0
            st.rerun()
    with col2:
        if st.button("Continue"):
            st.session_state["step"] = 2
            st.rerun()

# --- Step 2: Interaction Modes ---
elif st.session_state["step"] == 2:
    st.header("Interact with Your File")
    mode = st.radio("Choose a mode:", ["Ask Anything", "Challenge Me"], horizontal=True)
    st.divider()
    # --- Ask Anything Mode ---
    if mode == "Ask Anything":
        st.subheader("Ask Anything")
        st.caption("Type your question below. Answers are always justified with a snippet from the file.")
        # Social media chat-like UI (no colors, just alignment)
        chat_container = st.container()
        with chat_container:
            for entry in st.session_state["chat_history"]:
                st.markdown(f"<div style='border-radius:8px; padding:0.7em 1em; margin-bottom:0.5em; max-width:80%; margin-left:auto; text-align:right; border:1px solid #eee;'><b>You:</b> {entry['question']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='border-radius:8px; padding:0.7em 1em; margin-bottom:1.2em; max-width:80%; margin-right:auto; text-align:left; border:1px solid #eee;'><b>Assistant:</b> {entry['answer']}<br><span style='color:#888; font-size:0.9em;'>Snippet: {entry['snippet']}</span></div>", unsafe_allow_html=True)
        # Use a callback to clear the input after sending
        def send_message():
            user_question = st.session_state.get("ask_input_temp", "")
            if user_question:
                with st.spinner("Getting answer..."):
                    prompt = get_ask_prompt(st.session_state["doc_text"], user_question)
                    response = model.generate_content(prompt)
                    answer = response.text.strip()
                    snippet_prompt = (
                        f"From the file below, extract the exact sentence or paragraph that justifies the following answer.\n"
                        f"File Content:\n{st.session_state['doc_text']}\n\nAnswer: {answer}"
                    )
                    snippet_response = model.generate_content(snippet_prompt)
                    snippet = snippet_response.text.strip()
                st.session_state["chat_history"].append({
                    "question": user_question,
                    "answer": answer,
                    "snippet": snippet
                })
                st.session_state["ask_input_temp"] = ""
        col1, col2 = st.columns([8, 1])
        with col1:
            user_question = st.text_input(
                "Type a message...",
                placeholder="Ask a question about your file",
                key="ask_input_temp"
            )
        with col2:
            send_btn = st.button("Send", key="ask_btn", on_click=send_message)
        # Auto-scroll to bottom (Streamlit does this by default on rerun)
    # --- Challenge Me Mode ---
    elif mode == "Challenge Me":
        st.subheader("Challenge Me: Test Your Understanding!")
        st.caption("The assistant will generate 3 logic/comprehension questions from your file. Answer and get instant feedback!")
        if not st.session_state["challenge_started"]:
            if st.button("Start Challenge", type="primary"):
                st.session_state["challenge_started"] = True
                st.session_state["challenge_questions"] = []
                st.session_state["challenge_index"] = 0
                st.session_state["challenge_answers"] = []
                st.session_state["challenge_results"] = []
                st.rerun()
        else:
            if not st.session_state["challenge_questions"]:
                with st.spinner("Generating questions..."):
                    prompt = get_challenge_prompt(st.session_state["doc_text"])
                    response = model.generate_content(prompt)
                    raw = response.text.strip()
                    raw = re.sub(r"^Here are.*questions.*?:", "", raw, flags=re.IGNORECASE|re.DOTALL)
                    questions = re.split(r"\n?\s*\d+\.\s+|\n", raw)
                    questions = [q.strip() for q in questions if q.strip() and len(q.strip().split()) > 2]
                    st.session_state["challenge_questions"] = questions[:3]
            idx = st.session_state["challenge_index"]
            questions = st.session_state["challenge_questions"]
            if idx < len(questions):
                st.markdown(f"**Question:** {questions[idx]}")
                user_ans = st.text_input("Your Answer:", key=f"ans_{idx}", placeholder="Type your answer here...")
                submit_btn = st.button("Submit Answer", key=f"submit_{idx}")
                if submit_btn:
                    with st.spinner("Evaluating answer..."):
                        eval_prompt = get_evaluate_prompt(st.session_state["doc_text"], questions[idx], user_ans)
                        eval_response = model.generate_content(eval_prompt)
                        result = eval_response.text.strip()
                    st.session_state["challenge_answers"].append(user_ans)
                    st.session_state["challenge_results"].append(result)
                    st.session_state["challenge_index"] += 1
                    st.rerun()
            else:
                st.success("Challenge complete!")
                with st.expander("Challenge Results", expanded=True):
                    for q, a, r in zip(st.session_state["challenge_questions"], st.session_state["challenge_answers"], st.session_state["challenge_results"]):
                        st.markdown(f"**Q: {q}**")
                        st.markdown(f"Your answer: {a}")
                        st.markdown(f"Result: {r}")
                        st.markdown("---")
                if st.button("Restart Challenge", type="primary"):
                    st.session_state["challenge_started"] = False
                    st.session_state["challenge_questions"] = []
                    st.session_state["challenge_index"] = 0
                    st.session_state["challenge_answers"] = []
                    st.session_state["challenge_results"] = []
                    st.rerun()
    if st.button("Back"):
        st.session_state["step"] = 1
        st.rerun()
