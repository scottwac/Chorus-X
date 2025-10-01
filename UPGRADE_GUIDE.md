# Database Error Fix

## Problem
You're seeing this error:
```
sqlite3.OperationalError: no such column: bots.rag_results_count
```

This happens because we added new database columns, but your existing database doesn't have them.

## Solution

### Option 1: Quick Reset (Deletes All Data)

**Windows:**
```bash
# Double-click reset_database.bat
# OR run manually:
cd "Flask Server"
del chorus.db
rmdir /s /q chroma_data
rmdir /s /q uploads
python -c "from database import init_db; init_db()"
```

**Mac/Linux:**
```bash
cd "Flask Server"
rm chorus.db
rm -rf chroma_data
rm -rf uploads  
python -c "from database import init_db; init_db()"
```

Then restart your Flask server!

---

### Option 2: Manual Column Addition (Keeps Data)

If you want to keep your existing data:

```bash
cd "Flask Server"
sqlite3 chorus.db
```

Then run these SQL commands:
```sql
-- Add new columns
ALTER TABLE bots ADD COLUMN rag_results_count INTEGER DEFAULT 5;
ALTER TABLE uploaded_files ADD COLUMN dataset_id INTEGER;
ALTER TABLE uploaded_files ADD COLUMN original_filename VARCHAR(255);
ALTER TABLE uploaded_files ADD COLUMN stored_filename VARCHAR(255);
ALTER TABLE uploaded_files ADD COLUMN file_path VARCHAR(512);
ALTER TABLE uploaded_files ADD COLUMN file_type VARCHAR(50);
ALTER TABLE uploaded_files ADD COLUMN file_size INTEGER;
ALTER TABLE uploaded_files ADD COLUMN chunks_count INTEGER DEFAULT 0;
ALTER TABLE uploaded_files ADD COLUMN created_at DATETIME;

-- Exit sqlite3
.quit
```

---

## What Changed?

**New columns added:**
1. `bots.rag_results_count` - Control how many context chunks to retrieve
2. `uploaded_files` table - Track all uploaded files with metadata

These enable:
- ✅ Adjustable RAG results per bot
- ✅ File management (view, delete individual files)
- ✅ Image search functionality
- ✅ Better file tracking

---

## After Reset

You'll need to:
1. ✅ Recreate your datasets
2. ✅ Re-upload your files  
3. ✅ Recreate your Chorus models
4. ✅ Recreate your bots

Everything will work with the new features!

