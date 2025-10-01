# Manual Setup & Troubleshooting Guide

## 🔧 Manual Flask Server Setup

### Step-by-Step Commands

```bash
# 1. Navigate to Flask Server directory
cd "Flask Server"

# 2. Create virtual environment (first time only)
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Start the server
python app.py
```

### Verify It's Working
- Server should start on: `http://localhost:5000`
- Test health endpoint: `http://localhost:5000/api/health`

---

## 🎨 Manual Frontend Setup

### Step-by-Step Commands

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Check Node.js is installed
node --version
# Should show: v16.x.x or higher

# 3. Check npm is installed
npm --version
# Should show: 8.x.x or higher

# 4. Install dependencies (first time only)
npm install

# 5. Start development server
npm run dev
```

### Common Frontend Issues

#### Issue: "node is not recognized"
**Solution:** Install Node.js from https://nodejs.org/

```bash
# After installing, verify:
node --version
npm --version
```

#### Issue: "npm install" fails
**Solution 1:** Clear npm cache
```bash
npm cache clean --force
npm install
```

**Solution 2:** Delete node_modules and try again
```bash
rmdir /s /q node_modules
del package-lock.json
npm install
```

**Solution 3:** Use --legacy-peer-deps
```bash
npm install --legacy-peer-deps
```

#### Issue: Port 3000 already in use
**Solution:** Kill the process or use different port
```bash
# Windows - Find and kill process on port 3000
netstat -ano | findstr :3000
taskkill /PID <PID_NUMBER> /F

# Or change port in vite.config.js
```

#### Issue: "Cannot find module"
**Solution:** Reinstall dependencies
```bash
cd frontend
rmdir /s /q node_modules
npm install
```

---

## 🐛 Full Troubleshooting Workflow

### Frontend Won't Start - Debug Steps

1. **Check Node.js Installation**
```bash
node --version
npm --version
```
If these fail, install Node.js from https://nodejs.org/

2. **Navigate to Frontend Directory**
```bash
cd "C:\Users\AedhanCornish\OneDrive - Orchard Digital Marketing, Inc\Desktop\Chorus X\frontend"
```

3. **Clean Install**
```bash
# Remove old files
rmdir /s /q node_modules
del package-lock.json

# Fresh install
npm install
```

4. **Check package.json exists**
```bash
dir package.json
# Should show the file
```

5. **Try starting with verbose logging**
```bash
npm run dev --verbose
```

6. **If all else fails, install dependencies individually**
```bash
npm install vue@^3.4.0
npm install vue-router@^4.2.5
npm install axios@^1.6.5
npm install -D @vitejs/plugin-vue@^5.0.0
npm install -D vite@^5.0.11
npm install -D tailwindcss@^3.4.1
npm install -D postcss@^8.4.33
npm install -D autoprefixer@^10.4.16
```

---

## 🔑 Environment Setup

### Create .env file in root directory

```bash
# Navigate to project root
cd "C:\Users\AedhanCornish\OneDrive - Orchard Digital Marketing, Inc\Desktop\Chorus X"

# Create .env file
notepad .env
```

Add your API keys:
```env
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
GROQ_API_KEY=gsk-your-key-here
```

---

## 🏃 Quick Commands Reference

### Start Flask Server (Manual)
```bash
cd "Flask Server"
venv\Scripts\activate
python app.py
```

### Start Frontend (Manual)
```bash
cd frontend
npm run dev
```

### Build Frontend for Production
```bash
cd frontend
npm run build
npm run preview
```

### Check What's Running
```bash
# Windows
netstat -ano | findstr :5000
netstat -ano | findstr :3000

# See all Python processes
tasklist | findstr python

# See all Node processes
tasklist | findstr node
```

### Stop Running Servers
```bash
# Press Ctrl+C in the terminal window
# Or kill by PID:
taskkill /PID <PID_NUMBER> /F
```

---

## 📦 Fresh Install (Nuclear Option)

If everything is broken, start fresh:

```bash
# 1. Delete all generated files
cd "Flask Server"
rmdir /s /q venv
del chorus.db
rmdir /s /q chroma_data
rmdir /s /q uploads

cd ..\frontend
rmdir /s /q node_modules
del package-lock.json
rmdir /s /q dist

# 2. Start Flask Server setup
cd "..\Flask Server"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 3. Start Frontend setup
cd ..\frontend
npm install

# 4. Start everything
cd ..
start_chorus.bat
```

---

## ✅ Verify Everything Works

### Test Flask Server
```bash
curl http://localhost:5000/api/health
```

Should return:
```json
{
  "status": "healthy",
  "service": "Chorus Backend"
}
```

### Test Frontend
Open browser to: `http://localhost:3000`

Should see Chorus interface with green theme.

---

## 🆘 Still Having Issues?

1. **Check Python version:** `python --version` (need 3.8+)
2. **Check Node version:** `node --version` (need 16+)
3. **Check if ports are blocked:** Firewall/antivirus
4. **Run as Administrator:** Right-click batch file → Run as administrator
5. **Check file paths:** Make sure no special characters in folder names

---

## 💡 Pro Tips

- Keep two terminal windows open (one for Flask, one for Frontend)
- Use `Ctrl+C` to gracefully stop servers
- Check console output for specific error messages
- Restart both servers after changing .env file

