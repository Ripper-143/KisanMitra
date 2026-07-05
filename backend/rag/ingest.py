import os
import glob
try:
    from rag.chroma_client import RAGDatabase
except ImportError:
    from chroma_client import RAGDatabase

def run_ingestion():
    print("Starting RAG Ingestion...")
    db = RAGDatabase()
    
    # Reset collection first to prevent duplicate entries
    db.reset_database()
    print("ChromaDB collection cleared.")
    
    # Path to scheme documents
    schemes_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schemes")
    if not os.path.exists(schemes_dir):
        print(f"Directory {schemes_dir} does not exist. Creating it.")
        os.makedirs(schemes_dir, exist_ok=True)
        return
    
    # Support TXT, MD, and PDF files
    txt_files = glob.glob(os.path.join(schemes_dir, "*.txt"))
    md_files = glob.glob(os.path.join(schemes_dir, "*.md"))
    pdf_files = glob.glob(os.path.join(schemes_dir, "*.pdf"))
    
    all_files = txt_files + md_files + pdf_files
    print(f"Found {len(all_files)} scheme files to ingest.")
    
    total_chunks = 0
    for file_path in all_files:
        file_name = os.path.basename(file_path)
        print(f"Processing {file_name}...")
        
        if file_path.endswith(".pdf"):
            # Handle PDF
            chunks_added = db.ingest_pdf(file_path)
        else:
            # Handle Text-based files
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Simple text page wrapper to match ingest structure
            pages = [{"page_num": 1, "text": content}]
            chunks = db.chunk_document(pages, file_name, chunk_size=500, chunk_overlap=100)
            
            if chunks:
                ids = [c["id"] for c in chunks]
                texts = [c["text"] for c in chunks]
                metadatas = [c["metadata"] for c in chunks]
                
                embeddings = db.get_embeddings(texts)
                
                db.collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    documents=texts,
                    metadatas=metadatas
                )
                chunks_added = len(chunks)
            else:
                chunks_added = 0
                
        print(f"Ingested {chunks_added} chunks from {file_name}.")
        total_chunks += chunks_added
        
    print(f"SUCCESS: Ingestion complete! Total chunks in ChromaDB: {total_chunks}")

if __name__ == "__main__":
    run_ingestion()
