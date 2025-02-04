import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import PyPDF2
import json

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def generate_questions(context, num_questions=5):
    prompt = f"""
    Based on the following context, generate {num_questions} questions with their answers.
    Format the output as a JSON string with the following structure:
    {{
        "questions": [
            {{
                "question": "Question text here",
                "answer": "Answer text here"
            }}
        ]
    }}
    
    Context:
    {context}
    """
    
    response = model.generate_content(prompt)
    try:
        # Parse the response text as JSON
        questions_json = json.loads(response.text)
        return questions_json["questions"]
    except json.JSONDecodeError:
        st.error("Error parsing the generated questions. Please try again.")
        return []

def main():
    st.title("🤖 Automatic Question Answer Generator")
    st.write("Generate questions from text or PDF files using AI!")

    # Input method selection
    input_method = st.radio(
        "Choose input method:",
        ["Text Input", "PDF Upload"]
    )

    context = ""
    if input_method == "Text Input":
        context = st.text_area(
            "Enter your text here:",
            height=200,
            placeholder="Paste your text here..."
        )
    else:
        uploaded_file = st.file_uploader("Upload a PDF file", type=['pdf'])
        if uploaded_file is not None:
            context = extract_text_from_pdf(uploaded_file)
            st.success("PDF uploaded and processed successfully!")
            
            # Show a preview of the extracted text
            with st.expander("Show extracted text"):
                st.text(context[:500] + "...")

    # Number of questions slider
    num_questions = st.slider("Number of questions to generate", 1, 10, 5)

    if st.button("Generate Questions"):
        if context:
            with st.spinner("Generating questions..."):
                questions = generate_questions(context, num_questions)
                
                # Display questions and answers
                for i, qa in enumerate(questions, 1):
                    with st.expander(f"Question {i}"):
                        st.write("**Q:**", qa["question"])
                        st.write("**A:**", qa["answer"])
        else:
            st.warning("Please provide some text or upload a PDF first.")

if __name__ == "__main__":
    st.set_page_config(
        page_title="Question Answer Generator",
        page_icon="🤖",
        layout="wide"
    )
    main()
