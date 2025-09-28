from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_chunks(chunks):
    texts = [c["text"] for c in chunks]
    vectors = model.encode(texts)
    return np.array(vectors)

if __name__ == "__main__":
    import pickle
    with open("chunks.pkl", "rb") as f:
        all_chunks = pickle.load(f)
    vectors = embed_chunks(all_chunks)
    print(f"✅ Embedded shape: {vectors.shape}")
