import sys
from flask import Flask
from flask import jsonify
from flask_cors import CORS, cross_origin
import time

app = Flask(__name__, static_folder='.', static_url_path='')
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/')
def home():
    return app.send_static_file('Front-end/EnterpriseUser/index.html')
@app.route('/<mypage>')
def userpage(mypage):
    return app.send_static_file('Front-end/EnterpriseUser/index.html')
@app.route('/redactor')
def redactor():
    return app.send_static_file('Front-end/EnterpriseAuthor/index.html')
@app.route('/api/test', methods=['GET', 'OPTIONS'])
@cross_origin()
def test():
    jesus = "Congratulations, api is work @facexem_api. Time is ("+time.ctime(time.time())+')'
    return jsonify(jesus)

app.run(port=9999, debug=True)