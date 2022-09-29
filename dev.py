from ValroseDocs import app
import os

os.environ['FLASK_ENV'] = 'development'

if __name__ == "__main__":
    app.testing = True
    app.run(debug=True)