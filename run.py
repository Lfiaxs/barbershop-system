from app import app, db
from app.models import Usuario
from werkzeug.security import generate_password_hash

with app.app_context():

    db.create_all()

    admin = Usuario.query.filter_by(
        email="admin@barbeariafiais.com"
    ).first()

    if not admin:
        admin = Usuario(
            nome="Lucas",
            email="admin@barbeariafiais.com",
            senha=generate_password_hash("123456"),
            tipo="admin"
        )
        db.session.add(admin)
        db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)