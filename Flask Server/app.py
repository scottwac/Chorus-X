from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from database import get_db, init_db, Dataset, ChorusModel, Bot, ChatHistory, UploadedFile
from vector_store import VectorStore
from file_processor import FileProcessor
from chorus_service import ChorusService
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime
import shutil

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize services
vector_store = VectorStore()
file_processor = FileProcessor()
chorus_service = ChorusService()

# Upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize database
init_db()

# ==================== DATASET ENDPOINTS ====================

@app.route('/api/datasets', methods=['GET'])
def get_datasets():
    """Get all datasets"""
    db = get_db()
    datasets = db.query(Dataset).all()
    return jsonify([{
        'id': d.id,
        'name': d.name,
        'description': d.description,
        'file_count': d.file_count,
        'created_at': d.created_at.isoformat()
    } for d in datasets])

@app.route('/api/datasets', methods=['POST'])
def create_dataset():
    """Create a new dataset"""
    try:
        data = request.json
        db = get_db()
        
        # Validate input
        if not data or not data.get('name'):
            return jsonify({'error': 'Dataset name is required'}), 400
        
        # Check if dataset with this name already exists
        existing = db.query(Dataset).filter_by(name=data['name']).first()
        if existing:
            return jsonify({'error': f'Dataset with name "{data["name"]}" already exists'}), 409
        
        # Create unique collection name
        collection_name = f"dataset_{uuid.uuid4().hex[:8]}"
        
        dataset = Dataset(
            name=data['name'],
            description=data.get('description', ''),
            collection_name=collection_name
        )
        
        db.add(dataset)
        db.commit()
        
        # Create vector store collection
        vector_store.create_collection(collection_name)
        
        return jsonify({
            'id': dataset.id,
            'name': dataset.name,
            'description': dataset.description,
            'collection_name': collection_name,
            'created_at': dataset.created_at.isoformat()
        }), 201
    except Exception as e:
        db.rollback()
        print(f"Error creating dataset: {e}")
        return jsonify({'error': f'Failed to create dataset: {str(e)}'}), 500

@app.route('/api/datasets/<int:dataset_id>/upload', methods=['POST'])
def upload_files(dataset_id):
    """Upload files to a dataset"""
    try:
        db = get_db()
        dataset = db.query(Dataset).filter_by(id=dataset_id).first()
        
        if not dataset:
            return jsonify({'error': 'Dataset not found'}), 404
        
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        # Create dataset-specific folder
        dataset_folder = os.path.join(app.config['UPLOAD_FOLDER'], f"dataset_{dataset.id}")
        os.makedirs(dataset_folder, exist_ok=True)
        
        files = request.files.getlist('files')
        processed_files = []
        errors = []
        
        for file in files:
            if file.filename == '':
                continue
            
            try:
                filename = secure_filename(file.filename)
                stored_filename = f"{uuid.uuid4().hex}_{filename}"
                file_path = os.path.join(dataset_folder, stored_filename)
                
                # Save file persistently
                file.save(file_path)
                file_size = os.path.getsize(file_path)
                
                # Process file and extract text/embeddings
                documents = file_processor.process_file(file_path, filename)
                
                # Add to vector store
                vector_store.add_documents(dataset.collection_name, documents)
                
                # Save file metadata to database
                uploaded_file = UploadedFile(
                    dataset_id=dataset.id,
                    original_filename=filename,
                    stored_filename=stored_filename,
                    file_path=file_path,
                    file_type=os.path.splitext(filename)[1],
                    file_size=file_size,
                    chunks_count=len(documents)
                )
                db.add(uploaded_file)
                
                processed_files.append({
                    'id': uploaded_file.id,
                    'filename': filename,
                    'chunks': len(documents),
                    'size': file_size
                })
            except Exception as e:
                errors.append({
                    'filename': file.filename,
                    'error': str(e)
                })
                print(f"Error processing file {file.filename}: {e}")
        
        # Update file count
        dataset.file_count += len(processed_files)
        db.commit()
        
        response = {
            'message': f'Processed {len(processed_files)} files',
            'files': processed_files
        }
        
        if errors:
            response['errors'] = errors
            response['message'] += f', {len(errors)} failed'
        
        return jsonify(response)
    except Exception as e:
        db.rollback()
        print(f"Error uploading files: {e}")
        return jsonify({'error': f'Failed to upload files: {str(e)}'}), 500

