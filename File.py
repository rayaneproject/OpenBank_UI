from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bank.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modèle Utilisateur
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    balance = db.Column(db.Float, default=0.0)

# Modèle Transaction
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(10), nullable=False)  # deposit ou withdraw

# Création des tables
with app.app_context():
    db.create_all()

# Route pour créer un compte
@app.route('/create_account', methods=['POST'])
def create_account():
    data = request.json
    new_user = User(name=data['name'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Compte créé avec succès", "user_id": new_user.id})

# Route pour consulter le solde
@app.route('/balance/<int:user_id>', methods=['GET'])
def check_balance(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Utilisateur non trouvé"}), 404
    return jsonify({"name": user.name, "balance": user.balance})

# Route pour dépôt
@app.route('/deposit', methods=['POST'])
def deposit():
    data = request.json
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({"error": "Utilisateur non trouvé"}), 404
    
    user.balance += data['amount']
    transaction = Transaction(user_id=user.id, amount=data['amount'], type='deposit')
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({"message": "Dépôt réussi", "new_balance": user.balance})

# Route pour retrait
@app.route('/withdraw', methods=['POST'])
def withdraw():
    data = request.json
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({"error": "Utilisateur non trouvé"}), 404

    if user.balance < data['amount']:
        return jsonify({"error": "Fonds insuffisants"}), 400
    
    user.balance -= data['amount']
    transaction = Transaction(user_id=user.id, amount=data['amount'], type='withdraw')
    db.session.add(transaction)
    db.session.commit()

    return jsonify({"message": "Retrait réussi", "new_balance": user.balance})

# Lancer l'application
if __name__ == '__main__':
    app.run(debug=True)
