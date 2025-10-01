# Chorus Quick Start Guide

## 🚀 Running Chorus

### Option 1: All-in-One (Recommended)
```bash
start_chorus.bat
```
Double-click `start_chorus.bat` to start both Flask Server and Frontend automatically.

### Option 2: Start Components Separately

**Start Flask Server Only:**
```bash
start_server.bat
```

**Start Frontend Only:**
```bash
start_frontend.bat
```

---

## 🔑 First Time Setup

### 1. Create `.env` File
In the root `Chorus X` folder, create a file named `.env`:

```env
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
GROQ_API_KEY=gsk-your-key-here
```

### 2. Install Tesseract OCR
- **Windows**: https://github.com/UB-Mannheim/tesseract/wiki
- **Mac**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

### 3. Run Chorus
```bash
start_chorus.bat
```

---

## 📋 Available Models

### OpenAI
- `gpt-5-2025-08-07` ⭐ Latest GPT-5
- `gpt-5-nano` ⚡ Fast GPT-5
- `gpt-4o` 👁️ GPT-4 with vision
- `gpt-4o-mini` 💰 Budget-friendly
- `gpt-3.5-turbo` 🏃 Fast & efficient

### Anthropic Claude
- `claude-3-7-sonnet-20250219` ⭐ Newest Claude
- `claude-3-5-sonnet-20241022` 🎯 Highly capable
- `claude-3-5-haiku-20241022` ⚡ Fast Claude
- `claude-3-opus-20240229` 🧠 Most intelligent

### Groq
- `llama-3.3-70b-versatile` 🦙 Latest Llama
- `llama-3.1-8b-instant` ⚡ Ultra fast
- `mixtral-8x7b-32768` 🎭 Mixture of experts

See `MODELS_REFERENCE.md` for complete model information.

---

## 🎯 Basic Workflow

### 1. Create a Dataset
- Go to **Datasets** tab
- Click "New Dataset"
- Drag & drop files (PDF, DOCX, TXT, images)

### 2. Create a Chorus Model
- Go to **Chorus Models** tab
- Click "New Chorus Model"
- Add **Responder LLMs** (generate answers)
  - Example: GPT-5, Claude 3.7, Llama 3.3
- Add **Evaluator LLMs** (vote on best answer)
  - Example: Claude 3.7, GPT-5

### 3. Create a Bot
- Go to **Bots** tab
- Click "New Bot"
- Write instructions for the bot
- Select your dataset
- Select your Chorus model
- Click "Create"

### 4. Chat!
- Click on your bot
- Start asking questions
- Enable "Show Debug" to see all LLM responses and votes

---

## 🌐 Access Points

- **Frontend**: http://localhost:3000
- **API**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/health

---

## 💡 Quick Tips

1. **Multiple Responders = Better Answers**
   - Use 3-5 different models as responders
   - They'll generate diverse perspectives

2. **Choose Smart Evaluators**
   - Use Claude 3.7 or GPT-5 as evaluators
   - They're best at judging quality

3. **Dataset Quality Matters**
   - Upload relevant, well-formatted documents
   - Images work great with OCR + AI description

4. **Debug Mode is Your Friend**
   - See exactly what each model said
   - Understand why a particular answer won

5. **Mix Providers**
   - Combine OpenAI + Anthropic + Groq
   - Get diverse viewpoints and approaches

---

## 🔧 Troubleshooting

**"Module not found" errors:**
```bash
cd "Flask Server"
venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend won't start:**
```bash
cd frontend
npm install
npm run dev
```

**API key errors:**
- Check `.env` file is in root folder
- Verify API keys are valid
- Restart the server after updating `.env`

**Tesseract errors:**
- Make sure Tesseract is installed
- Add to PATH if on Windows

---

## 📚 Documentation

- `README.md` - Full documentation
- `MODELS_REFERENCE.md` - Complete model list with recommendations
- `env.example.txt` - Template for API keys

---

**Ready to orchestrate multiple AI models? Start now:**
```bash
start_chorus.bat
```

Happy orchestrating! 🎭

