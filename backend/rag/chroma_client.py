import os
from typing import List, Dict, Any
import chromadb
from config import settings

class RAGDatabase:
    def __init__(self, db_path: str = None, collection_name: str = None):
        """
        Initializes the ChromaDB persistent client and loads the sentence transformer embedding model.
        """
        self.db_path = os.path.abspath(db_path or settings.CHROMA_PERSIST_DIR)
        collection_name = collection_name or settings.CHROMA_COLLECTION
        
        os.makedirs(self.db_path, exist_ok=True)
        
        # Initialize persistent Chroma client
        self.client = chromadb.PersistentClient(path=self.db_path)
        
        # Load SentenceTransformer model
        self._load_model()
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def _load_model(self):
        if os.environ.get("USE_MOCK_EMBEDDINGS", "false").lower() == "true":
            print("USE_MOCK_EMBEDDINGS is enabled. Skipping SentenceTransformer loading.")
            self.has_model = False
            return
        try:
            from sentence_transformers import SentenceTransformer
            print("Loading SentenceTransformer model 'all-MiniLM-L6-v2'...")
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
            self.has_model = True
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Warning: Failed to load sentence-transformers locally ({e}). Using fallback mock embeddings.")
            self.has_model = False

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        if self.has_model:
            return self.model.encode(texts, show_progress_bar=False).tolist()
        else:
            # Fallback mock embedding: simple deterministic vector based on word hashes
            embeddings = []
            for text in texts:
                words = text.lower().split()
                # Create a 384-dimensional vector
                vector = [0.0] * 384
                for idx, word in enumerate(words):
                    hash_val = sum(ord(c) for c in word)
                    vector[hash_val % 384] += 1.0 + (idx * 0.1)
                # Normalize vector
                magnitude = sum(x*x for x in vector) ** 0.5
                if magnitude > 0:
                    vector = [x / magnitude for x in vector]
                embeddings.append(vector)
            return embeddings

    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extracts text page-by-page from a PDF file.
        """
        pages = []
        try:
            import pypdf
            with open(pdf_path, "rb") as f:
                reader = pypdf.PdfReader(f)
                num_pages = len(reader.pages)
                for page_idx in range(num_pages):
                    page = reader.pages[page_idx]
                    text = page.extract_text() or ""
                    pages.append({
                        "page_num": page_idx + 1,
                        "text": text.strip()
                    })
        except Exception as e:
            print(f"Error reading PDF {pdf_path}: {e}")
            # If PDF read fails, check if there is a TXT version or read file as text
            if os.path.exists(pdf_path):
                with open(pdf_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                    pages.append({
                        "page_num": 1,
                        "text": text
                    })
        return pages

    def chunk_document(self, pages: List[Dict[str, Any]], file_name: str, chunk_size: int = 600, chunk_overlap: int = 150) -> List[Dict[str, Any]]:
        all_chunks = []
        chunk_counter = 0
        
        for page in pages:
            text = page["text"]
            page_num = page["page_num"]
            if not text:
                continue
                
            start = 0
            text_len = len(text)
            
            while start < text_len:
                end = start + chunk_size
                if end > text_len:
                    end = text_len
                
                chunk_text = text[start:end].strip()
                
                if chunk_text:
                    all_chunks.append({
                        "id": f"{file_name}_p{page_num}_c{chunk_counter}",
                        "text": chunk_text,
                        "metadata": {
                            "source": file_name,
                            "page": page_num,
                            "chunk_index": chunk_counter
                        }
                    })
                    chunk_counter += 1
                
                start += (chunk_size - chunk_overlap)
                if end == text_len:
                    break
                    
        return all_chunks

    def ingest_pdf(self, pdf_path: str, chunk_size: int = 600, chunk_overlap: int = 150) -> int:
        file_name = os.path.basename(pdf_path)
        pages = self.extract_text_from_pdf(pdf_path)
        chunks = self.chunk_document(pages, file_name, chunk_size, chunk_overlap)
        
        if not chunks:
            return 0
            
        ids = [c["id"] for c in chunks]
        texts = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]
        
        embeddings = self.get_embeddings(texts)
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        
        return len(chunks)

    def retrieve(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        query_embeddings = self.get_embeddings([query])
        
        results = self.collection.query(
            query_embeddings=query_embeddings,
            n_results=top_k
        )
        
        retrieved_chunks = []
        if not results or not results["documents"] or len(results["documents"][0]) == 0:
            return retrieved_chunks
            
        docs = results["documents"][0]
        ids = results["ids"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)
        
        for i in range(len(docs)):
            retrieved_chunks.append({
                "id": ids[i],
                "text": docs[i],
                "metadata": metadatas[i],
                "distance": distances[i]
            })
            
        return retrieved_chunks

    def reset_database(self):
        try:
            self.client.delete_collection(self.collection.name)
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION,
            metadata={"hnsw:space": "cosine"}
        )
