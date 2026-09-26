import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from extensions import db
from models import Task

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("/var/log/taskmanager/app.log")
    ]
)
logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}"
        f"@{os.environ['DB_HOST']}:{os.environ.get('DB_PORT', 5432)}"
        f"/{os.environ['DB_NAME']}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    CORS(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()
        logger.info("Database tables verified/created.")

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"}), 200

    @app.route("/tasks", methods=["GET"])
    def get_tasks():
        tasks = Task.query.order_by(Task.created_at.desc()).all()
        logger.info(f"Fetched {len(tasks)} tasks.")
        return jsonify([t.to_dict() for t in tasks]), 200

    @app.route("/tasks/<int:task_id>", methods=["GET"])
    def get_task(task_id):
        task = Task.query.get_or_404(task_id)
        return jsonify(task.to_dict()), 200

    @app.route("/tasks", methods=["POST"])
    def create_task():
        data = request.get_json()
        if not data or not data.get("title"):
            return jsonify({"error": "title is required"}), 400
        task = Task(
            title=data["title"],
            description=data.get("description", ""),
            status=data.get("status", "pending")
        )
        db.session.add(task)
        db.session.commit()
        logger.info(f"Created task id={task.id} title='{task.title}'")
        return jsonify(task.to_dict()), 201

    @app.route("/tasks/<int:task_id>", methods=["PUT"])
    def update_task(task_id):
        task = Task.query.get_or_404(task_id)
        data = request.get_json()
        if "title" in data:
            task.title = data["title"]
        if "description" in data:
            task.description = data["description"]
        if "status" in data:
            task.status = data["status"]
        db.session.commit()
        logger.info(f"Updated task id={task.id}")
        return jsonify(task.to_dict()), 200

    @app.route("/tasks/<int:task_id>", methods=["DELETE"])
    def delete_task(task_id):
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        logger.info(f"Deleted task id={task_id}")
        return jsonify({"message": "Task deleted"}), 200

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(
        host="0.0.0.0",
        port=int(os.environ.get("FLASK_PORT", 5000))
    )
