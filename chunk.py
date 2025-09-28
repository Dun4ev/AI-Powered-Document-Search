def chunk_document(doc, size=1000, overlap=200):
    text = doc["text"]
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunk = text[start:end]
        chunks.append({"filename": doc["filename"], "text": chunk})
        start += size - overlap
    return chunks

if __name__ == "__main__":
    from ingest import extract_text_from_pdfs
    docs = extract_text_from_pdfs("./pdfs")
    all_chunks = []
    for doc in docs:
        all_chunks.extend(chunk_document(doc))
    print(f"🔹 Created {len(all_chunks)} chunks")
