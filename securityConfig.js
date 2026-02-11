const express = require('express');
const session = require('express-session');
const csrf = require('csurf');  // Middleware pour la protection CSRF
const app = express();

// Middleware pour gérer les sessions utilisateur
app.use(session({
  secret: 'secret-key',  // Utilise une clé secrète unique et aléatoire pour ta session
  resave: false,
  saveUninitialized: true,
  cookie: {
    httpOnly: true,   // Empêche l'accès au cookie via JavaScript
    secure: process.env.NODE_ENV === 'production', // Active "secure" uniquement en prod (HTTPS)
    sameSite: 'Strict',  // Empêche l'envoi des cookies en dehors du même site
    maxAge: 3600000 // Durée d'expiration de la session (1 heure)
  }
}));

// Middleware pour gérer les jetons CSRF
const csrfProtection = csrf();
app.use(csrfProtection);

// Middleware pour parser les données POST (si tu utilises des formulaires)
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// Ajout des headers de sécurité
app.use((req, res, next) => {
  // Content Security Policy
  res.setHeader('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';");

  // X-Frame-Options (protection contre le clickjacking)
  res.setHeader('X-Frame-Options', 'DENY');
  
  // X-Content-Type-Options (empêche MIME sniffing)
  res.setHeader('X-Content-Type-Options', 'nosniff');

  // Strict-Transport-Security (forcé sur HTTPS en production)
  res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');

  // Cache-Control (empêche la mise en cache des pages sensibles)
  res.setHeader('Cache-Control', 'no-store');
  
  next();
});

// Route principale pour afficher les produits (index.html)
app.get('/produits', (req, res) => {
  // Exemple de produits, à remplacer par des données réelles
  const products = [
    { id: 1, name: 'Produit A', price: 20 },
    { id: 2, name: 'Produit B', price: 35 }
  ];

  // Envoie les produits et le jeton CSRF à la vue (ici, avec EJS comme moteur de templates)
  res.render('index', { products: products, csrfToken: req.csrfToken() });
});

// Route pour afficher le panier (panier.html)
app.get('/panier', (req, res) => {
  // Exemple de panier
  const products = [
    { name: 'Produit A', price: 20 },
    { name: 'Produit B', price: 35 }
  ];
  const total = products.reduce((sum, product) => sum + product.price, 0);

  res.render('panier', { products: products, total: total, csrfToken: req.csrfToken() });
});

// Route POST pour commander
app.post('/commander', (req, res) => {
  // Logique pour traiter la commande
  res.send('Commande reçue !');
});

// Route POST pour ajouter un produit au panier (on suppose qu'une logique pour gérer ça est ajoutée)
app.post('/add_to_cart/:id', (req, res) => {
  // Logique pour ajouter un produit au panier (en fonction de l'ID du produit)
  res.redirect('/panier');
});

// Lancer le serveur sur un port
const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Serveur lancé sur le port ${port}`);
});
