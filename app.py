import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

# Chargement de la clé secrète depuis le fichier .env
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")  # Utiliser la clé secrète du fichier .env

# Fonction pour initialiser la base de données et ajouter les tables 'users', 'products' et 'orders' si elles n'existent pas
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Créer la table 'users' si elle n'existe pas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    ''')

    # Créer la table 'products' si elle n'existe pas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,         description TEXT
    )
    ''')

    # Créer la table 'orders' si elle n'existe pas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        total_price REAL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    ''')

    conn.commit()
    conn.close()

# Initialiser la base de données à chaque démarrage de l'application
init_db()

# Fonction pour se connecter à la base de données
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row  # Cela permet de récupérer les résultats sous forme de dictionnaires
    return conn

# Route pour la page d'accueil
@app.route("/")
def home():
    return render_template("index.html")

# Route pour l'inscription des utilisateurs
@app.route("/inscription", methods=["GET", "POST"])
def inscription():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)  # Hash du mot de passe

        conn = get_db_connection()
        cursor = conn.cursor()

        # Vérifier si l'email existe déjà
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if user:
            return "Email déjà utilisé !"

        # Insérer le nouvel utilisateur dans la base de données
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                       (username, email, hashed_password))
        conn.commit()
        conn.close()

        return redirect(url_for("connexion"))

    return render_template("inscription.html")

# Route pour la connexion des utilisateurs
@app.route("/connexion", methods=["GET", "POST"])
def connexion():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        conn = get_db_connection()
        cursor = conn.cursor()

        # Chercher l'utilisateur dans la base de données
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            conn.close()
            return redirect(url_for("home"))
        else:
            conn.close()
            return "Email ou mot de passe incorrect"

    return render_template("connexion.html")

# Route pour afficher les produits
@app.route("/produits")
def produits():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Récupérer tous les produits
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    conn.close()

    return render_template("produits.html", products=products)

# Ajouter des produits de test à la base de données
def add_test_products():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Vérifier si des produits existent déjà
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:  # Si aucun produit, on en ajoute
        products = [
            ('Télévision', 299.99, 'Télévision LED 4K 55 pouces'),
            ('Téléphone', 599.99, 'Smartphone dernier modèle'),
            ('Ordinateur', 899.99, 'Ordinateur portable 16Go RAM'),
        ]
        cursor.executemany("INSERT INTO products (name, price, description) VALUES (?, ?, ?)", products)
        conn.commit()

    conn.close()

# Ajouter des produits de test à la base de données
add_test_products()

# Route pour ajouter un produit au panier
@app.route("/ajouter_panier", methods=["POST"])
def ajouter_panier():
    if "cart" not in session:
        session["cart"] = []

    product_id = int(request.form["product_id"])  # Convertir en entier pour correspondre à la base de données
    session["cart"].append(product_id)
    
    return redirect(url_for("produits"))

# Route pour afficher le panier
@app.route("/panier")
def panier():
    if "cart" not in session or len(session["cart"]) == 0:
        return render_template("panier_vide.html")  # Page quand le panier est vide

    # Récupérer les produits du panier depuis la session
    cart_ids = session["cart"]
    conn = get_db_connection()
    cursor = conn.cursor()

    if cart_ids:  # Vérifier que le panier n'est pas vide
        # Crée une chaîne de placeholders dynamiques
        placeholders = ', '.join(['?'] * len(cart_ids))

        # Utilisation sécurisée de la requête avec des placeholders paramétrés
        query = "SELECT * FROM products WHERE id IN ({})".format(placeholders)
        cursor.execute(query, tuple(cart_ids))  # Passer cart_ids comme tuple
        products_in_cart = cursor.fetchall()
    else:
        products_in_cart = []

    # Calculer le total
    total = sum(product['price'] for product in products_in_cart)

    conn.close()

    return render_template("panier.html", products=products_in_cart, total=total)

# Route pour passer une commande
@app.route("/commander", methods=["POST"])
def commander():
    if "user_id" not in session:
        return redirect(url_for("connexion"))

    user_id = session["user_id"]
    cart = session.get("cart", [])
    total_price = 0
    conn = get_db_connection()
    cursor = conn.cursor()

    # Ajouter les produits du panier à la table 'orders'
    for product_id in cart:
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()

        if product:
            quantity = 1  # Nombre de produits (simplification)
            total_price += product['price']

            cursor.execute("INSERT INTO orders (user_id, product_id, quantity, total_price) VALUES (?, ?, ?, ?)",
                           (user_id, product_id, quantity, product['price']))

    conn.commit()
    conn.close()

    # Vider le panier après la commande
    session.pop("cart", None)

    return render_template("commande_confirmation.html")

# Route pour voir la confirmation de commande
@app.route("/commande_confirmation")
def commande_confirmation():
    return render_template("commande_confirmation.html")

if __name__ == "__main__":
    # Port dynamique pour Render
    port = int(os.environ.get("PORT", 5000))  # Défaut à 5000 si PORT n'est pas défini
    app.run(debug=False, host='0.0.0.0', port=port)

