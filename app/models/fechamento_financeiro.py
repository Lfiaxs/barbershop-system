from app import db
from datetime import date

class FechamentoFinanceiro(db.Model):
    __tablename__ = "fechamentos_financeiros"

    id = db.Column(db.Integer, primary_key=True)
    mes = db.Column(db.Integer, nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    receita = db.Column(db.Float, nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    ticket_medio = db.Column(db.Float, nullable=False)
    data_fechamento = db.Column(
        db.Date,
        default=date.today
    )