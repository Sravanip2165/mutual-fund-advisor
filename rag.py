# rag.py
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ─────────────────────────────────────────
# 1. Load documents
# ─────────────────────────────────────────
def load_documents():
    print("Loading documents...")
    
    docs = []
    
    # load SEBI PDF
    pdf_loader = PyPDFLoader("documents/sebi_mf_faq.pdf")
    docs.extend(pdf_loader.load())
    print(f"  PDF loaded: {len(docs)} pages")
    
    # load methodology text
    txt_loader = TextLoader("documents/methodology.txt")
    docs.extend(txt_loader.load())
    print(f"  TXT loaded")
    
    return docs


# ─────────────────────────────────────────
# 2. Split into chunks
# ─────────────────────────────────────────
def split_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(docs)
    print(f"  Total chunks created: {len(chunks)}")
    return chunks


# ─────────────────────────────────────────
# 3. Build vector store
# ─────────────────────────────────────────
def build_vectorstore(chunks):
    print("Building vector store...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local("vectorstore")
    print("  Vector store saved!")
    return vectorstore


# ─────────────────────────────────────────
# 4. Load existing vector store
# ─────────────────────────────────────────
def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vectorstore = FAISS.load_local(
        "vectorstore",
        embeddings,
        allow_dangerous_deserialization=True
    )
    return vectorstore


# ─────────────────────────────────────────
# 5. Answer question using RAG
# ─────────────────────────────────────────
def answer_question(question: str, vectorstore) -> str:
    # search relevant chunks
    docs = vectorstore.similarity_search(question, k=3)
    
    if not docs:
        return "I don't have information about this in my knowledge base."
    
    # combine chunks into context
    context = "\n\n".join([doc.page_content for doc in docs])
    
    prompt = f"""You are a helpful mutual fund assistant for Indian investors.

Answer the question using ONLY the context provided below.
If the answer is not in the context, say exactly:
"I don't have information about this in my knowledge base."

Context:
{context}

Question: {question}

Rules:
- Use simple plain English
- Keep answer under 100 words
- Do not add information outside the context
- Do not predict future returns
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"


# ─────────────────────────────────────────
# 6. Setup — run once to build vectorstore
# ─────────────────────────────────────────
def setup_rag():
    docs   = load_documents()
    chunks = split_documents(docs)
    vectorstore = build_vectorstore(chunks)
    return vectorstore


# ─────────────────────────────────────────
# 7. Get or build vectorstore
# ─────────────────────────────────────────
def get_vectorstore():
    if os.path.exists("vectorstore"):
        print("Loading existing vector store...")
        return load_vectorstore()
    else:
        print("Building new vector store...")
        return setup_rag()