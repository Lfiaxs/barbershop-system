from app import db


class Agendamento(db.Model):
    __tablename__ = "agendamentos"
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(
        db.Integer,
        db.ForeignKey("clientes.id"),
        nullable=False
    )
    servico_id = db.Column(
        db.Integer,
        db.ForeignKey("servicos.id"),
        nullable=False
    )
    data = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    status = db.Column(
        db.String(20),
        default="agendado"
    )
    observacoes = db.Column(db.Text)

    cliente = db.relationship("Cliente")
    servico = db.relationship("Servico")