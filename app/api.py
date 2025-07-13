import os
from quart import Quart, request, jsonify
from werkzeug.utils import secure_filename
from .populate_database import main as populate_main, clear_database
from .query_data import query_rag
from dotenv import load_dotenv

load_dotenv()

DATA_PATH = os.getenv("DATA_PATH")
UPLOAD_FOLDER = DATA_PATH
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def setup_routes(app: Quart):

    @app.route('/ingest-data', methods=['POST'])
    async def upload_file():
        files = await request.files
        if 'file' not in files:
            return jsonify({"error": "No file part"}), 400
        file = files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            await file.save(file_path)
            populate_main()
            return jsonify({"success": True, "file_path": file_path}), 200
        else:
            return jsonify({"error": "File type not allowed"}), 400

    @app.route('/fetch-response', methods=['POST'])
    async def query():
        data = await request.json
        query_text = data.get('text')
        session_id = data.get('session_id')
        if not query_text:
            return jsonify({"error": "Query text is required"}), 400
        if not session_id:
            return jsonify({"error": "Session ID is required"}), 400
        try:
            response_text = query_rag(session_id, query_text)
        except FileNotFoundError as e:
            return jsonify({"error": str(e)}), 404
        return jsonify({"response": response_text}), 200

    @app.route('/populate', methods=['POST'])
    async def populate():
        populate_main()
        return jsonify({"success": True}), 200
    
    @app.route('/resetDatabase', methods=['POST'])
    async def clear_db():
        try:
            clear_database()
            return jsonify({"success": True, "message": "Database reset successfully"}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500