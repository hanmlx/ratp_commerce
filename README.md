# Tableau de bord des commerces de proximité agréés RATP

## Contexte du projet

Ce projet a été réalisé dans le cadre d'un travail pratique sur l'exploitation de données ouvertes. Il s'appuie sur les données des commerces de proximité agréés par la RATP en région parisienne, mises à disposition via la plateforme Open Data de la RATP.

## Objectifs

L'objectif principal de ce projet était de développer une application web interactive permettant d'explorer, visualiser et analyser la distribution des commerces de proximité dans le réseau RATP. Les objectifs secondaires incluent :
- Récupérer et traiter les données depuis une API REST
- Mettre en œuvre différentes techniques de visualisation de données
- Créer une interface utilisateur intuitive avec Streamlit
- Appliquer des techniques de filtrage et d'analyse statistique

## Source des données

Les données proviennent de l'API Open Data de la RATP :
- **URL de l'API** : https://data.ratp.fr
- **Jeu de données** : Commerces de proximité agréés RATP
- **Format** : JSON via API REST
- **Fréquence de mise à jour** : Données en temps réel
- **Limitations** : 100 enregistrements par requête (avec implémentation d'une pagination automatique)

## Méthodologie

### 1. Récupération des données
- Implémentation d'une fonction de récupération paginée pour contourner la limite de 100 enregistrements par requête
- Mise en cache des données pour une durée de 1 heure (TTL: 3600s) pour optimiser les performances
- Gestion des erreurs de connexion à l'API

### 2. Traitement et nettoyage des données
- Normalisation des noms de colonnes pour assurer la compatibilité
- Extraction et conversion des coordonnées géographiques
- Gestion des valeurs manquantes

### 3. Analyse statistique
- Analyses univariées : répartition des types de commerce
- Analyses bivariées : types de commerce par commune
- Calculs de métriques clés : nombre total de commerces, types de commerce, communes

### 4. Visualisations
- Graphiques en barres et camemberts pour la répartition des types de commerce
- Heatmap pour la densité des commerces par commune et type
- Cartes interactives pour la distribution géographique

## Fonctionnalités de l'application

L'application web développée avec Streamlit propose quatre sections principales :

### 1. Analyse statistique
- Aperçu des données avec métriques clés
- Répartition des types de commerce (graphiques en barres et camemberts)
- Types de commerce par commune (barres groupées et heatmap)

### 2. Distribution géographique
- Carte interactive montrant la localisation des commerces
- Filtrage par type de commerce et commune
- Visualisation de la densité des commerces

### 3. Détail des commerces
- Tableau détaillé avec informations sur chaque commerce
- Options de filtrage avancées
- Export des données filtrées

### 4. Données brutes
- Accès aux données brutes récupérées depuis l'API
- Informations sur le traitement appliqué

### Options de filtrage
- Par type de commerce (sélection multiple)
- Par commune (sélection multiple)
- Ces filtres s'appliquent dynamiquement à toutes les visualisations

## Architecture technique

### Technologies utilisées
- **Python** : langage de programmation principal
- **Streamlit** : framework pour la création d'applications web interactives
- **Pandas** : manipulation et analyse de données
- **Plotly Express** : création de visualisations interactives
- **Requests** : interaction avec l'API REST

### Structure du projet
