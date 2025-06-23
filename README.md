# Gemini Document Assistant

An intelligent document assistant web app using Streamlit and Google's Gemini API (via google-generativeai). Upload a PDF or TXT, get a summary, ask questions, or challenge yourself with comprehension questions.

## Features
- Upload PDF or TXT documents
- Automatic summary (≤ 150 words)
- Ask Anything mode: ask questions and get justified answers
- Challenge Me mode: answer generated questions, get evaluated with explanations

## Setup
1. Clone/download this repo.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run app.py
   ```

## Configuration
- The Gemini API key is set in `app.py` (replace with your own for production).

## File Structure
- `app.py`: Streamlit app logic
- `utils.py`: File reading and prompt templates
- `requirements.txt`: Dependencies
- `README.md`: This file

## Notes
- All answers are based strictly on the uploaded document.
- Justifications reference specific document content.
- Clean, user-friendly interface.
