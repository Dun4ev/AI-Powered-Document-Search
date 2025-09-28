"""
Модуль для извлечения текста из PDF-файлов.

Функция `extract_text_from_pdfs` сканирует указанную папку, находит все
файлы с расширением .pdf, открывает их с помощью библиотеки PyMuPDF (fitz)
и извлекает текстовое содержимое со всех страниц.
"""
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