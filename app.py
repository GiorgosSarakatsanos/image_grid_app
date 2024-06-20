import os
from flask import Flask, render_template, request, jsonify, url_for
from PIL import Image
from reportlab.lib.pagesizes import A4, A3, landscape
from reportlab.pdfgen import canvas
from io import BytesIO

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

paper_sizes = {
    'C3': (458, 324),
    'A3': A3,
    'A4': A4
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename != '':
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            paper_type = request.form.get('paper_type', 'A4')
            user_width = int(request.form.get('user_width', 500))
            user_height = int(request.form.get('user_height', 1000))
            image_size = request.form.get('image_size', '85x55')
            
            # Determine paper dimensions
            if paper_type in paper_sizes:
                if paper_type == 'A3':
                    paper_width, paper_height = landscape(A3)
                elif paper_type == 'A4':
                    paper_width, paper_height = A4
                else:
                    paper_width, paper_height = paper_sizes[paper_type]
            else:
                paper_width = min(user_width, 500)
                paper_height = min(user_height, 1000)

            # Margins
            top_margin = bottom_margin = 15
            left_margin = 37
            right_margin = 17

            available_height = paper_height - top_margin - bottom_margin
            available_width = paper_width - left_margin - right_margin

            # Determine image dimensions based on selected size
            if image_size == '85x55':
                img_width_mm, img_height_mm = 85, 55
            elif image_size == '120x95':
                img_width_mm, img_height_mm = 120, 95
            else:
                img_width_mm = float(request.form.get('custom_img_width'))
                img_height_mm = float(request.form.get('custom_img_height'))

            # Calculate how many images fit in the available space
            columns = int(available_width // img_width_mm)
            rows = int(available_height // img_height_mm)

            # Create a PDF with the grid
            pdf_buffer = BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=(paper_width, paper_height))

            for row in range(rows):
                for col in range(columns):
                    x = left_margin + col * img_width_mm
                    y = paper_height - top_margin - (row + 1) * img_height_mm
                    c.drawImage(filepath, x, y, width=img_width_mm, height=img_height_mm)

            c.save()
            pdf_buffer.seek(0)

            pdf_filename = "grid.pdf"
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
            with open(pdf_path, "wb") as f:
                f.write(pdf_buffer.read())

            return jsonify({
                'pdf_url': url_for('static', filename='uploads/' + pdf_filename)
            })
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
