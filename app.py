import streamlit as st
import PyPDF2
import re

st.set_page_config(page_title="Smart Resume Analyzer", page_icon="📄", layout="centered")
st.title("Smart Resume Analyzer")
st.write("Upload a PDF or DOCX resume to receive basic structure checks, role-keyword matching, and improvement suggestions.")

uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "docx"])

if uploaded_file is not None:
    text = ""
    try:
        if uploaded_file.name.lower().endswith(".pdf"):
            reader = PyPDF2.PdfReader(uploaded_file)
            for page in reader.pages:
                text += page.extract_text() or ""
        else:
            from docx import Document as DocxDocument
            document = DocxDocument(uploaded_file)
            for paragraph in document.paragraphs:
                text += paragraph.text + "\n"
    except Exception as exc:
        st.error(f"Could not read this file. Please check that it is a valid PDF or DOCX. Details: {exc}")
        st.stop()

    if not text.strip():
        st.error("No readable text was found. Scanned/image-only PDFs may need OCR before analysis.")
        st.stop()

    st.success("Resume uploaded and analyzed.")
    with st.expander("View extracted resume text"):
        st.text(text)

    resume = text.lower()
    st.header("Resume Structure Score")
    checks = {
        "Education": "education" in resume,
        "Skills": "skills" in resume,
        "Projects": "projects" in resume,
        "Contact information": ("@" in text and bool(re.search(r"\b\d{10}\b", text))),
        "Certifications": "certifications" in resume
    }
    score = sum(checks.values()) * 20
    st.metric("Resume Structure Score", f"{score} / 100")
    st.progress(score / 100)
    for section, found in checks.items():
        st.write(("✅" if found else "❌"), section, "- " + ("Found" if found else "Missing"))

    st.header("ATS Keyword Checker")
    keywords = {
        "Data Analyst": ["python", "sql", "excel", "power bi", "tableau", "pandas", "statistics", "data visualization"],
        "Web Developer": ["html", "css", "javascript", "react", "bootstrap", "flask", "django", "sql"],
        "AI Engineer": ["python", "machine learning", "deep learning", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch"],
        "Cloud Engineer": ["aws", "azure", "google cloud", "linux", "docker", "kubernetes", "networking", "python"]
    }
    role = st.selectbox("Select your target job role", list(keywords.keys()))
    required = keywords[role]
    matched = [word for word in required if word in resume]
    missing = [word for word in required if word not in resume]
    ats_score = round(len(matched) / len(required) * 100)
    st.metric("Keyword Match (indicative)", f"{ats_score}%")
    st.write("**Matched keywords**")
    st.write(", ".join(matched) if matched else "None")
    st.write("**Missing keywords**")
    st.write(", ".join(missing) if missing else "None")

    st.header("Smart Resume Feedback")
    feedback = []
    for key, suggestion in [
        ("Education", "Add an Education section if applicable."),
        ("Skills", "Add a clearly labelled Skills section."),
        ("Projects", "Add projects and explain your individual contribution and outcome."),
        ("Certifications", "Include relevant certifications you have actually completed."),
    ]:
        if not checks[key]:
            feedback.append(suggestion)
    if not checks["Contact information"]:
        feedback.append("Check that your resume includes a valid email address and 10-digit phone number.")
    if len(text.split()) < 100:
        feedback.append("Your resume is brief. Add relevant details about skills, projects, responsibilities, and achievements.")
    if missing:
        feedback.append("Review missing keywords for the selected role and include only skills you genuinely possess.")
    if feedback:
        for item in feedback:
            st.write("💡", item)
    else:
        st.success("All basic structure checks passed.")

    report = (
        "SMART RESUME ANALYZER REPORT\n\n"
        f"Resume file: {uploaded_file.name}\n"
        f"Target role: {role}\n"
        f"Resume structure score: {score}/100\n"
        f"Indicative keyword match: {ats_score}%\n\n"
        f"Matched keywords: {', '.join(matched) if matched else 'None'}\n"
        f"Missing keywords: {', '.join(missing) if missing else 'None'}\n\n"
        "Structure checks:\n" + "\n".join(f"- {name}: {'Found' if found else 'Missing'}" for name, found in checks.items()) +
        "\n\nSuggestions:\n" + ("\n".join("- " + item for item in feedback) if feedback else "- No basic structure suggestions generated.")
    )
    st.header("Download Analysis Report")
    st.download_button("Download report (.txt)", data=report, file_name="resume_analysis_report.txt", mime="text/plain")
    st.caption("Prototype note: scores are rule-based indicators, not an official ATS score or a guarantee of recruitment outcomes.")
