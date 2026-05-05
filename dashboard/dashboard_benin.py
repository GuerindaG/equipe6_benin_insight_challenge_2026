import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# CONFIGURATION GÉNÉRALE DE LA PAGE

st.set_page_config(
    page_title="Bénin Media Intelligence Dashboard",
    page_icon="🇧🇯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Style CSS 
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-left: 4px solid #1a5276;
        padding: 12px 16px;
        border-radius: 4px;
        margin-bottom: 8px;
    }
    .metric-label { font-size: 12px; color: #666; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-value { font-size: 28px; font-weight: bold; color: #1a5276; }
    .metric-note  { font-size: 11px; color: #888; margin-top: 4px; }
    .section-title { font-size: 18px; font-weight: 600; color: #1a5276; margin-bottom: 4px; }
    .sidebar-info  { font-size: 12px; color: #555; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)


# Téléchargement depuis GitHub 
DATA_URL = (
    "https://raw.githubusercontent.com/GuerindaG/"
    "equipe6_benin_insight_challenge_2026/main/data/raw/"
    "bq-results-20260502-112631-1777721378470.csv"
)

@st.cache_data(show_spinner="Chargement des données GDELT...")
def charger_donnees(url: str) -> pd.DataFrame:
    """
    Charge et nettoie le jeu de données GDELT depuis GitHub.
    Le résultat est mis en cache pour éviter de re-télécharger à chaque interaction.
    """
    df = pd.read_csv(url)

    # Conversion de la date
    df["SQLDATE"] = pd.to_datetime(df["SQLDATE"], format="%Y%m%d")
    df["date"]    = df["SQLDATE"]
    df["mois"]    = df["date"].dt.to_period("M").astype(str)

    # Traduction des codes événements GDELT en libellés lisibles
    mapping_themes = {
        "01": "Diplomatie / Déclarations",
        "02": "Appels / Demandes",
        "03": "Coopération",
        "04": "Consultations",
        "05": "Engagements diplomatiques",
        "06": "Aide matérielle",
        "07": "Fourniture d'aide",
        "08": "Rendition / Retrait",
        "09": "Enquêtes",
        "10": "Demandes d'action",
        "11": "Désapprobation",
        "12": "Rejets",
        "13": "Menaces",
        "14": "Protestations",
        "15": "Mobilisation forcée",
        "16": "Réduction de présence",
        "17": "Coercition",
        "18": "Agression physique",
        "19": "Combats",
        "20": "Utilisation d'armes",
    }
    df["EventRootCode"] = df["EventRootCode"].astype(str).str.zfill(2)
    df["Theme"]         = df["EventRootCode"].map(mapping_themes).fillna("Autre")

    # Etiquette de tonalité
    df["AvgTone"] = pd.to_numeric(df["AvgTone"], errors="coerce")
    df["ton_label"] = df["AvgTone"].apply(
        lambda x: "Positif" if x > 1 else ("Negatif" if x < -1 else "Neutre")
    )

    return df


# Chargement et message en cas d'erreur
try:
    df = charger_donnees(DATA_URL)
except Exception as e:
    st.error(f"Impossible de charger les données : {e}")
    st.stop()


# BARRE LATÉRALE 
with st.sidebar:
    st.markdown("## Navigation")
    galerie = st.radio(
        "Choisir une galerie d'analyse",
        options=[
            "Vue d'ensemble",
            "Rayonnement Digital & Innovation",
            "Emergence Touristique",
            "Diplomatie Active",
            "Cyber-Vigilance & Désinformation",
        ],
    )

    st.markdown("---")
    st.markdown("### Filtres globaux")

    # Filtre temporel
    date_min = df["date"].min().date()
    date_max = df["date"].max().date()
    plage = st.date_input(
        "Période analysée",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max,
    )

    # Application du filtre de date
    if isinstance(plage, (list, tuple)) and len(plage) == 2:
        df_filtre = df[
            (df["date"].dt.date >= plage[0]) &
            (df["date"].dt.date <= plage[1])
        ]
    else:
        df_filtre = df.copy()
    
      # =========================
    # SECTION ANALYSE JOURNALIÈRE
    # =========================
    st.markdown("---")
    st.markdown("### Analyse journalière des sentiments")

    jour_selectionne = st.date_input(
        "Choisir un jour à analyser",
        value=date_max,
        min_value=date_min,
        max_value=date_max,
        key="jour_sentiment"
    )

    df_jour = df[df["date"].dt.date == jour_selectionne].copy()

    st.caption(f"{len(df_jour)} article(s) trouvé(s)")

    # aperçu rapide
    if len(df_jour) > 0:
        with st.expander("Voir les articles du jour"):
            colonnes_affichage = [
                col for col in ["SOURCEURL", "title", "AvgTone"]
                if col in df_jour.columns
            ]
            st.dataframe(
                df_jour[colonnes_affichage].head(20),
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("Aucun article disponible pour cette date.")

    st.markdown("---")
    st.markdown(
        '<p class="sidebar-info">Données : GDELT Project<br>'
        'Période : 12 mois<br>'
        'Équipe 6 : Bénin Insight Challenge 2026</p>',
        unsafe_allow_html=True,
    )

# FONCTIONS UTILITAIRES POUR LES GRAPHIQUES
COULEUR_PRINCIPALE = "#1a5276"
COULEUR_POSITIVE   = "#1D9E75"
COULEUR_NEGATIVE   = "#E24B4A"
TEMPLATE_PLOTLY    = "plotly_white"


def carte_kpi(label: str, valeur: str, note: str = "") -> None:
    """Affiche un indicateur clé (KPI) sous forme de carte simple."""
    st.markdown(
        f'<div class="metric-card">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{valeur}</div>'
        f'<div class="metric-note">{note}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def graphique_evolution_temporelle(df_local: pd.DataFrame, titre: str) -> go.Figure:
    """Courbe d'évolution du nombre d'articles par mois."""
    par_mois = df_local.groupby("mois").size().reset_index(name="Nombre d'articles")
    fig = px.area(
        par_mois,
        x="mois",
        y="Nombre d'articles",
        title=titre,
        template=TEMPLATE_PLOTLY,
        color_discrete_sequence=[COULEUR_PRINCIPALE],
    )
    fig.update_layout(
        xaxis_title="Mois",
        yaxis_title="Volume d'articles",
        xaxis_tickangle=-45,
        hovermode="x unified",
    )
    return fig


# GALERIE 1 : VUE D'ENSEMBLE

if galerie == "Vue d'ensemble":

    st.title("Bénin : Tableau de bord médiatique international")
    st.markdown(
        
        "Comment le Bénin est-il perçu, cité et analysé par les médias internationaux ? "
        "Ce tableau de bord transforme des millions de signaux médiatiques (base GDELT) "
        "en intelligence stratégique pour les décideurs."
        
        "Panorama de la couverture médiatique du Bénin dans la base de données GDELT "
        "sur une période de 12 mois. Utilisez la barre latérale pour naviguer entre les galeries thématiques."
    )

    # KPIs globaux
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        carte_kpi("Total articles", f"{len(df_filtre):,}", "sur la période sélectionnée")
    with col2:
        ton_moyen = df_filtre["AvgTone"].mean()
        signe = "+" if ton_moyen > 0 else ""
        carte_kpi("Tonalité moyenne", f"{signe}{ton_moyen:.2f}", "score AvgTone GDELT")
    with col3:
        nb_acteurs = df_filtre["Actor1Name"].nunique()
        carte_kpi("Acteurs identifiés", f"{nb_acteurs:,}", "entités distinctes citées")
    with col4:
        nb_lieux = df_filtre["ActionGeo_FullName"].nunique()
        carte_kpi("Lieux couverts", f"{nb_lieux:,}", "zones géographiques citées")

    st.markdown("---")

    # Évolution temporelle
    col_g, col_d = st.columns([2, 1])

    with col_g:
        st.markdown('<p class="section-title">Evolution du volume d\'articles</p>', unsafe_allow_html=True)
        fig_evo = graphique_evolution_temporelle(df_filtre, "Volume d'articles sur le Bénin par mois")
        st.plotly_chart(fig_evo, use_container_width=True)

    with col_d:
        st.markdown('<p class="section-title">Répartition des thèmes</p>', unsafe_allow_html=True)
        theme_counts = df_filtre["Theme"].value_counts().head(10).reset_index()
        theme_counts.columns = ["Theme", "Nombre"]
        fig_themes = px.bar(
            theme_counts,
            x="Nombre",
            y="Theme",
            orientation="h",
            template=TEMPLATE_PLOTLY,
            color_discrete_sequence=[COULEUR_PRINCIPALE],
        )
        fig_themes.update_layout(
            yaxis={"categoryorder": "total ascending"},
            xaxis_title="Nombre d'articles",
            yaxis_title="",
            showlegend=False,
        )
        st.plotly_chart(fig_themes, use_container_width=True)

    st.markdown("---")

    # Sentiment + Acteurs
    col_s, col_a = st.columns(2)

    with col_s:
        st.markdown('<p class="section-title">Distribution de la tonalité médiatique</p>', unsafe_allow_html=True)
        fig_ton = px.histogram(
            df_filtre,
            x="AvgTone",
            nbins=80,
            template=TEMPLATE_PLOTLY,
            color_discrete_sequence=[COULEUR_PRINCIPALE],
            opacity=0.85,
            labels={"AvgTone": "Score AvgTone (négatif < 0 < positif)"},
        )
        fig_ton.add_vline(x=0, line_dash="dash", line_color="red",
                          annotation_text="Neutre", annotation_position="top right")
        fig_ton.update_layout(showlegend=False, bargap=0.05)
        st.plotly_chart(fig_ton, use_container_width=True)
        st.caption("Un score négatif indique une couverture défavorable ; un score positif, une couverture favorable.")

    with col_a:
        st.markdown('<p class="section-title">Top 10 des acteurs les plus cités</p>', unsafe_allow_html=True)
        acteurs = df_filtre["Actor1Name"].dropna().value_counts().head(10).reset_index()
        acteurs.columns = ["Acteur", "Apparitions"]
        fig_act = px.bar(
            acteurs,
            x="Apparitions",
            y="Acteur",
            orientation="h",
            template=TEMPLATE_PLOTLY,
            color="Apparitions",
            color_continuous_scale="Blues",
        )
        fig_act.update_layout(
            yaxis={"categoryorder": "total ascending"},
            xaxis_title="Nombre d'apparitions",
            yaxis_title="",
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_act, use_container_width=True)

# GALERIE 2 : RAYONNEMENT DIGITAL & INNOVATION

elif galerie == "Rayonnement Digital & Innovation":

    st.title("Galerie 2 : RAYONNEMENT DIGITAL & INNOVATION")
    st.markdown(
        "Cette galerie mesure l'impact des investissements technologiques du Bénin "
        "(Sèmè City, e-services, télécoms) sur sa couverture médiatique internationale."
    )

    # Filtrage des articles tech
    mots_cles_tech = ["TECHNOLOGY", "INNOVATION", "TELECOM", "EDUCATION", "SCIENCE",
                      "STARTUP", "DIGITAL", "TECH", "SEME", "FIBER", "FIBRE"]
    pattern_tech = "|".join(mots_cles_tech)

    # On cherche dans les colonnes texte disponibles 
    masque_tech = (
        df_filtre["SOURCEURL"].astype(str).str.upper().str.contains(pattern_tech, na=False) |
        df_filtre["Actor1Name"].astype(str).str.upper().str.contains(pattern_tech, na=False)
    )
    df_tech = df_filtre[masque_tech].copy()

    # KPIs
    col1, col2, col3 = st.columns(3)
    with col1:
        carte_kpi("Articles Tech identifiés", f"{len(df_tech):,}", "filtre : TECHNOLOGY, INNOVATION, TELECOM…")
    with col2:
        if len(df_tech) > 0:
            ton_tech = df_tech["AvgTone"].mean()
            signe = "+" if ton_tech > 0 else ""
            carte_kpi("Indice de Confiance Tech", f"{signe}{ton_tech:.2f}", "tonalité moyenne des articles tech")
        else:
            carte_kpi("Indice de Confiance Tech", "N/A", "pas assez de données")
    with col3:
        pct_tech = (len(df_tech) / len(df_filtre) * 100) if len(df_filtre) > 0 else 0
        carte_kpi("Part de voix Tech", f"{pct_tech:.1f}%", "du volume total d'articles Bénin")

    st.markdown("---")

    if len(df_tech) > 0:

        col_g, col_d = st.columns([2, 1])

        with col_g:
            st.markdown('<p class="section-title">Volume d\'articles Tech sur le Bénin (évolution mensuelle)</p>',
                        unsafe_allow_html=True)
            fig_tech = graphique_evolution_temporelle(df_tech, "Articles Tech & Innovation")
            st.plotly_chart(fig_tech, use_container_width=True)

        with col_d:
            st.markdown('<p class="section-title">Top mots-clés détectés dans les URLs</p>',
                        unsafe_allow_html=True)
            # Comptage simple des mots-clés
            comptage = {}
            for mot in mots_cles_tech:
                n = df_filtre["SOURCEURL"].astype(str).str.upper().str.contains(mot, na=False).sum()
                if n > 0:
                    comptage[mot] = n
            df_comptage = pd.DataFrame(list(comptage.items()), columns=["Mot-clé", "Occurrences"])
            df_comptage = df_comptage.sort_values("Occurrences", ascending=False)
            fig_kw = px.bar(
                df_comptage,
                x="Occurrences",
                y="Mot-clé",
                orientation="h",
                template=TEMPLATE_PLOTLY,
                color_discrete_sequence=[COULEUR_PRINCIPALE],
            )
            fig_kw.update_layout(
                yaxis={"categoryorder": "total ascending"},
                yaxis_title="",
                xaxis_title="Occurrences dans les URLs",
            )
            st.plotly_chart(fig_kw, use_container_width=True)

        # "Le Plus" : Top 5 sources les plus relayées
        st.markdown("---")
        st.markdown('<p class="section-title">Les 5 articles Tech les plus relayés</p>',
                    unsafe_allow_html=True)
        st.caption("Classement par nombre de mentions : proxy du relais médiatique.")

        if "NumMentions" in df_tech.columns:
            df_tech["NumMentions"] = pd.to_numeric(df_tech["NumMentions"], errors="coerce")
            top5 = (
                df_tech[["SOURCEURL", "NumMentions", "date", "AvgTone"]]
                .dropna(subset=["SOURCEURL", "NumMentions"])
                .sort_values("NumMentions", ascending=False)
                .head(5)
                .reset_index(drop=True)
            )
            top5.index = top5.index + 1
            top5.columns = ["URL Source", "Nb Mentions", "Date", "Tonalité"]
            top5["Date"] = top5["Date"].dt.strftime("%d/%m/%Y")
            top5["Tonalité"] = top5["Tonalité"].round(2)
            st.dataframe(top5, use_container_width=True)
        else:
            st.info("Colonne NumMentions non disponible dans ce jeu de données.")
    else:
        st.warning(
            "Aucun article lié aux thèmes Tech/Innovation trouvé sur la période sélectionnée. "
            "Essayez d'élargir la plage de dates."
        )

# GALERIE 3 : EMERGENCE TOURISTIQUE

elif galerie == "Emergence Touristique":

    st.title("Galerie 3 : Emergence Touristique & Valorisation du Patrimoine")
    st.markdown(
        "Analyse de l'attractivité touristique et culturelle du Bénin : Ouidah, Ganvié, "
        "Abomey, Pendjari. Comment le Bénin est-il perçu comme destination internationale ?"
    )

    # Mots-clés et sites touristiques
    sites_cles = ["OUIDAH", "GANVIE", "ABOMEY", "PENDJARI", "COTONOU"]
    mots_tourisme = ["TOURISM", "TRAVEL", "HERITAGE", "CULTURE", "MUSEUM",
                     "PATRIMOINE", "PARC", "NATURE"] + sites_cles
    pattern_tourisme = "|".join(mots_tourisme)

    masque_tourisme = (
        df_filtre["SOURCEURL"].astype(str).str.upper().str.contains(pattern_tourisme, na=False) |
        df_filtre["ActionGeo_FullName"].astype(str).str.upper().str.contains("|".join(sites_cles), na=False)
    )
    df_tour = df_filtre[masque_tourisme].copy()

    # KPIs
    col1, col2, col3 = st.columns(3)
    with col1:
        carte_kpi("Articles Tourisme", f"{len(df_tour):,}", "filtre : TOURISM, HERITAGE, sites clés")
    with col2:
        if len(df_tour) > 0:
            ton_tour = df_tour["AvgTone"].mean()
            signe = "+" if ton_tour > 0 else ""
            carte_kpi("Baromètre d'Attractivité", f"{signe}{ton_tour:.2f}",
                       "tonalité moyenne (>0 = positif)")
        else:
            carte_kpi("Baromètre d'Attractivité", "N/A", "")
    with col3:
        pct_tour = (len(df_tour) / len(df_filtre) * 100) if len(df_filtre) > 0 else 0
        carte_kpi("Part de voix Tourisme", f"{pct_tour:.1f}%", "du volume total")

    st.markdown("---")

    col_g, col_d = st.columns([2, 1])

    with col_g:
        st.markdown('<p class="section-title">Carte des événements géolocalisés au Bénin</p>',
                    unsafe_allow_html=True)
        st.caption("Taille = volume d'événements | Couleur = tonalité (vert positif, rouge négatif)")

        df_geo = df_filtre.dropna(subset=["ActionGeo_Lat", "ActionGeo_Long"]).copy()

        df_geo["GoldsteinScale"] = pd.to_numeric(
            df_geo["GoldsteinScale"], errors="coerce"
        )
        df_geo["NumMentions"] = pd.to_numeric(
            df_geo.get("NumMentions", 1), errors="coerce"
        ).fillna(1)

        if len(df_geo) > 0:
            # Agrégation par lieu
            df_lieux = df_geo.groupby("ActionGeo_FullName").agg(
                lat=("ActionGeo_Lat", "first"),
                lon=("ActionGeo_Long", "first"),
                nb_events=("ActionGeo_FullName", "count"),
                ton_moyen=("AvgTone", "mean"),
                goldstein=("GoldsteinScale", "mean"),
                nb_mentions=("NumMentions", "sum"),
            ).reset_index()

            # Filtrer les lieux avec au moins 2 événements
            df_lieux = df_lieux[df_lieux["nb_events"] >= 2].copy()

            # Hover enrichi
            df_lieux["hover"] = df_lieux.apply(
                lambda r: f"<b>{r['ActionGeo_FullName']}</b><br>"
                        f"Événements : {r['nb_events']}<br>"
                        f"Ton moyen : {r['ton_moyen']:.2f}<br>"
                        f"Goldstein : {r['goldstein']:.2f}<br>"
                        f"Mentions : {r['nb_mentions']:,.0f}",
                axis=1
            )

            fig_carte = go.Figure()

            # Points négatifs
            neg = df_lieux[df_lieux["ton_moyen"] < 0]
            fig_carte.add_trace(go.Scattermapbox(
                lat=neg["lat"],
                lon=neg["lon"],
                mode="markers",
                marker=dict(
                    size=np.sqrt(neg["nb_events"]) * 5 + 6,
                    color="#E24B4A",
                    opacity=0.75,
                    sizemode="area",
                ),
                text=neg["hover"],
                hovertemplate="%{text}<extra></extra>",
                name="Ton négatif",
            ))

            # Points positifs
            pos = df_lieux[df_lieux["ton_moyen"] >= 0]
            fig_carte.add_trace(go.Scattermapbox(
                lat=pos["lat"],
                lon=pos["lon"],
                mode="markers",
                marker=dict(
                    size=np.sqrt(pos["nb_events"]) * 5 + 6,
                    color="#1D9E75",
                    opacity=0.75,
                    sizemode="area",
                ),
                text=pos["hover"],
                hovertemplate="%{text}<extra></extra>",
                name="Ton positif",
            ))

            fig_carte.update_layout(
                mapbox=dict(
                    style="carto-positron",
                    center=dict(lat=9.3, lon=2.3),
                    zoom=6,
                ),
                legend=dict(
                    orientation="h",
                    y=0.01,
                    x=0.5,
                    xanchor="center",
                    bgcolor="rgba(255,255,255,0.85)",
                    borderwidth=0,
                ),
                margin=dict(r=0, t=80, l=0, b=0),
                height=650,
            )

            st.plotly_chart(fig_carte, use_container_width=True)

        else:
            st.info("Pas de données géolocalisées disponibles sur cette période.")

    with col_d:
        st.markdown('<p class="section-title">Part de voix : Tourisme Culturel vs Nature</p>',
                    unsafe_allow_html=True)

        culture_count = df_filtre["SOURCEURL"].astype(str).str.upper().str.contains(
            "CULTURE|HERITAGE|MUSEUM|ABOMEY|OUIDAH|PATRIMOINE", na=False
        ).sum()
        nature_count = df_filtre["SOURCEURL"].astype(str).str.upper().str.contains(
            "NATURE|PENDJARI|PARC|WILDLIFE|ECOTOURISM", na=False
        ).sum()
        autre_count  = max(0, len(df_tour) - culture_count - nature_count)

        labels = ["Tourisme Culturel", "Tourisme Nature", "Autre Tourisme"]
        values = [culture_count, nature_count, autre_count]
        couleurs = ["#1a5276", "#1D9E75", "#c0c0c0"]

        if sum(values) > 0:
            fig_pie = go.Figure(go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                marker=dict(colors=couleurs),
                textinfo="percent+label",
                insidetextorientation="radial",
            ))
            fig_pie.update_layout(
                showlegend=False,
                margin=dict(t=10, b=10, l=10, r=10),
                height=320,
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Pas de données suffisantes pour ce graphique.")

        # Mentions par site
        st.markdown('<p class="section-title">Mentions par site emblématique</p>',
                    unsafe_allow_html=True)
        mentions_sites = {}
        for site in sites_cles:
            n = df_filtre["ActionGeo_FullName"].astype(str).str.upper().str.contains(site, na=False).sum()
            n += df_filtre["SOURCEURL"].astype(str).str.upper().str.contains(site, na=False).sum()
            if n > 0:
                mentions_sites[site.capitalize()] = n
        if mentions_sites:
            df_sites = pd.DataFrame(list(mentions_sites.items()), columns=["Site", "Mentions"])
            fig_sites = px.bar(df_sites, x="Site", y="Mentions",
                               template=TEMPLATE_PLOTLY,
                               color_discrete_sequence=[COULEUR_PRINCIPALE])
            fig_sites.update_layout(xaxis_title="", yaxis_title="Mentions")
            st.plotly_chart(fig_sites, use_container_width=True)

# GALERIE 4 : DIPLOMATIE ACTIVE & OUVERTURE INTERNATIONALE
elif galerie == "Diplomatie Active":

    st.title("Galerie 4 : Diplomatie Active & Ouverture Internationale")
    st.markdown(
        "Le Bénin multiplie ses partenariats au-delà de la sphère francophone. "
        "Cette galerie analyse les interactions diplomatiques avec les USA, la Chine, le Nigeria et les Émirats."
    )

    # Pays partenaires ciblés
    pays_cibles = {
        "USA":  "États-Unis",
        "CHN":  "Chine",
        "NGA":  "Nigeria",
        "ARE":  "Émirats Arabes Unis",
        "DEU":  "Allemagne",
        "GBR":  "Royaume-Uni",
    }
    codes_diplo = ["03", "04", "05"]

    df["EventCode_str"] = df["EventCode"].astype(str).str.zfill(2)

    # Filtre diplomatie
    masque_diplo = (
        (
            (df_filtre["Actor1CountryCode"] == "BEN") &
            (df_filtre["Actor2CountryCode"].isin(pays_cibles.keys()))
        ) | (
            (df_filtre["Actor2CountryCode"] == "BEN") &
            (df_filtre["Actor1CountryCode"].isin(pays_cibles.keys()))
        )
    )
    df_diplo = df_filtre[masque_diplo].copy()

    # Si filtre strict donne peu de résultats, on élargit avec les URL
    if len(df_diplo) < 50:
        mots_diplo = ["USA", "CHINA", "CHINE", "NIGERIA", "EMIRATES", "GERMAN",
                      "COOPERATION", "COOPÉRATION", "ACCORD", "DIPLOMATIC"]
        pattern_d  = "|".join(mots_diplo)
        df_diplo   = df_filtre[
            df_filtre["SOURCEURL"].astype(str).str.upper().str.contains(pattern_d, na=False)
        ].copy()

    # KPIs
    col1, col2, col3 = st.columns(3)
    with col1:
        carte_kpi("Articles diplomatiques", f"{len(df_diplo):,}", "interactions Bénin / partenaires")
    with col2:
        if len(df_diplo) > 0:
            ton_d = df_diplo["AvgTone"].mean()
            signe = "+" if ton_d > 0 else ""
            carte_kpi("Rayonnement Diplomatique", f"{signe}{ton_d:.2f}",
                       "tonalité moyenne hors-francophonie")
        else:
            carte_kpi("Rayonnement Diplomatique", "N/A", "")
    with col3:
        nb_pays_partenaires = df_filtre["Actor2CountryCode"].nunique()
        carte_kpi("Pays partenaires détectés", f"{nb_pays_partenaires:,}", "codes pays distincts (Actor2)")

    st.markdown("---")

    col_g, col_d = st.columns([2, 1])

    with col_g:
        st.markdown('<p class="section-title">Flux diplomatiques — Sankey (Bénin vers partenaires)</p>',
                    unsafe_allow_html=True)

        # Construction du Sankey
        liens = []
        for code, nom_pays in pays_cibles.items():
            masque_p = (
                ((df_filtre["Actor1CountryCode"] == "BEN") & (df_filtre["Actor2CountryCode"] == code)) |
                ((df_filtre["Actor2CountryCode"] == "BEN") & (df_filtre["Actor1CountryCode"] == code))
            )
            volume = masque_p.sum()
            if volume > 0:
                liens.append({"Source": "Bénin", "Target": nom_pays, "Volume": volume})

        if liens:
            df_liens = pd.DataFrame(liens)
            tous_noeuds = ["Bénin"] + list(df_liens["Target"].unique())
            noeud_idx   = {n: i for i, n in enumerate(tous_noeuds)}

            fig_sankey = go.Figure(go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=tous_noeuds,
                    color=[COULEUR_PRINCIPALE] + [COULEUR_POSITIVE] * (len(tous_noeuds) - 1),
                ),
                link=dict(
                    source=[noeud_idx[r["Source"]] for _, r in df_liens.iterrows()],
                    target=[noeud_idx[r["Target"]] for _, r in df_liens.iterrows()],
                    value=df_liens["Volume"].tolist(),
                    color="rgba(26, 82, 118, 0.3)",
                ),
            ))
            fig_sankey.update_layout(height=380, margin=dict(t=20, b=20))
            st.plotly_chart(fig_sankey, use_container_width=True)
        else:
            st.info("Pas assez de données pour construire le Sankey sur cette période. Essayez une période plus longue.")

    with col_d:
        st.markdown('<p class="section-title">Langues des sources médiatiques</p>',
                    unsafe_allow_html=True)
        st.caption("Estimation par domaine de l'URL (.fr, .en, .cn...)")

        def detecter_langue(url: str) -> str:
            url = str(url).lower()
            if ".fr" in url or "france" in url or "lemonde" in url or "lefigaro" in url:
                return "Français"
            elif ".cn" in url or "xinhua" in url or "china" in url or "beijing" in url:
                return "Chinois"
            elif ".ng" in url or "nigeria" in url or "naija" in url:
                return "Anglais (Nigeria)"
            elif ".de" in url or "deutsch" in url:
                return "Allemand"
            elif ".pt" in url or "brasil" in url:
                return "Portugais"
            else:
                return "Anglais"

        if len(df_diplo) > 0:
            df_diplo["Langue"] = df_diplo["SOURCEURL"].apply(detecter_langue)
            lang_counts = df_diplo["Langue"].value_counts().reset_index()
            lang_counts.columns = ["Langue", "Articles"]
            fig_lang = go.Figure(go.Pie(
                labels=lang_counts["Langue"],
                values=lang_counts["Articles"],
                hole=0.35,
                marker=dict(colors=px.colors.qualitative.Set2),
                textinfo="percent+label",
            ))
            fig_lang.update_layout(showlegend=False, margin=dict(t=10, b=10), height=320)
            st.plotly_chart(fig_lang, use_container_width=True)
        else:
            st.info("Pas de données disponibles.")

    # Tableau des interactions par pays
    st.markdown("---")
    st.markdown('<p class="section-title">Volume d\'interactions par pays partenaire</p>',
                unsafe_allow_html=True)
    if liens:
        df_liens_sorted = df_liens.sort_values("Volume", ascending=False)
        fig_bar_diplo = px.bar(
            df_liens_sorted,
            x="Target",
            y="Volume",
            template=TEMPLATE_PLOTLY,
            color_discrete_sequence=[COULEUR_PRINCIPALE],
            labels={"Target": "Pays partenaire", "Volume": "Nombre d'articles"},
        )
        st.plotly_chart(fig_bar_diplo, use_container_width=True)


# GALERIE 5 : CYBER-VIGILANCE & DÉSINFORMATION

elif galerie == "Cyber-Vigilance & Désinformation":

    st.title("Galerie 5 : Cyber-Vigilance & Lutte contre la Désinformation")
    st.markdown(
        "Outil d'alerte précoce pour détecter des campagnes d'influence ou des pics anormaux "
        "de couverture négative. A destination du CNIN (Centre National de l'Intelligence Nationale)."
    )

    # KPIs de vigilance
    col1, col2, col3, col4 = st.columns(4)

    # Calcul du pic de volume
    par_jour = df_filtre.groupby(df_filtre["date"].dt.date).size()
    pic      = par_jour.max() if len(par_jour) > 0 else 0
    moy_jour = par_jour.mean() if len(par_jour) > 0 else 0

    with col1:
        carte_kpi("Pic quotidien détecté", f"{pic:,}",
                   f"articles en un seul jour (moy. {moy_jour:.0f}/jour)")
    with col2:
        pct_negatif = (df_filtre["ton_label"] == "Negatif").mean() * 100
        carte_kpi("Part d'articles négatifs", f"{pct_negatif:.1f}%", "ton < -1 (AvgTone)")
    with col3:
        pct_positif = (df_filtre["ton_label"] == "Positif").mean() * 100
        carte_kpi("Part d'articles positifs", f"{pct_positif:.1f}%", "ton > +1 (AvgTone)")
    with col4:
        if "GoldsteinScale" in df_filtre.columns:
            goldstein_moy = pd.to_numeric(df_filtre["GoldsteinScale"], errors="coerce").mean()
            signe = "+" if goldstein_moy > 0 else ""
            carte_kpi("Indice de Stabilité", f"{signe}{goldstein_moy:.2f}",
                       "GoldsteinScale (>0 = stabilisant)")
        else:
            carte_kpi("Indice de Stabilité", "N/A", "")

    st.markdown("---")

    # Détection de pics anormaux
    col_g, col_d = st.columns([2, 1])

    with col_g:
        st.markdown('<p class="section-title">Volume quotidien — Détection de pics anormaux</p>',
                    unsafe_allow_html=True)
        st.caption("Les points en rouge dépassent 2 fois l'écart-type de la moyenne (signal d'alerte).")

        par_jour_df = par_jour.reset_index()
        par_jour_df.columns = ["Date", "Articles"]
        par_jour_df["Date"] = pd.to_datetime(par_jour_df["Date"])
        seuil = par_jour_df["Articles"].mean() + 2 * par_jour_df["Articles"].std()
        par_jour_df["Alerte"] = par_jour_df["Articles"] > seuil

        fig_vigilance = go.Figure()
        fig_vigilance.add_trace(go.Scatter(
            x=par_jour_df["Date"], y=par_jour_df["Articles"],
            mode="lines", name="Volume quotidien",
            line=dict(color=COULEUR_PRINCIPALE, width=1.5),
        ))
        # Points en alerte
        alertes = par_jour_df[par_jour_df["Alerte"]]
        fig_vigilance.add_trace(go.Scatter(
            x=alertes["Date"], y=alertes["Articles"],
            mode="markers", name="Pic anormal",
            marker=dict(color=COULEUR_NEGATIVE, size=10, symbol="circle"),
        ))
        fig_vigilance.add_hline(
            y=seuil,
            line_dash="dash",
            line_color="orange",
            annotation_text=f"Seuil d'alerte ({seuil:.0f})",
            annotation_position="top right",
        )
        fig_vigilance.update_layout(
            template=TEMPLATE_PLOTLY,
            xaxis_title="Date",
            yaxis_title="Nombre d'articles",
            hovermode="x unified",
            legend=dict(orientation="h", y=1.1),
        )
        st.plotly_chart(fig_vigilance, use_container_width=True)

    with col_d:
        st.markdown('<p class="section-title">Evolution de la tonalité moyenne (mensuelle)</p>',
                    unsafe_allow_html=True)
        ton_mensuel = df_filtre.groupby("mois")["AvgTone"].mean().reset_index()
        ton_mensuel.columns = ["Mois", "Tonalité"]
        fig_ton = px.bar(
            ton_mensuel,
            x="Mois",
            y="Tonalité",
            template=TEMPLATE_PLOTLY,
            color="Tonalité",
            color_continuous_scale=["#E24B4A", "#f5f5f5", "#1D9E75"],
            color_continuous_midpoint=0,
            labels={"Tonalité": "Ton moyen (AvgTone)"},
        )
        fig_ton.update_layout(
            xaxis_tickangle=-45,
            coloraxis_showscale=False,
            showlegend=False,
        )
        st.plotly_chart(fig_ton, use_container_width=True)

    st.markdown("---")

    # Tableau des sources suspectes (domaines les plus actifs pendant les pics)
    st.markdown('<p class="section-title">Analyse des sources les plus actives</p>',
                unsafe_allow_html=True)
    st.caption(
        "Extraction des domaines sources (proxy de traçabilité). "
        "Un volume anormalement élevé d'un domaine inconnu peut indiquer une source coordinée."
    )

    def extraire_domaine(url: str) -> str:
        try:
            parts = str(url).split("/")
            return parts[2] if len(parts) > 2 else str(url)
        except Exception:
            return "inconnu"

    if "SOURCEURL" in df_filtre.columns:
        df_sources = df_filtre.copy()
        df_sources["domaine"] = df_sources["SOURCEURL"].apply(extraire_domaine)
        top_sources = df_sources["domaine"].value_counts().head(20).reset_index()
        top_sources.columns = ["Domaine", "Nombre d'articles"]

        fig_sources = px.bar(
            top_sources,
            x="Nombre d'articles",
            y="Domaine",
            orientation="h",
            template=TEMPLATE_PLOTLY,
            color="Nombre d'articles",
            color_continuous_scale="Blues",
        )
        fig_sources.update_layout(
            yaxis={"categoryorder": "total ascending"},
            yaxis_title="",
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_sources, use_container_width=True)

    # Box plot tonalité positif vs négatif
    st.markdown('<p class="section-title">Distribution de la tonalité par catégorie</p>',
                unsafe_allow_html=True)
    df_box = df_filtre[df_filtre["ton_label"].isin(["Positif", "Negatif"])].copy()
    if len(df_box) > 0:
        fig_box = px.box(
            df_box,
            x="ton_label",
            y="AvgTone",
            color="ton_label",
            template=TEMPLATE_PLOTLY,
            color_discrete_map={"Positif": COULEUR_POSITIVE, "Negatif": COULEUR_NEGATIVE},
            labels={"ton_label": "Catégorie", "AvgTone": "Score de tonalité"},
        )
        fig_box.update_layout(showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)

# PIED DE PAGE
st.markdown("---")
st.markdown(
    '<p style="text-align:center; color:#888; font-size:12px;">'
    "Bénin Insight Challenge 2026 : Équipe 6 | Données : GDELT Project | "
    "Dashboard v1.0"
    "</p>",
    unsafe_allow_html=True,
)
