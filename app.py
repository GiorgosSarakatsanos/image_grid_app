import os
from flask import Flask, render_template, request, jsonify, url_for
from PIL import Image
from reportlab.lib.pagesizes import A4, A3, landscape, portrait
from reportlab.pdfgen import canvas
from io import BytesIO

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Function to convert mm to points
def mm_to_points(mm):
    return mm * 2.83465  # 1 mm = 2.83465 points

paper_sizes = {
    'C3': (458, 324),
    'A3': (420, 297),
    'A4': (297, 210)
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
            
            # Determine paper dimensions and orientation
            if paper_type in paper_sizes:
                paper_width, paper_height = paper_sizes[paper_type]
                if paper_type == 'A4':
                    paper_width_pts, paper_height_pts = landscape((mm_to_points(paper_width), mm_to_points(paper_height)))
                    top_margin = bottom_margin = mm_to_points(15)
                    left_margin = mm_to_points(37)
                    right_margin = mm_to_points(17)
                else:
                    paper_width_pts, paper_height_pts = portrait((mm_to_points(paper_width), mm_to_points(paper_height)))
                    top_margin = mm_to_points(15)
                    bottom_margin = mm_to_points(15)
                    left_margin = mm_to_points(37)
                    right_margin = mm_to_points(17)
            else:
                paper_width_pts = min(mm_to_points(user_width), mm_to_points(500))
                paper_height_pts = min(mm_to_points(user_height), mm_to_points(1000))
                top_margin = mm_to_points(15)
                bottom_margin = mm_to_points(15)
                left_margin = mm_to_points(37)
                right_margin = mm_to_points(17)
            
            available_width_pts = paper_width_pts - left_margin - right_margin
            available_height_pts = paper_height_pts - top_margin - bottom_margin

            # Determine image dimensions based on selected size
            if image_size == '85x55':
                img_width_mm, img_height_mm = 85, 55
            elif image_size == '120x95':
                img_width_mm, img_height_mm = 120, 95
            else:
                img_width_mm = float(request.form.get('custom_img_width'))
                img_height_mm = float(request.form.get('custom_img_height'))

            # Convert image dimensions to points
            img_width_pts = mm_to_points(img_width_mm)
            img_height_pts = mm_to_points(img_height_mm)

            # Calculate how many images fit in the available space
            columns = int(available_width_pts // img_width_pts)
            rows = int(available_height_pts // img_height_pts)

            # Create a PDF with the grid
            pdf_buffer = BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=(paper_width_pts, paper_height_pts))

            for row in range(rows):
                for col in range(columns):
                    x = left_margin + col * img_width_pts
                    y = paper_height_pts - top_margin - (row + 1) * img_height_pts

                    # Open the image to check its dimensions
                    img = Image.open(filepath)
                    img_width, img_height = img.size

                    # Decide if image needs rotation (only for landscape orientation)
                    if paper_type == 'A3' and img_width > img_height:
                        c.saveState()
                        c.translate(x, y)
                        c.rotate(90)
                        c.drawImage(filepath, 0, -img_width_pts, width=img_width_pts, height=img_height_pts)
                        c.restoreState()
                    else:
                        c.drawImage(filepath, x, y, width=img_width_pts, height=img_height_pts)

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
