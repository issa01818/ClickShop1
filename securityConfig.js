const csrf = require('csurf');
const session = require('express-session');

const securityConfig = (app) => {
  // Middleware pour gérer les sessions utilisateur
  app.use(session({
    secret: 'secret-key',  // Utiliser une clé secrète unique
    resave: false,
    saveUninitialized: true,
    cookie: {
      httpOnly: true,  // Empêche l'accès au cookie via JavaScript
      secure: process.env.NODE_ENV === 'production',  // Active "secure" uniquement en prod (HTTPS)
      sameSite: 'Strict',  // Empêche l'envoi des cookies en dehors du même site
      maxAge: 3600000  // Durée d'expiration de la session (1 heure)
    }
  }));

  // Middleware pour gérer les jetons CSRF
  const csrfProtection = csrf();
  app.use(csrfProtection);

  // Middleware pour ajouter les headers de sécurité
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
};

module.exports = securityConfig;

