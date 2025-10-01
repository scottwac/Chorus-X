# Chorus - Multi-LLM Orchestration Platform

Chorus is a sophisticated AI orchestration platform that enables you to create intelligent bots powered by multiple Large Language Models (LLMs) working together through a voting system. It combines RAG (Retrieval-Augmented Generation) with multi-model consensus for superior AI responses.

## 🌟 Features

### 1. **Datasets & RAG**
- 📁 Drag-and-drop file upload for building knowledge bases
- 📄 Support for multiple file types: `.txt`, `.pdf`, `.docx`, `.md`
- 🖼️ Image support with OCR and AI-powered visual description
- 🔍 Vector search using ChromaDB and OpenAI embeddings
- 💾 Local vector storage for privacy and speed

### 2. **Chorus Models**
- 🎭 Configure multiple LLMs to respond to queries simultaneously
- ⚖️ Set up evaluator LLMs to vote on the best responses
- 🤝 Supports OpenAI, Anthropic (Claude), and Groq
- 🏆 Democratic selection of the highest-quality answer
- 🔧 Flexible configuration for different use cases

### 3. **Bots**
- 🤖 Create custom AI bots with specific instructions
- 📚 Link bots to datasets for domain-specific knowledge
- 💬 Interactive chat interface
- 📊 Debug mode to see all responses and voting details
- 💾 Persistent chat history

## 🛠️ Tech Stack

### Backend
- **Flask** - Python web framework
- **ChromaDB** - Vector database for embeddings
- **SQLite** - Relational database for metadata
- **OpenAI, Anthropic, Groq APIs** - LLM providers
  - GPT-5, GPT-4o, GPT-3.5-turbo
  - Claude 3.7 Sonnet, Claude 3.5 Sonnet/Haiku
  - Llama 3.3, Mixtral, Gemma
- **PyPDF2, python-docx, Pytesseract** - File processing

### Frontend
- **Vue 3** - Progressive JavaScript framework
- **TailwindCSS** - Utility-first CSS framework
- **Vite** - Next-generation frontend tooling
- **Axios** - HTTP client

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- Tesseract OCR (for image text extraction)
- API keys for OpenAI, Anthropic, and/or Groq

### Installation

### Quick Start (Easiest Way)

1. **Navigate to Chorus X folder**
```bash
cd "Chorus X"
```

2. **Set up your API keys**
Create a `.env` file in the root folder:
```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk_...
```

3. **Install Tesseract OCR** (one-time setup)
- **Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki
- **Mac**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

4. **Start Chorus!**
```bash
# Double-click start_chorus.bat (Windows)
# OR run manually:
start_chorus.bat
```

This will automatically:
- Create Python virtual environment
- Install all dependencies
- Start Flask Server (port 5000)
- Start Frontend (port 3000)

5. **Access Chorus**
Open your browser to `http://localhost:3000`

### Manual Setup (Alternative)

#### Set up the Flask Server
```bash
cd "Flask Server"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

#### Set up the frontend
```bash
cd frontend
npm install
npm run dev
```

## 📖 Usage Guide

### Creating a Dataset
1. Navigate to the **Datasets** page
2. Click "New Dataset"
3. Enter a name and description
4. Drag and drop files into the dataset card
5. Files are automatically processed and embedded

### Creating a Chorus Model
1. Navigate to the **Chorus Models** page
2. Click "New Chorus Model"
3. Add **Responder LLMs** - these generate responses
   - Choose providers: OpenAI, Anthropic, or Groq
   - Select specific models
4. Add **Evaluator LLMs** - these vote on best responses
5. Save the model

### Creating a Bot
1. Navigate to the **Bots** page
2. Click "New Bot"
3. Enter a name and instructions
4. Select a dataset (optional)
5. Select a Chorus model
6. Click "Create"

### Chatting with a Bot
1. Click on a bot card or click "Start Chat"
2. Type your message and press Enter or click Send
3. Enable "Show Debug" to see all LLM responses and votes
4. The bot will:
   - Search your dataset for relevant information
   - Query all responder LLMs with context
   - Have evaluator LLMs vote on responses
   - Return the highest-voted answer

## 🏗️ Architecture

```
┌─────────────────┐
│   Vue Frontend  │
└────────┬────────┘
         │
         │ HTTP/REST
         │
┌────────▼────────┐
│  Flask Backend  │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬───────────┐
    │         │          │           │
┌───▼───┐ ┌──▼──┐  ┌────▼────┐  ┌──▼───┐
│SQLite │ │Chroma│  │LLM APIs │  │Files │
│  DB   │ │  DB  │  │         │  │      │
└───────┘ └──────┘  └─────────┘  └──────┘
```

## 🎨 Design Philosophy

Chorus uses a **modern green theme** reflecting growth, harmony, and technological advancement. The interface is designed to be:
- **Intuitive** - Clear navigation and obvious actions
- **Responsive** - Works on desktop and tablet devices
- **Fast** - Optimized loading and smooth transitions
- **Informative** - Debug mode for transparency

## 🔒 Security Notes

- API keys are stored in `.env` and never committed to version control
- All file uploads are processed server-side
- Vector databases are stored locally
- No data is sent to third parties except LLM APIs

## 🤝 Contributing

This is a technological demonstration project. Feel free to fork and customize for your needs!

## 📝 License

This project is provided as-is for educational and demonstration purposes.

## 🐛 Troubleshooting

### Tesseract not found
Make sure Tesseract is installed and in your PATH. On Windows, you may need to add it manually.

### CORS errors
Ensure the backend is running on port 5000 and frontend on port 3000.

### API errors
Check that your API keys are correctly set in the `.env` file.

### ChromaDB errors
Delete the `chroma_data` folder and restart the backend to reset the vector database.

## 🎯 Future Enhancements

- [ ] User authentication and multi-tenancy
- [ ] More LLM provider support
- [ ] Advanced RAG techniques (reranking, hybrid search)
- [ ] Bot performance analytics
- [ ] Export/import functionality
- [ ] Custom embedding models
- [ ] Streaming responses

---

Built with ❤️ for the future of AI orchestration