@app.route('/api/datasets/<int:dataset_id>', methods=['GET'])
def get_dataset(dataset_id):
    """Get dataset details with files"""
    db = get_db()
    dataset = db.query(Dataset).filter_by(id=dataset_id).first()
    
    if not dataset:
        return jsonify({'error': 'Dataset not found'}), 404
    
    # Get all files in this dataset
    files = db.query(UploadedFile).filter_by(dataset_id=dataset_id).all()
    
    return jsonify({
        'id': dataset.id,
        'name': dataset.name,
        'description': dataset.description,
        'file_count': dataset.file_count,
        'collection_name': dataset.collection_name,
        'created_at': dataset.created_at.isoformat(),
        'files': [{
            'id': f.id,
            'filename': f.original_filename,
            'file_type': f.file_type,
            'file_size': f.file_size,
            'chunks_count': f.chunks_count,
            'created_at': f.created_at.isoformat()
        } for f in files]
    })

@app.route('/api/datasets/<int:dataset_id>/files/<int:file_id>', methods=['GET'])
def get_file_content(dataset_id, file_id):
    """Get file content"""
    db = get_db()
    uploaded_file = db.query(UploadedFile).filter_by(id=file_id, dataset_id=dataset_id).first()
    
    if not uploaded_file:
        return jsonify({'error': 'File not found'}), 404
    
    try:
        # Read file content
        with open(uploaded_file.file_path, 'rb') as f:
            content = f.read()
        
        # Try to decode as text
        try:
            text_content = content.decode('utf-8')
        except:
            text_content = content.decode('latin-1')
        
        return jsonify({
            'id': uploaded_file.id,
            'filename': uploaded_file.original_filename,
            'file_type': uploaded_file.file_type,
            'file_size': uploaded_file.file_size,
            'content': text_content,
            'chunks_count': uploaded_file.chunks_count,
            'created_at': uploaded_file.created_at.isoformat()
        })
    except Exception as e:
        return jsonify({'error': f'Failed to read file: {str(e)}'}), 500

@app.route('/api/datasets/<int:dataset_id>/files/<int:file_id>', methods=['DELETE'])
def delete_file(dataset_id, file_id):
    """Delete a file from dataset"""
    db = get_db()
    uploaded_file = db.query(UploadedFile).filter_by(id=file_id, dataset_id=dataset_id).first()
    
    if not uploaded_file:
        return jsonify({'error': 'File not found'}), 404
    
    try:
        # Delete physical file
        if os.path.exists(uploaded_file.file_path):
            os.remove(uploaded_file.file_path)
        
        # Delete from database
        db.delete(uploaded_file)
        
        # Update dataset file count
        dataset = db.query(Dataset).filter_by(id=dataset_id).first()
        if dataset:
            dataset.file_count = max(0, dataset.file_count - 1)
        
        db.commit()
        
        return jsonify({'message': 'File deleted successfully'})
    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Failed to delete file: {str(e)}'}), 500

@app.route('/api/datasets/<int:dataset_id>', methods=['DELETE'])
def delete_dataset(dataset_id):
    """Delete a dataset"""
    db = get_db()
    dataset = db.query(Dataset).filter_by(id=dataset_id).first()
    
    if not dataset:
        return jsonify({'error': 'Dataset not found'}), 404
    
    # Delete all uploaded files
    uploaded_files = db.query(UploadedFile).filter_by(dataset_id=dataset_id).all()
    for uploaded_file in uploaded_files:
        if os.path.exists(uploaded_file.file_path):
            os.remove(uploaded_file.file_path)
        db.delete(uploaded_file)
    
    # Delete dataset folder
    dataset_folder = os.path.join(app.config['UPLOAD_FOLDER'], f"dataset_{dataset.id}")
    if os.path.exists(dataset_folder):
        shutil.rmtree(dataset_folder)
    
    # Delete vector store collection
    vector_store.delete_collection(dataset.collection_name)
    
    # Delete from database
    db.delete(dataset)
    db.commit()
    
    return jsonify({'message': 'Dataset deleted'})

