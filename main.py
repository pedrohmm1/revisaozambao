from flask import Flask, request, jsonify
from db import db
from models import Post
import redis
import json
import os
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "postgresql://appuser:apppass@localhost:5432/posts"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True
)

USER_API_URL = os.getenv("USER_API_URL", "http://127.0.0.1:5001/users")


def send_event(event_type, description):
    event = {
        "id": None,
        "type": event_type,
        "description": description,
        "source": "POSTS_API",
        "date": None
    }

    redis_client.rpush("events-queue", json.dumps(event))


def user_exists(user_id):
    try:
        with urlopen(f"{USER_API_URL}/{user_id}") as response:
            return response.status == 200
    except HTTPError:
        return False
    except URLError:
        return False


with app.app_context():
    db.create_all()


@app.route("/post", methods=["GET"])
def list_posts():
    posts = Post.query.all()

    send_event("LIST_POST", "List all posts")

    return jsonify([post.to_dict() for post in posts]), 200


@app.route("/post", methods=["POST"])
def create_post():
    user_id = request.headers.get("usuario")

    if not user_id:
        return jsonify({"erro": "Header 'usuario' é obrigatório"}), 400

    if not user_exists(user_id):
        return jsonify({"erro": "Usuário não existe"}), 400

    data = request.json

    if not data:
        return jsonify({"erro": "Body é obrigatório"}), 400

    if "titulo" not in data:
        return jsonify({"erro": "Campo 'titulo' é obrigatório"}), 400

    if "mensagem" not in data:
        return jsonify({"erro": "Campo 'mensagem' é obrigatório"}), 400

    post = Post(
        titulo=data["titulo"],
        mensagem=data["mensagem"],
        usuario=user_id
    )

    db.session.add(post)
    db.session.commit()

    send_event("CREATE_POST", f"Post {post.id} created by user {user_id}")

    return jsonify(post.to_dict()), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5002)