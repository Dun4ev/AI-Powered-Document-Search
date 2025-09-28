import pickle
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')
index = faiss.read_index("docs.index")
with open("chunks.pkl", "rb") as f:
    chunks = pickle.load(f)

def search_docs(query, top_k=3):
    q_vector = model.encode([query])
    distances, indices = index.search(np.array(q_vector), top_k)
    return [chunks[i] for i in indices[0]]

if __name__ == "__main__":
    results = search_docs("Explain transfer learning")
    for r in results:
        print(f"{r['filename']} :\n{r['text'][:300]}...\n")
