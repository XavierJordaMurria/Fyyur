from models.database import db

class Genere(db.Model):
    __tablename__ = 'Genere'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)