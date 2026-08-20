from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
# import faiss
import numpy as np
import ollama
from dotenv import load_dotenv
from pypdf import PdfReader
# from pydantic import BaseModel
import os
import time
from supabase import create_client
from fastapi.responses import StreamingResponse

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

_supabase_client = None

def get_supabase():
    global _supabase_client
    if _supabase_client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise RuntimeError(
                "Missing required environment variables: SUPABASE_URL and/or SUPABASE_KEY. "
                "Please configure them in your Render Dashboard under Environment Variables."
            )
        _supabase_client = create_client(url, key)
    return _supabase_client

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}


# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Lazy-load embedding model on first use (prevents blocking Uvicorn startup)
_embedding_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        print("🧠 Loading embedding model...")
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model


documents = []
index = None

# ✅ Ensure uploads folder exists
os.makedirs("uploads", exist_ok=True)

def enhance_query(question: str):
    q = question.lower()

    # dynamic intent detection (no strict hardcoding)
    keywords = []

    if any(word in q for word in ["intro", "introduction", "about", "summary"]):
        keywords.append("professional summary profile experience")

    if any(word in q for word in ["skills", "tech", "technology"]):
        keywords.append("technical skills technologies stack")

    if any(word in q for word in ["project", "work"]):
        keywords.append("projects experience work details")

    # combine original + inferred intent
    return question + " " + " ".join(keywords)

# 🔹 Extract text from PDF
def extract_text(file_path):
    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content + " "

    # Clean text
    text = text.replace("\n", " ")
    return text


# 🔹 Better chunking with overlap (IMPORTANT)
def chunk_text(text, size=400, overlap=50):
    chunks = []
    for i in range(0, len(text), size - overlap):
        chunks.append(text[i:i + size])
    return chunks


# 🔹 Upload Resume
@app.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    global documents, index

    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    print("📄 Extracting text...")
    text = extract_text(file_path)

    print("✂️ Chunking...")
    chunks = chunk_text(text)[:20]  # limit chunks for speed

    print("🧠 Creating embeddings...")
    start = time.time()
    embeddings = get_embedding_model().encode(chunks).astype(float)
    print("⏱ Embedding time:", time.time() - start)

    for i, chunk in enumerate(chunks):
        try:
            res = get_supabase().table("resumes").insert({
                "content": chunk,
                "embedding": embeddings[i].tolist()
            }).execute()

            print("✅ Insert success:", res)

        except Exception as e:
            print("❌ Insert error:", e)

    #Below code is for storing embedding data in virtual DB
    # documents = chunks
    # dim = embeddings.shape[1]
    # index = faiss.IndexFlatL2(dim)
    # index.add(np.array(embeddings)) 

    return {"message": "Resume processed successfully"}


# # 🔹 Request schema
# class QueryRequest(BaseModel):
#     question: str

def search_similar_chunks(query_embedding):
    result = get_supabase().rpc(
        "match_documents",
        {
            "query_embedding": query_embedding.tolist(),
            "match_count": 5
        }
    ).execute()


    return [item["content"] for item in result.data]


@app.get("/query-stream")
def query_stream(question: str):
    
    # query_embedding = embedding_model.encode([question])
    enhanced_question = enhance_query(question)
    query_embedding = get_embedding_model().encode([enhanced_question])
    similar_chunks = search_similar_chunks(query_embedding[0])
    context = "\n".join(similar_chunks)[:800]

    prompt = f"""
    You are a strict resume parser.

    RULES:
    1. ONLY use the given context
    2. DO NOT generate anything outside context
    3. If answer is not clearly present → say "Not found"
    4. Keep answer short and exact

    Context:
    {context}

    Question: {question}

    Answer:
    """

    def generate():
        stream = ollama.chat(
            model="phi3",
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        for chunk in stream:
            content = chunk.get("message", {}).get("content", "")
            if content:
                yield f"data: {content}\n\n"   # ✅ SSE FORMAT
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)