import fitz  # PyMuPDF

def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_txt(file):
    return file.read().decode("utf-8")

# Prompt templates
def get_summary_prompt(doc_text):
    return f"Summarize this document in less than 150 words:\n{doc_text}"

def get_ask_prompt(doc_text, user_question):
    return f"Based on the following document, answer the question and provide justification:\n\n{doc_text}\n\nQuestion: {user_question}"

def get_challenge_prompt(doc_text):
    return f"Generate 3 logic/comprehension-based questions from the following document:\n\n{doc_text}"

def get_evaluate_prompt(doc_text, q, a):
    return f"Document: {doc_text}\nQuestion: {q}\nUser Answer: {a}\nIs the answer correct? Justify based only on the document."
