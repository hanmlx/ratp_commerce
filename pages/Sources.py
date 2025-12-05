import streamlit as st
from datetime import datetime

st.title("ℹ️ À propos des données RATP")

st.markdown("""
Ce tableau de bord utilise les données ouvertes de la RATP concernant les commerces de proximité agréés en région parisienne.

**Source des données :** [API Open Data RATP](https://data.ratp.fr)

- **Jeu de données :** Commerces de proximité agréés RATP
- **Format :** JSON via API REST
- **URL API :** https://data.ratp.fr/api/explore/v2.1/catalog/datasets/commerces-de-proximite-agrees-ratp/records
- **Fréquence de mise à jour :** Données en temps réel
- **Limite API :** 100 enregistrements par requête
- **Total disponible :** Variable selon l'API

Les données sont récupérées dynamiquement à chaque chargement de l'application. Pour plus d'informations, consultez la [documentation officielle](https://data.ratp.fr/pages/home/).
""")

# Afficher la date de dernière synchronisation
st.info(f"**Dernière synchronisation :** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
