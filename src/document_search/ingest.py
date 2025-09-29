
"""
Модуль для извлечения текста из PDF-файлов.

Функция `extract_text_from_pdfs` сканирует указанную папку, находит все
файлы с расширением .pdf, открывает их с помощью библиотеки PyMuPDF (fitz)
и извлекает текстовое содержимое со всех страниц.

Для всех страниц, кроме первой, применяется очистка от повторяющихся шапок.
Логика очистки использует шаблоны из файла `header_templates.json`.
"""
import fitz
import os
import json

def _clean_page_text(page_text: str, header_labels: list[str]) -> str:
    """
    Очищает текст одной страницы от шапки.

    Алгоритм находит последнюю строку, которая похожа на метку из шапки,
    и удаляет весь текст до этой строки, включая небольшой запас, 
    чтобы захватить строки со значениями.
    """
    lines = page_text.split('\n')
    last_header_line_index = -1

    # Находим индекс последней строки, которая начинается с одной из меток
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        if any(stripped_line.startswith(label) for label in header_labels):
            last_header_line_index = i

    # Если метки шапки вообще не найдены, возвращаем исходный текст
    if last_header_line_index == -1:
        return page_text

    # Определяем, где начинается основной контент.
    # Берем индекс последней метки + небольшой запас (например, 5 строк),
    # чтобы покрыть многострочные значения и пустые строки.
    content_start_index = last_header_line_index + 5

    # Собираем очищенные строки
    cleaned_lines = lines[content_start_index:]
    
    return '\n'.join(cleaned_lines)


def extract_text_from_pdfs(folder: str) -> list[dict]:
    """
    Извлекает текст из всех PDF-файлов в папке, очищая шапки.
    """
    try:
        with open('header_templates.json', 'r', encoding='utf-8') as f:
            templates = json.load(f)
        # Используем первый шаблон из файла
        header_labels = templates['templates'][0]['header_labels']
    except FileNotFoundError:
        print("⚠️  Файл 'header_templates.json' не найден. Очистка шапок не будет производиться.")
        header_labels = []
    except (json.JSONDecodeError, IndexError, KeyError):
        print("⚠️  Ошибка чтения 'header_templates.json'. Файл поврежден или имеет неверную структуру.")
        header_labels = []


    documents = []
    for file in os.listdir(folder):
        if file.endswith(".pdf"):
            path = os.path.join(folder, file)
            full_text = ""
            try:
                pdf = fitz.open(path)
                for i, page in enumerate(pdf):
                    page_text = page.get_text()
                    if i == 0 or not header_labels:
                        # Оставляем первую страницу как есть или если нет меток
                        full_text += page_text
                    else:
                        # Очищаем все последующие страницы
                        cleaned_text = _clean_page_text(page_text, header_labels)
                        full_text += cleaned_text
                pdf.close()
                documents.append({"filename": file, "text": full_text})
                print(f"✅ {file} - {len(full_text)} chars")
            except Exception as e:
                print(f"❌ Не удалось обработать файл {file}: {e}")

    return documents

if __name__ == "__main__":
    # Пример использования
    docs = extract_text_from_pdfs("pdfs")
