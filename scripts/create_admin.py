from app import app, db
from app.models import Usuario
from werkzeug.security import generate_password_hash

with app.app_context():

    db.create_all()

    admin = Usuario.query.filter_by(
        email="admin@barbeariafiais.com"
    ).first()

    if admin:
        admin.nome = "Lucas"
        admin.senha = generate_password_hash("123456")
        admin.tipo = "admin"
        db.session.commit()
        print("Administrador atualizado com sucesso!")
    else:
        admin = Usuario(
            nome="Lucas",
            email="admin@barbeariafiais.com",
            senha=generate_password_hash("123456"),
            tipo="admin"
        )

        db.session.add(admin)
        db.session.commit()

        print("Administrador criado com sucesso!")