# ==================== CHORUS MODEL ENDPOINTS ====================

@app.route('/api/chorus-models', methods=['GET'])
def get_chorus_models():
    """Get all Chorus models"""
    db = get_db()
    models = db.query(ChorusModel).all()
    return jsonify([{
        'id': m.id,
        'name': m.name,
        'description': m.description,
        'responder_llms': m.responder_llms,
        'evaluator_llms': m.evaluator_llms,
        'created_at': m.created_at.isoformat()
    } for m in models])

@app.route('/api/chorus-models', methods=['POST'])
def create_chorus_model():
    """Create a new Chorus model"""
    try:
        data = request.json
        db = get_db()
        
        # Validate input
        if not data or not data.get('name'):
            return jsonify({'error': 'Chorus model name is required'}), 400
        
        # Check if model with this name already exists
        existing = db.query(ChorusModel).filter_by(name=data['name']).first()
        if existing:
            return jsonify({'error': f'Chorus model with name "{data["name"]}" already exists'}), 409
        
        model = ChorusModel(
            name=data['name'],
            description=data.get('description', ''),
            responder_llms=data['responder_llms'],
            evaluator_llms=data['evaluator_llms']
        )
        
        db.add(model)
        db.commit()
        
        return jsonify({
            'id': model.id,
            'name': model.name,
            'description': model.description,
            'responder_llms': model.responder_llms,
            'evaluator_llms': model.evaluator_llms,
            'created_at': model.created_at.isoformat()
        }), 201
    except Exception as e:
        db.rollback()
        print(f"Error creating chorus model: {e}")
        return jsonify({'error': f'Failed to create chorus model: {str(e)}'}), 500

@app.route('/api/chorus-models/<int:model_id>', methods=['DELETE'])
def delete_chorus_model(model_id):
    """Delete a Chorus model"""
    db = get_db()
    model = db.query(ChorusModel).filter_by(id=model_id).first()
    
    if not model:
        return jsonify({'error': 'Chorus model not found'}), 404
    
    db.delete(model)
    db.commit()
    
    return jsonify({'message': 'Chorus model deleted'})

# ==================== BOT ENDPOINTS ====================

@app.route('/api/bots', methods=['GET'])
def get_bots():
    """Get all bots"""
    db = get_db()
    bots = db.query(Bot).all()
    return jsonify([{
        'id': b.id,
        'name': b.name,
        'instructions': b.instructions,
        'dataset_id': b.dataset_id,
        'chorus_model_id': b.chorus_model_id,
        'rag_results_count': b.rag_results_count,
        'created_at': b.created_at.isoformat()
    } for b in bots])

@app.route('/api/bots', methods=['POST'])
def create_bot():
    """Create a new bot"""
    try:
        data = request.json
        db = get_db()
        
        # Validate input
        if not data or not data.get('name'):
            return jsonify({'error': 'Bot name is required'}), 400
        if not data.get('instructions'):
            return jsonify({'error': 'Bot instructions are required'}), 400
        
        # Check if bot with this name already exists
        existing = db.query(Bot).filter_by(name=data['name']).first()
        if existing:
            return jsonify({'error': f'Bot with name "{data["name"]}" already exists'}), 409
        
        bot = Bot(
            name=data['name'],
            instructions=data['instructions'],
            dataset_id=data.get('dataset_id'),
            chorus_model_id=data.get('chorus_model_id'),
            rag_results_count=data.get('rag_results_count', 5)
        )
        
        db.add(bot)
        db.commit()
        
        return jsonify({
            'id': bot.id,
            'name': bot.name,
            'instructions': bot.instructions,
            'dataset_id': bot.dataset_id,
            'chorus_model_id': bot.chorus_model_id,
            'rag_results_count': bot.rag_results_count,
            'created_at': bot.created_at.isoformat()
        }), 201
    except Exception as e:
        db.rollback()
        print(f"Error creating bot: {e}")
        return jsonify({'error': f'Failed to create bot: {str(e)}'}), 500

@app.route('/api/bots/<int:bot_id>', methods=['DELETE'])
def delete_bot(bot_id):
    """Delete a bot"""
    db = get_db()
    bot = db.query(Bot).filter_by(id=bot_id).first()
    
    if not bot:
        return jsonify({'error': 'Bot not found'}), 404
    
    db.delete(bot)
    db.commit()
    
    return jsonify({'message': 'Bot deleted'})

