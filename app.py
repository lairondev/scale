from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
from models import db, Motorista, Escala, Evento

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gerencia_escala.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'sua_chave_secreta_aqui'  # Necessária para usar flash messages
db.init_app(app)

# Função para criar tabelas
def criar_tabelas():
    with app.app_context():
        db.create_all()

#Função formatar horas em mmodo amigável        
def formatar_horas_minutos(horas_decimais):
    horas = int(horas_decimais)  # Parte inteira das horas
    minutos = int((horas_decimais - horas) * 60)  # Parte decimal em minutos
    return f"{horas}h{minutos:02d}min"  # Formatação com zero à esquerda para minutos



@app.route('/')
def index():
    escalas = Escala.query.all()
    return render_template('index.html', escalas=escalas)
    
@app.route('/escala/<int:escala_id>/eventos', methods=['GET', 'POST'])
def gerenciar_eventos(escala_id):
    escala = Escala.query.get_or_404(escala_id)
    if request.method == 'POST':
        descricao = request.form['descricao']
        horario_str = request.form['horario'].replace('T', ' ')
        
        try:
            horario = datetime.strptime(horario_str, '%Y-%m-%d %H:%M')
            novo_evento = Evento(descricao=descricao, horario=horario, escala_id=escala.id)
            db.session.add(novo_evento)
            db.session.commit()
            return redirect(url_for('gerenciar_eventos', escala_id=escala.id))
        except ValueError:
            flash("Formato de data/hora inválido. Por favor, use o formato correto.")
            return redirect(url_for('gerenciar_eventos', escala_id=escala.id))

    eventos = Evento.query.filter_by(escala_id=escala.id).all()
    return render_template('gerenciar_eventos.html', escala=escala, eventos=eventos)



@app.route('/criar_escala', methods=['GET', 'POST'])
def criar_escala():
    motoristas = Motorista.query.all()
    if request.method == 'POST':
        motorista_id = request.form['motorista_id']
        data_str = request.form['data']
        data = datetime.strptime(data_str, '%Y-%m-%d').date()
        hora_inicio_str = request.form['hora_inicio']
        hora_fim_str = request.form['hora_fim']
        
        hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
        hora_fim = datetime.strptime(hora_fim_str, '%H:%M').time()

        # Convertendo para datetime para facilitar cálculos
        inicio = datetime.combine(data, hora_inicio)
        fim = datetime.combine(data, hora_fim)

        # Horas limites para cálculo
        inicio_jornada = datetime.combine(data, datetime.strptime("08:00", "%H:%M").time())
        fim_jornada = datetime.combine(data, datetime.strptime("17:00", "%H:%M").time())

        # Cálculo das horas normais e extras
        horas_normais = min(fim, fim_jornada) - max(inicio, inicio_jornada)
        horas_extras = max(fim - fim_jornada, timedelta(0))

        # Convertendo para horas
        horas_normais = horas_normais.total_seconds() / 3600 if horas_normais > timedelta(0) else 0
        horas_extras = horas_extras.total_seconds() / 3600 if horas_extras > timedelta(0) else 0

        # Criando a escala
        nova_escala = Escala(
            motorista_id=motorista_id,
            data=data,
            hora_inicio=hora_inicio,
            hora_fim=hora_fim
        )

        # Atualizando as horas do motorista
        motorista = Motorista.query.get(motorista_id)
        motorista.horas_normais += horas_normais
        motorista.horas_extras += horas_extras

        db.session.add(nova_escala)
        db.session.commit()
        
        return redirect(url_for('index'))
    
    return render_template('criar_escala.html', motoristas=motoristas)


@app.route('/balanco_mensal')
def balanco_mensal():
    motoristas = Motorista.query.all()
    
    # Calcula o banco de horas em formato legível para cada motorista
    for motorista in motoristas:
        motorista.horas_normais_formatado = formatar_horas_minutos(motorista.horas_normais)
        motorista.horas_extras_formatado = formatar_horas_minutos(motorista.horas_extras)
    
    return render_template('balanco_mensal.html', motoristas=motoristas)



@app.route('/adicionar_motorista', methods=['POST'])
def adicionar_motorista():
    nome = request.form['nome']
    novo_motorista = Motorista(nome=nome)
    db.session.add(novo_motorista)
    db.session.commit()
    return redirect(url_for('criar_escala'))

if __name__ == '__main__':
    criar_tabelas()
    app.run(debug=True)
