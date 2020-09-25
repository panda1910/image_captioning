import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from flask import send_from_directory
import time

UPLOAD_FOLDER = f'{os.getcwd()}/uploads'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/<name>')
def uploaded(name):
    cap = ""
    with open(f"uploads/caption.txt", "r") as f:
        cap += f.read()
    return render_template('index_after_upload.html', content=cap, img_name=name)

tot_files = 0
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    global tot_files

    fpath = UPLOAD_FOLDER+"image.jpg"
    if os.path.exists(fpath):
        os.remove(fpath)
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            # flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser
        # submit an empty part without filename
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            if tot_files >= 10:
                tot_files = 0
                ll = os.listdir(UPLOAD_FOLDER)
                for ele in ll:
                    os.remove(UPLOAD_FOLDER + "/" + ele)
            else:
                tot_files += 1

            filename = secure_filename(file.filename)
            with open(f"uploads/{filename}.txt", "w") as dummy:
                pass
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # return redirect(url_for('uploaded_file',filename=filename))
        
            os.system('python3 ./AI/image_captioning/sample.py --image' + '/home/ubuntu/Timathon/uploads/' + filename)
            count = 0
            while os.path.getsize(f"uploads/{filename}.txt") == 0:
                if count >= 60:
                    with open(f"uploads/{filename}.txt", "w") as dummy:
                        dummy.write("Could not generate the caption")
                    break
                time.sleep(0.5)
                count+=1

            return redirect(url_for('uploaded', name=filename))
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)
