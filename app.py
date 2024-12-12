from flask import Flask, render_template, request, send_file, jsonify
import os
import sys
import webbrowser
from threading import Timer
from werkzeug.utils import secure_filename

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

app = Flask(__name__)
# 移除文件大小限制
app.config['MAX_CONTENT_LENGTH'] = None
# 文件保存路径
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.expanduser('~'), 'WebShare_Files')

# 确保上传目录存在
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def open_browser():
    webbrowser.open('http://127.0.0.1:5000/')

@app.route('/')
def index():
    files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        size = os.path.getsize(filepath)
        # 转换文件大小为人类可读格式
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024*1024:
            size_str = f"{size/1024:.1f} KB"
        elif size < 1024*1024*1024:
            size_str = f"{size/(1024*1024):.1f} MB"
        else:
            size_str = f"{size/(1024*1024*1024):.1f} GB"
        
        files.append({
            'name': filename,
            'size': size_str
        })
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # 如果文件已存在，添加数字后缀
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(filepath):
                filename = f"{base}_{counter}{ext}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                counter += 1
            
            file.save(filepath)
            return jsonify({'success': True, 'message': '文件上传成功'})
        return jsonify({'success': False, 'message': '没有选择文件'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'上传失败: {str(e)}'})

@app.route('/upload-chunk', methods=['POST'])
def upload_chunk():
    try:
        chunk = request.files['chunk']
        filename = request.form['filename']
        chunk_number = int(request.form['chunkNumber'])
        total_chunks = int(request.form['totalChunks'])
        
        temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'temp')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            
        # 保存分片
        chunk_path = os.path.join(temp_dir, f"{filename}.part{chunk_number}")
        chunk.save(chunk_path)
        
        # 检查是否所有分片都已上传
        if chunk_number == total_chunks - 1:
            # 合并文件
            final_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
            with open(final_path, 'wb') as final_file:
                for i in range(total_chunks):
                    chunk_path = os.path.join(temp_dir, f"{filename}.part{i}")
                    with open(chunk_path, 'rb') as chunk_file:
                        final_file.write(chunk_file.read())
                    os.remove(chunk_path)
            
            return jsonify({'success': True, 'message': '文件上传成功'})
        
        return jsonify({'success': True, 'message': '分片上传成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'分片上传失败: {str(e)}'})

@app.route('/download/<filename>')
def download(filename):
    try:
        return send_file(
            os.path.join(app.config['UPLOAD_FOLDER'], filename),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return f"下载失败: {str(e)}", 404

def main():
    Timer(1.5, open_browser).start()
    app.run(debug=False, host='127.0.0.1', port=5000)

if __name__ == '__main__':
    main()
