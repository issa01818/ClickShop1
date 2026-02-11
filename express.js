const express = require('express');
const app = express();
const path = require('path');
const session = require('express-session');

// Importer la configuration de sécurité
const securityConfig = require('./securityConfig'); // Importer les configurations de sécurité

// Configurer la sécurité pour l'ensemble de l'application
securityConfig(app);

// Middleware pour parser les données POST (si tu utilises des formulaires)
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// Configurer le moteur de template (si tu utilises EJS par exemple)
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Exemple de produits, à remplacer par des données réelles
const products = [
  { id: 1, name: 'Produit A', price: 20 },
  { id: 2, name: 'Produit B', price: 35 },
];

// Route principale pour afficher les produits (index.html)
app.get('/produits', (req, res) => {
  res.render('index', { products: products, csrfToken: req.csrfToken() });
});

// Route pour afficher le panier (panier.html)
app.get('/panier', (req, res) => {
  const total = products.reduce((sum, product) => sum + product.price, 0);
  res.render('panier', { products: products, total: total, csrfToken: req.csrfToken() });
});

// Route POST pour commander
app.post('/commander', (req, res) => {
  // Logique pour traiter la commande
  res.send('Commande reçue !');
});

// Route POST pour ajouter un produit au panier
app.post('/add_to_cart/:id', (req, res) => {
  // Logique pour ajouter un produit au panier (en fonction de l'ID du produit)
  res.redirect('/panier');
});

// Lancer le serveur sur un port
const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Serveur lancé sur le port ${port}`);
});

