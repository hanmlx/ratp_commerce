import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Tableau de bord des commerces RATP",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titre et introduction
st.title("🏪 Tableau de bord des commerces de proximité agréés RATP")
st.markdown("""
Ce tableau de bord présente les données des commerces de proximité agréés par la RATP en région parisienne.
Les données proviennent de la plateforme Open Data de la RATP.
""")

# Fonction pour charger les données depuis l'API
@st.cache_data(ttl=3600)  # Cache 1 heure
def load_data_from_api():
    url = "https://data.ratp.fr/api/explore/v2.1/catalog/datasets/commerces-de-proximite-agrees-ratp/records"
    
    try:
        all_records = []
        offset = 0
        limit = 100  # Limite maximale autorisée par l'API
        
        while True:
            # Récupérer les données par lots
            params = {
                'limit': limit,
                'offset': offset
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Vérifier si des résultats sont présents
            records = data.get('results', [])
            if not records:
                break
                
            all_records.extend(records)
            
            # Vérifier si nous avons récupéré tous les résultats
            if len(records) < limit:
                break
                
            offset += limit
        
        if not all_records:
            st.error("Aucune donnée trouvée dans l'API")
            return pd.DataFrame()
        
        # Convertir en DataFrame
        df = pd.DataFrame(all_records)
        
        # Nettoyer et standardiser les noms de colonnes
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        st.success(f"✅ Données chargées avec succès : {len(df)} commerces trouvés")
        return df
        
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erreur lors du chargement des données : {e}")
        return pd.DataFrame()

# Fonction pour mapper et normaliser les colonnes
def normalize_columns(df):
    """Normalise les noms de colonnes pour assurer la compatibilité"""
    column_mapping = {
        'commerce': 'type_commerce',
        'dea_nom_commerce': 'nom_commerce',
        'dea_jour_fermeture': 'jour_fermeture',
        'dea_rue_livraison': 'rue',
        'dea_cp_livraison': 'code_postal',
        'dea_commune_livraison': 'commune',
        'geocodage_ban': 'coordonnees'
    }
    
    # Renommer les colonnes existantes
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns and new_col not in df.columns:
            df[new_col] = df[old_col]
    
    return df

# Fonction pour extraire les coordonnées géographiques
def extract_coordinates(df):
    """Extrait les coordonnées latitude/longitude des différentes colonnes possibles"""
    # Essayer la colonne geocodage_ban (format JSON avec lat/lon)
    if 'geocodage_ban' in df.columns:
        try:
            # Extraire les coordonnées du format JSON
            df['latitude'] = df['geocodage_ban'].apply(lambda x: x.get('lat') if isinstance(x, dict) else None)
            df['longitude'] = df['geocodage_ban'].apply(lambda x: x.get('lon') if isinstance(x, dict) else None)
            
            # Convertir en numérique
            df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
            df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
            
            # Vérifier si nous avons des coordonnées valides
            if df['latitude'].notna().any() and df['longitude'].notna().any():
                return df
        except:
            pass
    
    # Essayer d'autres colonnes de coordonnées
    coord_columns = ['coordonnees', 'geo_point_2d', 'geolocation']
    
    for col in coord_columns:
        if col in df.columns:
            try:
                # Séparer latitude et longitude si format "lat,lon"
                if df[col].dtype == 'object' and df[col].str.contains(',').any():
                    coords = df[col].str.split(',', expand=True)
                    if len(coords.columns) == 2:
                        df['latitude'] = pd.to_numeric(coords[0], errors='coerce')
                        df['longitude'] = pd.to_numeric(coords[1], errors='coerce')
                        break
            except:
                continue
    
    # Vérifier les colonnes latitude/longitude séparées
    if 'latitude' not in df.columns or 'longitude' not in df.columns:
        for lat_col in ['latitude', 'lat']:
            for lon_col in ['longitude', 'lon', 'lng']:
                if lat_col in df.columns and lon_col in df.columns:
                    df['latitude'] = pd.to_numeric(df[lat_col], errors='coerce')
                    df['longitude'] = pd.to_numeric(df[lon_col], errors='coerce')
                    break
    
    return df

# Application principale
def main():
    # Chargement des données
    with st.spinner('Chargement des données depuis l\'API RATP...'):
        df = load_data_from_api()
    
    if df.empty:
        st.warning("Impossible de charger les données. Veuillez vérifier votre connexion internet.")
        return
    
    # Normalisation des colonnes
    df = normalize_columns(df)
    df = extract_coordinates(df)
    
    # Choix de la page
    st.sidebar.subheader("Navigation")
    page_choisie = st.sidebar.radio("Choisir une page", [
        "📈 Analyse statistique", 
        "🗺️ Distribution géographique", 
        "🏪 Détail des commerces", 
        "📋 Données brutes"
    ])
    
    # Filtrage des données
    st.sidebar.subheader("Filtrage des données")
    
    # Filtre par type de commerce (multiples choix)
    type_col = 'tco_libelle' if 'tco_libelle' in df.columns else 'commerce' if 'commerce' in df.columns else 'type_commerce'
    if type_col in df.columns:
        types_commerce_disponibles = sorted(df[type_col].dropna().unique().tolist())
        types_selectionnes = st.sidebar.multiselect("Types de commerce", types_commerce_disponibles, default=types_commerce_disponibles)
        
        if types_selectionnes:
            df = df[df[type_col].isin(types_selectionnes)]
    
    # Filtre par commune (multiples choix)
    commune_col = 'commune' if 'commune' in df.columns else 'dea_commune_livraison'
    if commune_col in df.columns:
        communes_disponibles = sorted(df[commune_col].dropna().unique().tolist())
        communes_selectionnees = st.sidebar.multiselect("Communes", communes_disponibles, default=communes_disponibles)
        
        if communes_selectionnees:
            df = df[df[commune_col].isin(communes_selectionnees)]
    
    # Afficher le contenu selon la page choisie
    if page_choisie == "📈 Analyse statistique":
        st.subheader("📊 Aperçu des données")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_commerces = len(df)
            st.metric("Nombre total de commerces", total_commerces)
        
        with col2:
            type_col = 'tco_libelle' if 'tco_libelle' in df.columns else 'commerce' if 'commerce' in df.columns else 'type_commerce'
            nb_types = df[type_col].nunique() if type_col in df.columns else 0
            st.metric("Types de commerce", nb_types)
        
        with col3:
            commune_col = 'commune' if 'commune' in df.columns else 'dea_commune_livraison'
            nb_communes = df[commune_col].nunique() if commune_col in df.columns else 0
            st.metric("Communes", nb_communes)
        
        with col4:
            has_coords = all(col in df.columns for col in ['latitude', 'longitude'])
            coords_valides = df.dropna(subset=['latitude', 'longitude']).shape[0] if has_coords else 0
            st.metric("Coordonnées valides", coords_valides)
        
        # Graphiques univariés
        st.subheader("📊 Analyses univariées")
        
        if not df.empty:
            type_col = 'tco_libelle' if 'tco_libelle' in df.columns else 'commerce' if 'commerce' in df.columns else 'type_commerce'
            
            # Analyse des types de commerce
            if type_col in df.columns:
                st.write("**Répartition des types de commerce**")
                type_counts = df[type_col].value_counts().reset_index()
                type_counts.columns = ['type_commerce', 'nombre']
                
                col1, col2 = st.columns(2)
                with col1:
                    # Graphique en barres
                    fig_bar = px.bar(type_counts.head(10), x='type_commerce', y='nombre',
                                   title="Top 10 - Barres")
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                with col2:
                    # Graphique circulaire
                    fig_pie = px.pie(type_counts.head(8), values='nombre', names='type_commerce',
                                    title="Top 8 - Camembert")
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                # Histogramme
                fig_hist = px.histogram(type_counts, x='nombre', nbins=20,
                                     title="Distribution des fréquences")
                st.plotly_chart(fig_hist, use_container_width=True)
            
            # Analyse des communes
            commune_col = 'commune' if 'commune' in df.columns else 'dea_commune_livraison'
            if commune_col in df.columns:
                st.write("**Répartition par commune**")
                commune_counts = df[commune_col].value_counts().reset_index()
                commune_counts.columns = ['commune', 'nombre']
                
                col1, col2 = st.columns(2)
                with col1:
                    # Barres horizontales
                    fig_hbar = px.bar(commune_counts.head(10), x='nombre', y='commune',
                                     orientation='h', title="Top 10 - Barres horizontales")
                    st.plotly_chart(fig_hbar, use_container_width=True)
                
                with col2:
                    # Nuage de points
                    fig_scatter = px.scatter(commune_counts.head(15), x=range(len(commune_counts.head(15))), 
                                          y='nombre', hover_name='commune',
                                          title="Distribution - Nuage de points")
                    st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Graphiques bivariés
        st.subheader("📈 Analyses bivariées")
        
        if not df.empty and type_col in df.columns and commune_col in df.columns:
            # Croisement types de commerce vs communes
            st.write("**Types de commerce par commune**")
            
            # Top 10 des communes pour l'analyse
            top_communes = df[commune_col].value_counts().head(10).index.tolist()
            df_top = df[df[commune_col].isin(top_communes)]
            
            # Graphique en barres groupées
            cross_tab = pd.crosstab(df_top[type_col], df_top[commune_col])
            fig_grouped = px.bar(cross_tab.reset_index().melt(id_vars=[type_col]), 
                               x=type_col, y='value', color='commune',
                               title="Types de commerce par commune (Top 10)")
            fig_grouped.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_grouped, use_container_width=True)
            
            # Heatmap
            fig_heatmap = px.imshow(cross_tab, 
                                  title="Heatmap - Types de commerce vs Communes",
                                  labels=dict(x="Commune", y="Type de commerce", color="Nombre"))
            st.plotly_chart(fig_heatmap, use_container_width=True)
            
            # Box plot
            col1, col2 = st.columns(2)
            with col1:
                # Distribution par commune
                box_data = df.groupby(commune_col).size().reset_index(name='count')
                fig_box = px.box(box_data, y='count', 
                               title="Distribution du nombre de commerces par commune")
                st.plotly_chart(fig_box, use_container_width=True)
            
            with col2:
                # Distribution par type de commerce
                box_data_type = df.groupby(type_col).size().reset_index(name='count')
                fig_box_type = px.box(box_data_type, y='count',
                                     title="Distribution du nombre de commerces par type")
                st.plotly_chart(fig_box_type, use_container_width=True)
        
        # Analyses temporelles si données disponibles
        if 'date_creation' in df.columns or 'date' in df.columns:
            st.write("**Analyses temporelles**")
            date_col = 'date_creation' if 'date_creation' in df.columns else 'date'
            if date_col in df.columns:
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                df_temp = df.dropna(subset=[date_col])
                
                if not df_temp.empty:
                    # Évolution temporelle
                    df_temp['mois'] = df_temp[date_col].dt.to_period('M').astype(str)
                    monthly_counts = df_temp['mois'].value_counts().sort_index().reset_index()
                    monthly_counts.columns = ['mois', 'nombre']
                    
                    fig_time = px.line(monthly_counts, x='mois', y='nombre',
                                    title="Évolution temporelle des commerces")
                    fig_time.update_xaxis(tickangle=45)
                    st.plotly_chart(fig_time, use_container_width=True)
    
    elif page_choisie == "🗺️ Distribution géographique":
        st.subheader("Distribution géographique")
        
        # Vérifier la présence de coordonnées géographiques
        has_coords = all(col in df.columns for col in ['latitude', 'longitude'])
        
        if has_coords and not df.empty:
            # Préparer les données pour la carte
            df_carte = df.dropna(subset=['latitude', 'longitude']).copy()
            
            if not df_carte.empty:
                # Afficher la carte
                st.map(df_carte, latitude='latitude', longitude='longitude')
                
                # Informations supplémentaires
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Commerces localisés", len(df_carte))
                with col2:
                    commune_col = 'commune' if 'commune' in df_carte.columns else 'dea_commune_livraison'
                    if commune_col in df_carte.columns:
                        st.metric("Communes couvertes", df_carte[commune_col].nunique())
            else:
                st.info("Aucune coordonnée géographique valide trouvée")
        else:
            st.info("Coordonnées géographiques non disponibles dans les données de l'API")
    
    elif page_choisie == "🏪 Détail des commerces":
        st.subheader("Détail des commerces")
        
        if not df.empty:
            nom_col = 'nom_commerce' if 'nom_commerce' in df.columns else 'dea_nom_commerce'
            
            for idx, commerce in df.iterrows():
                nom_commerce = commerce.get(nom_col, 'Nom non disponible')
                type_commerce = commerce.get(type_col, 'Type non disponible')
                
                with st.expander(f"{nom_commerce} - {type_commerce}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Informations générales:**")
                        if type_col in commerce:
                            st.write(f"Type: {commerce[type_col]}")
                        
                        commune_col = 'commune' if 'commune' in commerce else 'dea_commune_livraison'
                        if commune_col in commerce:
                            st.write(f"Commune: {commerce[commune_col]}")
                        
                        rue_col = 'rue' if 'rue' in commerce else 'dea_rue_livraison'
                        if rue_col in commerce:
                            st.write(f"Rue: {commerce[rue_col]}")
                        
                        cp_col = 'code_postal' if 'code_postal' in commerce else 'dea_cp_livraison'
                        if cp_col in commerce:
                            st.write(f"Code postal: {commerce[cp_col]}")
                    
                    with col2:
                        st.write("**Coordonnées:**")
                        if 'latitude' in commerce and pd.notna(commerce['latitude']):
                            st.write(f"Latitude: {commerce['latitude']}")
                        if 'longitude' in commerce and pd.notna(commerce['longitude']):
                            st.write(f"Longitude: {commerce['longitude']}")
                        
                        fermeture_col = 'jour_fermeture' if 'jour_fermeture' in commerce else 'dea_jour_fermeture'
                        if fermeture_col in commerce:
                            st.write(f"Jour de fermeture: {commerce[fermeture_col]}")
        else:
            st.info("Aucun commerce à afficher")
    
    elif page_choisie == "📋 Données brutes":
        st.subheader("Données brutes")
        
        if not df.empty:
            st.write(f"Affichage de {len(df)} commerces")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Aucune donnée à afficher")
            st.write("**Statistiques de base:**")
            st.write(f"Nombre de lignes: {len(df)}")
            st.write(f"Nombre de colonnes: {len(df.columns)}")
            st.write(f"Valeurs manquantes: {df.isnull().sum().sum()}")
    
    # Informations dans la barre latérale
    st.sidebar.markdown("---")
    st.sidebar.subheader("ℹ️ À propos")
    st.sidebar.info("""
    **Source des données:** API Open Data RATP  
    **Jeu de données:** Commerces de proximité agréés RATP  
    **Dernière mise à jour:** Données en temps réel  
    **URL API:** data.ratp.fr
    """)

if __name__ == "__main__":
    main()
