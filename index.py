import faiss
import pickle
import numpy as np

def build_faiss_index(vectors):
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)
    return index

if __name__ == "__main__":
    with open("vectors.npy", "rb") as f:
        vectors = np.load(f)
    with open("chunks.pkl", "rb") as f:
        all_chunks = pickle.load(f)
    index = build_faiss_index(vectors)
    faiss.write_index(index, "docs.index")
    with open("chunks.pkl", "wb") as f:
        pickle.dump(all_chunks, f)
    print("📦 Index and metadata saved")
