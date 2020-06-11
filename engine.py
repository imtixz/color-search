from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from algorithm import get_image, get_colors
import numpy as np
from skimage.color import rgb2lab, deltaE_cie76
import os

app = Flask(__name__)

app.config['IMAGE_UPLOADS'] = './static/uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)


class Images(db.Model):
    url = db.Column(db.String(1024), primary_key=True)
    regular = db.Column(db.String(1024))
    raw = db.Column(db.String(1024))
    meta = db.Column(db.String(1024))
    diff = 0

    dominantColor = db.relationship('Colors', backref='image', lazy=True)

    def getDifference(self, uploaded_color):
        color = self.dominantColor[0]
        color.getLab()
        print("color dot lab")
        print(color.lab)
        print("uploaded color")
        print(uploaded_color)

        # this entire function has to go into algorithm file
        self.diff = deltaE_cie76(color.lab, uploaded_color)


class Colors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    red = db.Column(db.Float)
    green = db.Column(db.Float)
    blue = db.Column(db.Float)
    image_url = db.Column(db.String(1024), db.ForeignKey(
        'images.url'), nullable=False)

    def getLab(self):
        newArray = [np.array([self.red, self.green, self.blue])]
        self.lab = rgb2lab(np.uint8(np.asarray([[newArray]])))


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if request.files:
            image = request.files['image']
            filePath = os.path.join(
                app.config["IMAGE_UPLOADS"], image.filename)
            image.save(filePath)
            return redirect('/r/'+image.filename)

    return render_template('index.html')


@app.route('/r/<imageName>')
def result(imageName):
    filePath = os.path.join(app.config["IMAGE_UPLOADS"], imageName)
    colorArray = get_colors(get_image(filePath), 1)
    colorArray = rgb2lab(np.uint8(np.asarray([[colorArray]])))

    all_images = list(Images.query.all())
    for img in all_images:
        img.getDifference(colorArray)
    all_images.sort(key=lambda x: x.diff, reverse=False)
    all_images = all_images[:100]

    urls_list = []
    raw_list = []
    meta_list = []
    for img in all_images:
        urls_list.append(img.url)
        raw_list.append(img.raw)
        meta_list.append(img.meta)

    os.remove(filePath)

    return render_template('result.html', urls=urls_list, raws=raw_list, zip=zip)


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=5000)
