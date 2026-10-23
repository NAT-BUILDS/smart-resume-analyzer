"""Command-line prototype for the Smart Resume Analyzer."""
import re
import PyPDF2

def extract_pdf_text(path):
    text = ""
    with open(path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

def analyze_structure(text):
    lower = text.lower()
    checks = {
        "Education": "education" in lower,
        "Skills": "skills" in lower,
        "Projects": "projects" in lower,
        "Contact information": "@" in text and bool(re.search(r"\b\d{10}\b", text)),
        "Certifications": "certifications" in lower,
    }
    return checks, sum(checks.values()) * 20

def main():
    path = input("Enter the path to a text-based PDF resume: ").strip().strip('"')
    try:
        text = extract_pdf_text(path)
    except Exception as exc:
        print(f"Could not read the PDF: {exc}")
        return
    if not text.strip():
        print("No readable text found. Scanned PDFs may require OCR.")
        return
    checks, score = analyze_structure(text)
    print("\nSMART RESUME ANALYZER")
    print(f"Structure score: {score}/100")
    for section, found in checks.items():
        print(f"{'Found' if found else 'Missing'}: {section}")
    print("\nThis command-line version checks basic structure only.")
    print("For keyword matching and downloadable reports, run the Streamlit app with: streamlit run app.py")

if __name__ == "__main__":
    main()
