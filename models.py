from db import db
from datetime import datetime


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.Text, nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    data = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    usuario = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "mensagem": self.mensagem,
            "data": self.data.isoformat(),
            "usuario": self.usuario
        }