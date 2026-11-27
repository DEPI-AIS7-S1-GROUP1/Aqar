"""S2-M1-10 RAG: sourced answers about areas and developers.

Pieces: docs.py (read + chunk the Markdown guides), embeddings.py (Gemini or offline fake),
store.py (pgvector or in-memory), search.py (the Rag service the agent calls).
"""
