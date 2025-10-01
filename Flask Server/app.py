from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import os
from datetime import datetime, UTC
from database import get_db, init_db, Dataset, ChorusModel, Bot, ChatHistory, UploadedFile
from vector_store import VectorStore
from file_processor import FileProcessor
from chorus_service import ChorusService
from chart_generator import ChartGenerator
from werkzeug.utils import secure_filename
import uuid
import shutil

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize services
vector_store = VectorStore()
file_processor = FileProcessor()
chorus_service = ChorusService()
chart_generator = ChartGenerator()

# Upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Generated charts folder
CHARTS_FOLDER = 'generated_charts'
os.makedirs(CHARTS_FOLDER, exist_ok=True)

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
            'created_at': dataset.created_at.isoformat() if dataset.created_at else datetime.now(UTC).isoformat()
        }), 201
    except Exception as e:
        db.rollback()
        print(f"Error creating dataset: {e}")
        return jsonify({'error': f'Failed to create dataset: {str(e)}'}), 500

@app.route('/api/datasets/<int:dataset_id>/upload', methods=['POST'])
def upload_files(dataset_id):
    """Upload files to a dataset (including ZIP files that will be extracted)"""
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
        total_files = 0
        processed_count = 0
        
        # Count total files including those in ZIP files
        for file in files:
            if file.filename:
                filename = secure_filename(file.filename)
                if filename.lower().endswith('.zip'):
                    # Count files in ZIP
                    temp_zip_path = os.path.join(dataset_folder, f"temp_{filename}")
                    file.save(temp_zip_path)
                    try:
                        import zipfile
                        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                            total_files += len([f for f in zip_ref.namelist() if not f.endswith('/')])
                    except Exception as e:
                        print(f"Error counting ZIP files: {e}")
                        total_files += 1
                    finally:
                        if os.path.exists(temp_zip_path):
                            os.remove(temp_zip_path)
                else:
                    total_files += 1
        
        print(f"Total files to process: {total_files}")
        
        for file in files:
            if file.filename == '':
                continue
            
            try:
                filename = secure_filename(file.filename)
                file_extension = os.path.splitext(filename)[1].lower()
                
                # Check if this is a ZIP file
                if file_extension == '.zip':
                    # Handle ZIP file extraction
                    import zipfile
                    import tempfile
                    
                    # Save ZIP to temp location
                    temp_zip_path = os.path.join(dataset_folder, f"temp_{uuid.uuid4().hex}.zip")
                    file.save(temp_zip_path)
                    
                    try:
                        # Extract ZIP file
                        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                            # Get list of files in ZIP
                            zip_files = [f for f in zip_ref.namelist() if not f.endswith('/') and not f.startswith('__MACOSX')]
                            
                            print(f"Extracting ZIP file '{filename}' with {len(zip_files)} files")
                            
                            # Create temp extraction folder
                            extract_folder = os.path.join(dataset_folder, f"temp_extract_{uuid.uuid4().hex}")
                            os.makedirs(extract_folder, exist_ok=True)
                            
                            # Extract files
                            zip_ref.extractall(extract_folder)
                            
                            # Process each extracted file
                            for i, zip_file_name in enumerate(zip_files):
                                processed_count += 1
                                print(f"Processing file {processed_count}/{total_files}: {zip_file_name}")
                                
                                try:
                                    extracted_path = os.path.join(extract_folder, zip_file_name)
                                    
                                    if not os.path.isfile(extracted_path):
                                        continue
                                    
                                    # Get just the filename (remove directory path)
                                    original_filename = os.path.basename(zip_file_name)
                                    original_filename = secure_filename(original_filename)
                                    
                                    # Move to dataset folder with unique name
                                    stored_filename = f"{uuid.uuid4().hex}_{original_filename}"
                                    final_path = os.path.join(dataset_folder, stored_filename)
                                    shutil.move(extracted_path, final_path)
                                    
                                    file_size = os.path.getsize(final_path)
                                    
                                    # Process file
                                    documents = file_processor.process_file(final_path, original_filename)
                                    
                                    # Add to vector store
                                    vector_store.add_documents(dataset.collection_name, documents)
                                    
                                    # Save file metadata
                                    uploaded_file = UploadedFile(
                                        dataset_id=dataset.id,
                                        original_filename=original_filename,
                                        stored_filename=stored_filename,
                                        file_path=final_path,
                                        file_type=os.path.splitext(original_filename)[1],
                                        file_size=file_size,
                                        chunks_count=len(documents)
                                    )
                                    db.add(uploaded_file)
                                    
                                    processed_files.append({
                                        'id': uploaded_file.id,
                                        'filename': original_filename,
                                        'chunks': len(documents),
                                        'size': file_size,
                                        'from_zip': filename
                                    })
                                    
                                except Exception as e:
                                    errors.append({
                                        'filename': zip_file_name,
                                        'error': f"Error in ZIP: {str(e)}"
                                    })
                                    print(f"Error processing file from ZIP {zip_file_name}: {e}")
                            
                            # Cleanup temp extraction folder
                            shutil.rmtree(extract_folder, ignore_errors=True)
                            
                    finally:
                        # Remove temp ZIP file
                        if os.path.exists(temp_zip_path):
                            os.remove(temp_zip_path)
                
                else:
                    # Regular file upload (not a ZIP)
                    processed_count += 1
                    print(f"Processing file {processed_count}/{total_files}: {filename}")
                    
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
        # Check if it's an image file
        if uploaded_file.file_type in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
            # For images, we'll return the file path and let frontend handle display
            return jsonify({
                'id': uploaded_file.id,
                'filename': uploaded_file.original_filename,
                'file_type': uploaded_file.file_type,
                'file_size': uploaded_file.file_size,
                'is_image': True,
                'chunks_count': uploaded_file.chunks_count,
                'created_at': uploaded_file.created_at.isoformat()
            })
        
        # Read text file content
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
            'is_image': False,
            'chunks_count': uploaded_file.chunks_count,
            'created_at': uploaded_file.created_at.isoformat()
        })
    except Exception as e:
        return jsonify({'error': f'Failed to read file: {str(e)}'}), 500

