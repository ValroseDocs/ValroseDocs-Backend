from ValroseDocs import app
import flask_monitoringdashboard as dashboard

if __name__ == "__main__":
    dashboard.bind(app)
    app.run()