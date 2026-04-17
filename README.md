# Resume Chat Assistant

## Overview

This project is a **Resume Chat Assistant** built using the **MERN stack + Python (FastAPI)** that allows users to:

* Upload a resume (PDF)
* Ask questions based on the resume
* Get AI-generated answers using **RAG (Retrieval-Augmented Generation)**

---

# What is RAG?

RAG = **Retrieval + Generation**

```text
User Question → Retrieve relevant data → Generate answer using LLM
```

Instead of sending the whole resume to the model, we:

1. Convert resume into chunks
2. Store embeddings
3. Retrieve relevant chunks
4. Send only relevant context to LLM

---

# Tech Stack

## Frontend

* React.js
* Axios / Fetch API
* SSE (Server-Sent Events)

## Backend

* Node.js (API Gateway)
* Python (FastAPI - AI service)

## AI / ML

* Sentence Transformers (Embeddings)
* Ollama (Local LLM - phi3 / llama3)

## Database

* Supabase (PostgreSQL + pgvector)

---

# Why Each Technology?

## FastAPI

* Fast Python backend
* Easy API creation
* Supports async + streaming

## Sentence Transformers

* Converts text → vectors
* Enables semantic search

## Ollama

* Runs LLM locally (FREE)
* No API cost
* Supports streaming

## Supabase

* Stores embeddings (vector DB)
* PostgreSQL + pgvector support
* Easy integration

## SSE (Streaming)

* Real-time response like ChatGPT
* Better UX (no waiting for full response)

---

# Installation Steps

## Setup Python Service

```bash
cd rag-service
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install fastapi uvicorn sentence-transformers ollama pypdf supabase
```

---

## Run Python Server

```bash
uvicorn main:app --reload
```

---

## Install Ollama & Models
# Ollama should be installed at system root layer

```bash
ollama serve
ollama pull phi3
```

(Alternative model)

```bash
ollama pull llama3
```

---

## Setup Supabase

* Create project in Supabase
* Create table:

```sql
create table resumes (
  id uuid primary key default uuid_generate_v4(),
  content text,
  embedding vector(384)
);
```

* Create RPC function:

```sql
create or replace function match_documents(
  query_embedding vector(384),
  match_count int
)
returns table (
  id uuid,
  content text,
  similarity float
)
language sql stable
as $$
  select
    id,
    content,
    1 - (embedding <=> query_embedding) as similarity
  from resumes
  order by embedding <=> query_embedding
  limit match_count;
$$;
```

---

## Setup Node Server

```bash
cd server
npm install
npm start
```

---

## Setup Frontend

```bash
cd client
npm install
npm start
```

---

# Application Flow

## Upload Resume

```text
User Upload → FastAPI
→ Extract text (PDF)
→ Chunk text
→ Generate embeddings
→ Store in Supabase
```

---

## Query Flow

```text
User Question
→ Enhance Query
→ Convert to embedding
→ Search similar chunks (Supabase)
→ Send context to LLM
→ Stream response (SSE)
```

---

# Core Concepts

## Embeddings

Text → Vector representation

Example:

```text
"React developer" → [0.12, -0.45, ...]
```

Used for semantic similarity search.

---

## Chunking

Large resume → small parts

Why?

* Better retrieval
* Faster processing

---

## Query Enhancement

Improves user query for better search

Example:

```text
"intro" → "professional summary experience"
```

---

## Vector Search

Finds most relevant chunks using similarity

---

## Streaming (SSE)

Server sends response in parts:

```text
data: Hello
data: I am
data: developer
```

---

# Key Features

* Resume-based Q&A
* Real-time streaming responses
* Vector search (semantic)
* Local LLM (no cost)

---

# Example Queries

* "What are the skills?"
* "Give me introduction"
* "What projects are mentioned?"

---

# Known Limitations

* Query enhancement is rule-based (can improve)
* Accuracy depends on chunk quality
* Single resume support (currently)

---

# Future Improvements

* Multi-resume support
* Hybrid search (keyword + vector)
* Reranking (better accuracy)
* Chat history
* Authentication

---

# Commands Summary

```bash
# Python
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn sentence-transformers ollama pypdf numpy supabase
uvicorn main:app --reload

# Ollama
ollama serve
ollama pull phi3

# Node
npm install
npm start

# React
npm install
npm start
```

---

## Setup Project in Other System

# Freeze Python Venv Installed Packages
pip freeze > requirements.txt

# Install Python Venv Packages In Other System
1. Install venv
- python3 -m venv venv
- source venv/bin/activate
2. Install requirements
- pip install -r requirements.txt
3. Run python in venv
- uvicorn main:app --reload

# Conclusion

This project demonstrates a **production-style RAG system** using:

* Vector embeddings
* Semantic search
* Local LLM
* Streaming responses

It is scalable and can be extended into a full AI product.

---
