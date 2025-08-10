from flask import Flask
from routes import main_bp # Import the blueprint from your routes file

# Create the main Flask application instance
app = Flask(__name__)

# Register the blueprint. This connects all the routes from routes.py to your app.
app.register_blueprint(main_bp)

if __name__ == "__main__":
    app.run(debug=True)
