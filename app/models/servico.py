from app import db


class Servico(db.Model):
    __tablename__ = "servicos"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    duracao = db.Column(db.Integer, nullable=False)
    descricao = db.Column(db.Text)