from crewai.tools import tool
from rag.chroma_client import RAGDatabase

@tool("Query Government Schemes Database Tool")
def query_government_schemes(query: str) -> str:
    """
    Queries the vector database to retrieve eligibility guidelines, subsidies, 
    and application processes of government schemes (like PM-Kisan, PMFBY, YSR Rythu Bharosa, Rythu Bandhu).
    Input should be a query string related to a farmer's crop, land size, or location.
    Returns: Relevant text chunks containing the scheme guidelines.
    """
    db = RAGDatabase()
    results = db.retrieve(query, top_k=4)
    
    if not results:
        return (
            "No matching scheme information found in the database. "
            "Please check if the vector store has been seeded with scheme documents."
        )
        
    formatted = []
    for res in results:
        formatted.append(
            f"Scheme Source Document: {res['metadata']['source']}\n"
            f"Content Details: {res['text']}\n"
            f"----------------------------------------"
        )
    return "\n".join(formatted)
