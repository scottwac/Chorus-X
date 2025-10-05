# Chorus Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              CHORUS ARCHITECTURE                                │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│   Vue Frontend  │ ← User Interface (Datasets, Chorus Models, Bots, Chat)
│   (Port 3000)   │
└────────┬────────┘
         │ HTTP/REST API
         │
┌────────▼────────┐
│  Flask Backend  │ ← Main orchestration server
│   (Port 5000)   │
└────────┬────────┘
         │
    ┌────┴─────┬──────────┬───────────┬──────────┬─────────────┐
    │          │          │           │          │             │
┌───▼───┐ ┌───▼───┐ ┌────▼────┐ ┌───▼────┐ ┌──▼──────┐ ┌───▼────┐
│SQLite │ │Chroma │ │LLM APIs │ │ Files  │ │ Charts  │ │ Images │
│  DB   │ │Vector │ │         │ │Storage │ │Generator│ │   AI   │
│       │ │ Store │ │         │ │        │ │         │ │        │
└───────┘ └───────┘ └─────────┘ └────────┘ └─────────┘ └────────┘
    │         │           │          │          │          │
    │         │           │          │          │          │
    ▼         ▼           ▼          ▼          ▼          ▼
 Metadata   Vector    OpenAI     File      Chart      Image
   Data    Embeddings Anthropic  Uploads   Files    Generation
           Search     Groq APIs            (.png)

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                DATA FLOW                                        │
└─────────────────────────────────────────────────────────────────────────────────┘

1. DATASET CREATION
   User → Frontend → Backend → SQLite (metadata) + ChromaDB (vectors)

2. FILE UPLOAD & PROCESSING  
   Files → FileProcessor → VectorStore → ChromaDB + SQLite

3. CHORUS MODEL SETUP
   User → Frontend → Backend → SQLite (responder + evaluator LLMs)

4. BOT CREATION
   User → Frontend → Backend → SQLite (instructions + dataset + model links)

5. CHAT INTERACTION
   User Query → Intent Classification → RAG Search → Chorus Process → Response

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              CHORUS PROCESS                                     │
└─────────────────────────────────────────────────────────────────────────────────┘

User Query
    │
    ▼
┌─────────────────┐
│ Intent Classify │ ← GPT-5 determines: text/find_image/generate_chart/generate_image
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   RAG Search    │ ← Query ChromaDB for relevant context
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Responder LLMs  │ ← Multiple LLMs generate responses using context
│  (Parallel)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Evaluator LLMs  │ ← Vote on best response from responders
│   (Voting)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Final Response  │ ← Highest voted response returned to user
└─────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              KEY COMPONENTS                                     │
└─────────────────────────────────────────────────────────────────────────────────┘

🗄️  DATABASE LAYER
   • SQLite: Metadata (datasets, bots, models, chat history)
   • ChromaDB: Vector embeddings for semantic search

🤖 LLM SERVICES  
   • OpenAI: GPT-5, GPT-4o, GPT-3.5-turbo
   • Anthropic: Claude 3.7 Sonnet, Claude 3.5 Sonnet/Haiku  
   • Groq: Llama 3.3, Mixtral, Gemma

📁 FILE PROCESSING
   • Text: .txt, .md, .pdf, .docx
   • Images: OCR + AI description
   • Chunking & embedding generation

🎭 CHORUS ORCHESTRATION
   • Multi-LLM response generation
   • Democratic voting system
   • Best response selection

🖼️  SPECIALIZED FEATURES
   • Chart Generation: Data visualization
   • Image AI: Generation & editing
   • Image Search: Find uploaded images
```
