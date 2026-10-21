"""
MILA Cafe - Main Flask Application
Organized with Blueprints for modular route management
"""
from flask import Flask
import os
from dotenv import load_dotenv
from backend.routes import register_blueprints

# Load environment variables from .env
load_dotenv()

# Get the parent directory (mila_cafe root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'frontend')
STATIC_DIR = os.path.join(BASE_DIR, 'frontend')

# Initialize Flask app
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

# Load Flask secret key from environment variables
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Register all blueprints
register_blueprints(app)


if __name__ == "__main__":
    app.run(debug=True)