@app.route('/api/bots/<int:bot_id>/chat', methods=['POST'])
def chat_with_bot(bot_id):
    """Send a message to a bot and get response"""
    data = request.json
    user_message = data.get('message', '')
    rag_count = data.get('rag_count')  # Optional override for RAG results count
    
    db = get_db()
    bot = db.query(Bot).filter_by(id=bot_id).first()
    
    if not bot:
        return jsonify({'error': 'Bot not found'}), 404
    
    # Get dataset and chorus model
    dataset = db.query(Dataset).filter_by(id=bot.dataset_id).first() if bot.dataset_id else None
    chorus_model = db.query(ChorusModel).filter_by(id=bot.chorus_model_id).first() if bot.chorus_model_id else None
    
    if not chorus_model:
        return jsonify({'error': 'Bot has no Chorus model configured'}), 400
    
    # Step 1: Classify user intent using GPT-5
    from llm_service import LLMService
    llm_service_instance = LLMService()
    intent = llm_service_instance.classify_user_intent(user_message)
    
    print(f"User intent classified as: {intent}")
    
    # Handle different intents
    if intent == 'find_image':
        # Image search functionality (to be implemented)
        response_text = "🖼️ Image search functionality is coming soon! I detected you want to find an image from the dataset."
        
        chat_entry = ChatHistory(
            bot_id=bot_id,
            user_message=user_message,
            bot_response=response_text
        )
        db.add(chat_entry)
        db.commit()
        
        return jsonify({
            'response': response_text,
            'intent': intent,
            'debug': {
                'intent_detected': intent,
                'status': 'not_implemented'
            }
        })
    
    elif intent == 'generate_image':
        # Image generation functionality (to be implemented)
        response_text = "🎨 Image generation functionality is coming soon! I detected you want to create a new image."
        
        chat_entry = ChatHistory(
            bot_id=bot_id,
            user_message=user_message,
            bot_response=response_text
        )
        db.add(chat_entry)
        db.commit()
        
        return jsonify({
            'response': response_text,
            'intent': intent,
            'debug': {
                'intent_detected': intent,
                'status': 'not_implemented'
            }
        })
    
    # Intent is 'text' - proceed with normal Chorus flow
    # Query vector store for relevant context
    context = ""
    n_results = rag_count if rag_count is not None else (bot.rag_results_count or 5)
    if dataset:
        relevant_docs = vector_store.query_collection(dataset.collection_name, user_message, n_results=n_results)
        context = "\n\n".join([f"[{doc['metadata'].get('filename', 'Unknown')}]\n{doc['text']}" for doc in relevant_docs])
    
    # Add bot instructions to context
    full_context = f"Bot Instructions:\n{bot.instructions}\n\n"
    if context:
        full_context += f"Relevant Information:\n{context}"
    
    # Run Chorus model
    result = chorus_service.run_chorus(
        user_query=user_message,
        context=full_context,
        responder_llms=chorus_model.responder_llms,
        evaluator_llms=chorus_model.evaluator_llms
    )
    
    # Save to chat history
    chat_entry = ChatHistory(
        bot_id=bot_id,
        user_message=user_message,
        bot_response=result['final_response']
    )
    db.add(chat_entry)
    db.commit()
    
    return jsonify({
        'response': result['final_response'],
        'intent': intent,
        'rag_count_used': n_results,
        'debug': {
            'intent_detected': intent,
            'rag_count_used': n_results,
            'all_responses': result['responses'],
            'votes': result.get('votes'),
            'vote_counts': result.get('vote_counts'),
            'winner_index': result.get('winner_index')
        }
    })

@app.route('/api/bots/<int:bot_id>/history', methods=['GET'])
def get_chat_history(bot_id):
    """Get chat history for a bot"""
    db = get_db()
    history = db.query(ChatHistory).filter_by(bot_id=bot_id).order_by(ChatHistory.created_at).all()
    
    return jsonify([{
        'id': h.id,
        'user_message': h.user_message,
        'bot_response': h.bot_response,
        'created_at': h.created_at.isoformat()
    } for h in history])

# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Chorus Backend',
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)

