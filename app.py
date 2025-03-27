#FINALMENTE V1

from flask import Flask, render_template, redirect
from normativa import normativa_bp


app = Flask(__name__)
app.register_blueprint(normativa_bp, url_prefix="/normativa")  # monta el blueprint

@app.route('/')
def index():
    return render_template('index.html')

#if __name__ == '__main__':
#    app.run(debug=True)
