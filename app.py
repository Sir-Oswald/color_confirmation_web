from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
import os
import json
import traceback
from utils.color_processing import find_main_colors, snap_to_allowed_colors
from utils.file_handling import save_uploaded_files

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'data/patterns'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB limit
app.config['RESULTS_FILE'] = os.path.join(app.config['UPLOAD_FOLDER'], 'color_confirmation_results.json')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/confirm_colors')
def confirm_colors():
    pattern_folders = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isdir(os.path.join(app.config['UPLOAD_FOLDER'], f))]
    return render_template('confirm_colors.html', pattern_folders=pattern_folders)

@app.route('/get_pattern_folders')
def get_pattern_folders():
    pattern_folders = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isdir(os.path.join(app.config['UPLOAD_FOLDER'], f))]
    return jsonify({'pattern_folders': pattern_folders})

@app.route('/get_images')
def get_images():
    folder = request.args.get('folder')
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder)
    images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    return jsonify({'images': images})

@app.route('/pattern_image/<path:filename>')
def pattern_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/get_image_colors', methods=['POST'])
def get_image_colors():
    data = request.json
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], data['pattern_folder'], data['image_name'])
    if not os.path.exists(image_path):
        return jsonify({'error': 'Image not found'}), 404
    main_colors = find_main_colors(image_path, num_colors=2)
    snapped_colors = snap_to_allowed_colors(main_colors)
    return jsonify({'colors': snapped_colors})

@app.route('/save_colors', methods=['POST'])
def save_colors():
    try:
        data = request.json
        app.logger.info(f"Received data: {data}")  # Log received data
        
        pattern_folder = data['pattern_folder']
        file_name = data['file_name']
        colors = data['colors']
        
        color_data = {
            "file_name": file_name,
            "primary_color": colors[0],
            "secondary_color": colors[1],
            "crop": "",
            "feature_image": ""
        }
        
        # Ensure the UPLOAD_FOLDER exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Load existing results
        results_file = app.config['RESULTS_FILE']
        if os.path.exists(results_file):
            try:
                with open(results_file, 'r') as f:
                    results = json.load(f)
            except json.JSONDecodeError:
                app.logger.error(f"Error decoding JSON from {results_file}. Creating new results.")
                results = {}
        else:
            results = {}
        
        # Update results
        if pattern_folder not in results:
            results[pattern_folder] = {}
        results[pattern_folder][file_name] = color_data
        
        # Save updated results
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        app.logger.info("Colors saved successfully")
        return jsonify({'message': 'Colors saved successfully'}), 200
    except Exception as e:
        app.logger.error(f"Error in save_colors: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/download_results')
def download_results():
    if os.path.exists(app.config['RESULTS_FILE']):
        return send_file(app.config['RESULTS_FILE'], as_attachment=True, download_name='color_confirmation_results.json')
    else:
        return jsonify({'error': 'No results found'}), 404

@app.route('/delete_results', methods=['POST'])
def delete_results():
    try:
        if os.path.exists(app.config['RESULTS_FILE']):
            os.remove(app.config['RESULTS_FILE'])
            return jsonify({'message': 'Results deleted successfully'}), 200
        else:
            return jsonify({'message': 'No results file found'}), 404
    except Exception as e:
        app.logger.error(f"Error deleting results: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)