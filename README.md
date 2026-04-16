# Football-Dashboard

# ⚽ K-League Data Pipeline & Automation

---

## 📋 Étape 1 : Extraction des Données (Scraping)
Mise en place des scripts pour récupérer les données exhaustives des ligues (K League 1, 2, 3, 4).

* **Données Clubs :** Nom, logo, ligue, nombre de joueurs, statistiques (buts, data historiques).
* **Données Joueurs :** Extraction par club incluant le poste, le club actuel et l'historique complet des 5 dernières années.
* **Valeur marchande :** Récupération des données financières et performances.

## 🖥️ Étape 2 : Interface et Gestion du Cache
Développement de la logique de sélection et optimisation des requêtes.

* **Navigation :** Système de filtrage hiérarchique (Ligue ➔ Club ➔ Joueur).
* **Performance :** Mise en cache des données récupérées via les commandes pour éviter les appels API/Scraping inutiles.

## 🤖 Étape 3 : Automatisation (CI/CD)
Mise à jour automatique des fichiers de données.

* **Workflow YAML :** Configuration d'une **GitHub Action** pour exécuter le script une fois par semaine.
* **Export :** Mise à jour automatique d'un fichier Excel unique dans le dossier `/data` du projet.

## ⚙️ Étape 4 : Optimisation
Amélioration globale du système.

* **Code :** Refactorisation pour rendre le script plus rapide et plus robuste.
* **Application :** Optimisation de l'UX et de la gestion de la mémoire.

## 🌍 Étape 5 : Scalabilité
* **Expansion :** Déploiement du modèle sur d'autres championnats internationaux sur la même base technique.

---
