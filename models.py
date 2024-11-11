# models.py
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Motorista(db.Model):
    __tablename__ = 'motoristas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    horas_normais = db.Column(db.Float, default=0)
    horas_extras = db.Column(db.Float, default=0) 

class Escala(db.Model):
    __tablename__ = 'escalas'
    id = db.Column(db.Integer, primary_key=True)
    motorista_id = db.Column(db.Integer, db.ForeignKey('motoristas.id'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fim = db.Column(db.Time, nullable=False)
    motorista = db.relationship('Motorista', backref=db.backref('escalas', lazy=True))

class Evento(db.Model):
    __tablename__ = 'eventos'
    id = db.Column(db.Integer, primary_key=True)
    escala_id = db.Column(db.Integer, db.ForeignKey('escalas.id'), nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    horario = db.Column(db.DateTime, nullable=False)
    escala = db.relationship('Escala', backref=db.backref('eventos', lazy=True))
