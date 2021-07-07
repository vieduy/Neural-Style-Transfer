import os, glob
from flask import Flask, request, redirect, render_template, flash
from werkzeug.utils import secure_filename
from PaddleGAN.ppgan.utils.config import get_config
from PaddleGAN.tools.main import main as Model
import numpy as np

UPLOAD_FOLDER = 'static/uploads/'
DOWNLOAD_FOLDER = 'static/downloads/'
ALLOWED_EXTENSIONS = {'jpg', 'png', '.jpeg'}
app = Flask(__name__, static_url_path="/static")

# APP CONFIGURATIONS
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 300
app.config['SECRET_KEY'] = 'opencv'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
# limit upload size upto 6mb
app.config['MAX_CONTENT_LENGTH'] = 6 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# No caching at all for API endpoints.
@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file attached in request')
            return redirect(request.url)
        file = request.files['file']
        model = request.form.get('comp_select')
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            ul = glob.glob('./static/uploads/*')
            for f in ul:
                os.remove(f)
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            process_file(os.path.join(UPLOAD_FOLDER, filename), filename, model)
            data = {
                'selected': model,
                "content_img": os.path.join(UPLOAD_FOLDER, filename),
                "processed_img": 'static/downloads/visual_test/' + filename.split('.')[0] + '_stylized.png'
            }
            return render_template("index.html", data=data)
    return render_template('index.html', data={'selected': None})


def process_file(path, filename, model):
    args = {
        'config_file': 'PaddleGAN/configs/lapstyle_rev_second.yaml',
        'evaluate_only': True,
        'load': 'PaddleGAN/lapstyle_circuit.pdparams',
        'model_path': None,
        'no_cuda': False,
        'opt': None,
        'reference_dir': '',
        'resume': None,
        'source_path': '',
        'style': 'PaddleGAN/data/images/circuit.jpg',
        'val_interval': 1
    }
    cfg = get_config(args['config_file'], args['opt'])
    if model == 'One':
        args['style'] = 'PaddleGAN/data/images/stars.png'
        args['load'] = 'PaddleGAN/lapstyle_stars.pdparams'

    elif model == 'Two':
        args['style'] = 'PaddleGAN/data/images/ocean.png'
        args['load'] = 'PaddleGAN/lapstyle_ocean.pdparams'

    elif model == 'Three':
        args['style'] = 'PaddleGAN/data/images/starry_night.jpg'
        args['load'] = 'PaddleGAN/lapstyle_starrynew.pdparams'

    else:
        args['style'] = 'PaddleGAN/data/images/circuit.jpg'
        args['load'] = 'PaddleGAN/lapstyle_circuit.pdparams'

    Model(args, cfg)


if __name__ == '__main__':
    app.run()