@app.route('/api/datasets/<int:dataset_id>/files/<int:file_id>/image', methods=['GET'])
def get_file_image(dataset_id, file_id):
    """Get actual image file"""
    from flask import send_file
    db = get_db()
    uploaded_file = db.query(UploadedFile).filter_by(id=file_id, dataset_id=dataset_id).first()
    
    if not uploaded_file:
        return jsonify({'error': 'File not found'}), 404
    
    if uploaded_file.file_type not in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
        return jsonify({'error': 'File is not an image'}), 400
    
    try:
        return send_file(uploaded_file.file_path, mimetype=f'image/{uploaded_file.file_type[1:]}')
    except Exception as e:
        return jsonify({'error': f'Failed to read image: {str(e)}'}), 500

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
    image_settings = data.get('image_settings', {})  # Image search settings from frontend
    
    db = get_db()
    bot = db.query(Bot).filter_by(id=bot_id).first()
    
    if not bot:
        return jsonify({'error': 'Bot not found'}), 404
    
    # Get dataset and chorus model
    dataset = db.query(Dataset).filter_by(id=bot.dataset_id).first() if bot.dataset_id else None
    chorus_model = db.query(ChorusModel).filter_by(id=bot.chorus_model_id).first() if bot.chorus_model_id else None
    
    if not chorus_model:
        return jsonify({'error': 'Bot has no Chorus model configured'}), 400
    
    # Track processing steps for frontend display
    processing_steps = []
    
    # Step 1: Classify user intent using GPT-5
    from llm_service import LLMService
    llm_service_instance = LLMService()
    processing_steps.append('Classifying user intent...')
    intent = llm_service_instance.classify_user_intent(user_message)
    processing_steps.append(f'Determined user inquiry as: {intent}')
    
    print(f"User intent classified as: {intent}")
    
    # Handle different intents
    if intent == 'find_image':
        # Image search functionality
        processing_steps.append('Searching for images in dataset...')
        if not dataset:
            response_text = "🖼️ No dataset is connected to this bot. Please add a dataset to search for images."
            
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
                'images': [],
                'processing_steps': processing_steps,
                'debug': {
                    'intent_detected': intent,
                    'status': 'no_dataset'
                }
            })
        
        # Search for image-related documents in the vector store
        n_results = rag_count if rag_count is not None else (bot.rag_results_count or 5)
        processing_steps.append(f'Retrieving {n_results} relevant documents...')
        relevant_docs = vector_store.query_collection(dataset.collection_name, user_message, n_results=n_results * 2)
        
        # Get image search settings from frontend
        max_images = image_settings.get('maxResults', 3)
        min_confidence = image_settings.get('minConfidence', 0.6)
        
        # Filter for image-related documents
        image_results = []
        seen_filenames = set()
        
        for doc in relevant_docs:
            metadata = doc.get('metadata', {})
            image_type = metadata.get('image_type')
            filename = metadata.get('filename', '')
            relevance_score = 1 - doc.get('distance', 0)
            
            # Check if this is an image document and meets confidence threshold
            if image_type in ['ocr', 'description'] and filename and filename not in seen_filenames:
                # Apply confidence filter
                if relevance_score >= min_confidence:
                    seen_filenames.add(filename)
                    
                    # Get the actual file from database
                    uploaded_file = db.query(UploadedFile).filter_by(
                        dataset_id=dataset.id,
                        original_filename=filename
                    ).first()
                    
                    if uploaded_file and uploaded_file.file_type in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
                        image_results.append({
                            'filename': filename,
                            'file_id': uploaded_file.id,
                            'file_path': uploaded_file.file_path,
                            'description': doc.get('text', ''),
                            'relevance_score': relevance_score,
                            'file_size': uploaded_file.file_size
                        })
        
        # Limit to max results from settings
        image_results = image_results[:max_images]
        
        if image_results:
            confidence_text = f" (min {int(min_confidence * 100)}% confidence)" if min_confidence > 0 else ""
            response_text = f"🖼️ I found {len(image_results)} relevant image(s) in the dataset{confidence_text}:"
            for idx, img in enumerate(image_results, 1):
                response_text += f"\n\n{idx}. **{img['filename']}**"
                response_text += f" - {int(img['relevance_score'] * 100)}% match"
                # Add a snippet of the description
                desc_snippet = img['description'][:150] + "..." if len(img['description']) > 150 else img['description']
                response_text += f"\n   {desc_snippet}"
        else:
            if min_confidence > 0:
                response_text = f"🖼️ I couldn't find any images matching your query with at least {int(min_confidence * 100)}% confidence. Try lowering the minimum confidence threshold or being more specific."
            else:
                response_text = "🖼️ I couldn't find any relevant images in the dataset for your query. Try being more specific or check if images have been uploaded."
        
        chat_entry = ChatHistory(
            bot_id=bot_id,
            user_message=user_message,
            bot_response=response_text
        )
        db.add(chat_entry)
        db.commit()
        
        processing_steps.append(f'Found {len(image_results)} matching images')
        
        return jsonify({
            'response': response_text,
            'intent': intent,
            'images': image_results,
            'processing_steps': processing_steps,
            'debug': {
                'intent_detected': intent,
                'images_found': len(image_results),
                'total_docs_searched': len(relevant_docs),
                'rag_count_used': n_results
            }
        })
    
    elif intent == 'generate_chart':
        # Chart generation functionality
        try:
            processing_steps.append('Retrieving relevant data from dataset...')
            # Get RAG context for data
            n_results = rag_count if rag_count is not None else (bot.rag_results_count or 5)
            
            context = ""
            if dataset:
                # Get relevant context from dataset
                relevant_docs = vector_store.query_collection(dataset.collection_name, user_message, n_results=n_results)
                context = "\n\n".join([f"[{doc['metadata'].get('filename', 'Unknown')}]\n{doc['text']}" for doc in relevant_docs])
            
            # Generate the chart
            processing_steps.append('Analyzing data and generating chart...')
            print(f"Generating chart for query: {user_message}")
            chart_result = chart_generator.generate_chart(user_message, context)
            processing_steps.append('Chart generated successfully')
            
            # Generate a text response explaining the chart
            explanation_prompt = f"""The user asked: "{user_message}"

A chart has been generated based on the available data. Provide a brief explanation of what the chart shows.

Context data:
{context[:1000]}"""
            
            explanation = llm_service_instance.call_llm(
                'openai',
                'gpt-5-2025-08-07',
                [{'role': 'user', 'content': explanation_prompt}]
            )
            
            # Save to chat history
            chat_entry = ChatHistory(
                bot_id=bot_id,
                user_message=user_message,
                bot_response=explanation
            )
            db.add(chat_entry)
            db.commit()
            
            return jsonify({
                'response': explanation,
                'intent': intent,
                'generated_chart': {
                    'filename': chart_result['filename'],
                    'chart_type': chart_result['chart_type'],
                    'title': chart_result['title']
                },
                'processing_steps': processing_steps,
                'debug': {
                    'intent_detected': intent,
                    'rag_count_used': n_results
                }
            })
            
        except Exception as e:
            error_message = f"Failed to generate chart: {str(e)}"
            print(error_message)
            processing_steps.append(f'Error: {error_message}')
            
            chat_entry = ChatHistory(
                bot_id=bot_id,
                user_message=user_message,
                bot_response=error_message
            )
            db.add(chat_entry)
            db.commit()
            
            return jsonify({
                'response': error_message,
                'intent': intent,
                'processing_steps': processing_steps,
                'debug': {
                    'intent_detected': intent,
                    'error': str(e)
                }
            })
    
    elif intent == 'generate_image':
        # Image generation functionality
        try:
            reference_image_path = None
            reference_filename = None
            
            # Check if the user is referencing a specific image file from their dataset
            if dataset:
                # Extract potential filenames from the user message
                # Look for common image extensions
                import re
                filename_pattern = r'([A-Za-z0-9_\-\.]+\.(png|jpg|jpeg|gif|bmp|webp))'
                matches = re.findall(filename_pattern, user_message, re.IGNORECASE)
                
                if matches:
                    # User mentioned a filename - try to find it in the dataset
                    mentioned_filename = matches[0][0]
                    
                    uploaded_file = db.query(UploadedFile).filter_by(
                        dataset_id=dataset.id,
                        original_filename=mentioned_filename
                    ).first()
                    
                    if uploaded_file and uploaded_file.file_type in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
                        reference_image_path = uploaded_file.file_path
                        reference_filename = uploaded_file.original_filename
                        print(f"Found reference image: {reference_filename} at {reference_image_path}")
                    else:
                        print(f"Mentioned file '{mentioned_filename}' not found in dataset or not an image")
            
            # Get image generation settings
            quality = image_settings.get('quality', 'high')
            size = image_settings.get('size', '1024x1024')
            
            # Generate the image
            print(f"Generating image for prompt: {user_message}")
            image_result = llm_service_instance.generate_image(
                prompt=user_message,
                reference_image_path=reference_image_path,
                quality=quality,
                size=size
            )
            
            # Save the generated image
            import base64
            import uuid
            
            generated_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'generated')
            os.makedirs(generated_folder, exist_ok=True)
            
            image_filename = f"generated_{uuid.uuid4().hex}.png"
            image_path = os.path.join(generated_folder, image_filename)
            
            # Decode and save
            image_bytes = base64.b64decode(image_result['image_base64'])
            with open(image_path, 'wb') as f:
                f.write(image_bytes)
            
            # Create response text
            if reference_filename:
                response_text = f"🎨 I've edited the image based on your request!\n\n**Original:** {reference_filename}\n**Edit:** {user_message}"
            else:
                response_text = f"🎨 I've generated an image for you!\n\n**Prompt:** {image_result['revised_prompt']}"
            
            # Save to chat history
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
                'generated_image': {
                    'filename': image_filename,
                    'path': image_path,
                    'prompt': image_result['revised_prompt'],
                    'is_edit': reference_image_path is not None
                },
                'debug': {
                    'intent_detected': intent,
                    'quality': quality,
                    'size': size,
                    'revised_prompt': image_result['revised_prompt']
                }
            })
            
        except Exception as e:
            print(f"Error in image generation: {e}")
            error_text = f"🎨 Sorry, I encountered an error while generating the image: {str(e)}"
            
            chat_entry = ChatHistory(
                bot_id=bot_id,
                user_message=user_message,
                bot_response=error_text
            )
            db.add(chat_entry)
            db.commit()
            
            return jsonify({
                'response': error_text,
                'intent': intent,
                'debug': {
                    'intent_detected': intent,
                    'error': str(e)
                }
            }), 500
    
    # Intent is 'text' - proceed with normal Chorus flow
    # Query vector store for relevant context
    processing_steps.append(f'Retrieving relevant context from dataset...')
    context = ""
    n_results = rag_count if rag_count is not None else (bot.rag_results_count or 5)
    if dataset:
        relevant_docs = vector_store.query_collection(dataset.collection_name, user_message, n_results=n_results)
        context = "\n\n".join([f"[{doc['metadata'].get('filename', 'Unknown')}]\n{doc['text']}" for doc in relevant_docs])
        processing_steps.append(f'Retrieved {n_results} relevant context chunks')
    
    # Add bot instructions to context
    full_context = f"Bot Instructions:\n{bot.instructions}\n\n"
    if context:
        full_context += f"Relevant Information:\n{context}"
    
    # Run Chorus model
    num_responders = len(chorus_model.responder_llms)
    num_evaluators = len(chorus_model.evaluator_llms)
    processing_steps.append(f'Generating {num_responders} response(s)...')
    
    result = chorus_service.run_chorus(
        user_query=user_message,
        context=full_context,
        responder_llms=chorus_model.responder_llms,
        evaluator_llms=chorus_model.evaluator_llms
    )
    
    if num_evaluators > 0 and num_responders > 1:
        processing_steps.append(f'Evaluating responses with {num_evaluators} evaluator(s)...')
        processing_steps.append(f'Selected best response')
    else:
        processing_steps.append('Response generated successfully')
    
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
        'processing_steps': processing_steps,
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

@app.route('/api/bots/<int:bot_id>/history', methods=['DELETE'])
def clear_chat_history(bot_id):
    """Clear chat history for a bot"""
    try:
        db = get_db()
        # Delete all chat history for this bot
        db.query(ChatHistory).filter_by(bot_id=bot_id).delete()
        db.commit()
        
        return jsonify({'message': 'Chat history cleared successfully'})
    except Exception as e:
        db.rollback()
        print(f"Error clearing chat history: {e}")
        return jsonify({'error': f'Failed to clear chat history: {str(e)}'}), 500

# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Chorus Backend',
        'timestamp': datetime.now(UTC).isoformat()
    })

@app.route('/api/generated-images/<path:filename>', methods=['GET'])
def serve_generated_image(filename):
    """Serve generated images"""
    try:
        generated_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'generated')
        return send_file(os.path.join(generated_folder, filename), mimetype='image/png')
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/api/generated-charts/<path:filename>', methods=['GET'])
def serve_generated_chart(filename):
    """Serve generated charts"""
    try:
        return send_file(os.path.join(CHARTS_FOLDER, filename), mimetype='image/png')
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)

