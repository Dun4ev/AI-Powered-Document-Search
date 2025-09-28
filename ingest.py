import fitz
import os

def extract_text_from_pdfs(folder):
    documents = []
    for file in os.listdir(folder):
        if file.endswith(".pdf"):
            path = os.path.join(folder, file)
            text = ""
            pdf = fitz.open(path)
            for page in pdf:
                text += page.get_text()
            documents.append({"filename": file, "text": text})
            print(f"✅ {file} - {len(text)} chars")
    return documents

if __name__ == "__main__":
    docs = extract_text_from_pdfs("./pdfs")
