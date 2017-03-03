from flask import Flask, jsonify
from .extensions import db
from .user.views import user
from flask_cors import CORS

app = Flask('Facexem', instance_relative_config=True)
app.register_blueprint(user)
app.config.from_object('config')
db.app = app
db.init_app(app)
CORS(app)

@app.errorhandler(404)
def page_not_found(error):
        return jsonify('Not found'), 404

@app.errorhandler(500)
def server_error_page(error):
        return jsonify('Server error'), 500
