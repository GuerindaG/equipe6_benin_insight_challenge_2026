import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from urllib.parse import urlparse

# ──────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Bénin Insights Dashboard",
    page_icon="🇧🇯",
    layout="wide",
    initial_sidebar_state="expanded",
)

COULEUR_PRINCIPALE = "#006BA6"
COULEUR_POS = "#2E8B57"
COULEUR_NEG = "#B22222"
COULEUR_NEUTRE = "#808080"
TEMPLATE = "plotly_white"

# CSS custom
st.markdown("""
<style>
:root { --primary: #006BA6; --bg: #f8f9fa; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
h1, h2, h3 { color: #1a5276 !important; }
.stMetric > div > div > div { font-size: 1.8rem !important; }
.kpi-row { display: flex; gap: 1rem; margin-bottom: 1rem; }
.sidebar-info { font-size: 13px; color: #555; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# CHARGEMENT DES DONNÉES
# ──────────────────────────────────────────────
DATA_URL = (
    "https://raw.githubusercontent.com/GuerindaG/"
    "equipe6_benin_insight_challenge_2026/main/data/raw/"
    "bq-results-20260502-112631-1777721378470.csv"
)

code_pays = {
    'BEN':'Bénin', 'BJ':'Bénin', 'USA':'États-Unis', 'CHN':'Chine', 'FRA':'France',
    'GBR':'R.-U.', 'NGA':'Nigéria', 'NER':'Niger', 'BFA':'Burkina Faso',
    "CIV":"Côte d'Ivoire", 'TGO':'Togo', 'GHA':'Ghana', 'DEU':'Allemagne',
    'RUS':'Russie', 'IND':'Inde', 'CAN':'Canada', 'AUS':'Australie', 'JPN':'Japon',
    'BRA':'Brésil', 'ZAF':'Af. du Sud', 'ARE':'Émirats Arabes Unis',
    'SAU':'Arabie Saoudite', 'KEN':'Kenya', 'EGY':'Égypte', 'DZA':'Algérie',
    'MAR':'Maroc', 'SEN':'Sénégal', 'MLI':'Mali', 'LBR':'Liberia',
    'LCA':'Sainte-Lucie', 'UNO':'ONU', 'IGO':'Org. internationale',
}

mapping_themes = {
    "01": "Diplomatie / Déclarations", "02": "Appels / Demandes",
    "03": "Coopération", "04": "Consultations",
    "05": "Engagements diplomatiques", "06": "Aide matérielle",
    "07": "Fourniture d'aide", "08": "Rendition / Retrait",
    "09": "Enquêtes", "10": "Demandes d'action",
    "11": "Désapprobation", "12": "Rejets",
    "13": "Menaces", "14": "Protestations",
    "15": "Mobilisation forcée", "16": "Réduction de présence",
    "17": "Coercition", "18": "Agression physique",
    "19": "Combats", "20": "Utilisation d'armes",
}

@st.cache_data(show_spinner="Chargement des données GDELT…")
def charger_donnees(url):
    df = pd.read_csv(url, engine='python', on_bad_lines='skip')
    df.columns = [c.strip() for c in df.columns]

    df["SQLDATE"] = pd.to_datetime(df["SQLDATE"], format="%Y%m%d", errors="coerce")
    df["date"] = df["SQLDATE"]
    df["mois"] = df["date"].dt.to_period("M").astype(str)
    df["AvgTone"] = pd.to_numeric(df["AvgTone"], errors="coerce")
    df["GoldsteinScale"] = pd.to_numeric(df["GoldsteinScale"], errors="coerce")
    df["NumArticles"] = pd.to_numeric(df["NumArticles"], errors="coerce")
    df["NumMentions"] = pd.to_numeric(df["NumMentions"], errors="coerce")
    df["NumSources"] = pd.to_numeric(df["NumSources"], errors="coerce")

    df["EventRootCode"] = df["EventRootCode"].astype(str).str.zfill(2)
    df["Theme"] = df["EventRootCode"].map(mapping_themes).fillna("Autre")

    df["ton_label"] = df["AvgTone"].apply(
        lambda x: "Positif" if x > 1 else ("Négatif" if x < -1 else "Neutre")
    )
    df["domain"] = df["SOURCEURL"].apply(
        lambda u: urlparse(str(u)).netloc.replace("www.", "") if pd.notna(u) else "inconnu"
    )
    return df

try:
    df = charger_donnees(DATA_URL)
except Exception as e:
    st.error(f"Impossible de charger les données : {e}")
    st.stop()

# ──────────────────────────────────────────────
# BARRE LATÉRALE
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🇧🇯 Bénin Insights")
    st.markdown("---")
    galerie = st.radio(
        "Navigation",
        ["Vue d'ensemble", "Couverture médiatique", "Sentiment & Perception",
         "Acteurs & Diplomatie", "Digital & Tourisme", "Cyber-Vigilance"],
    )
    st.markdown("---")
    st.markdown("### Filtres")
    date_min, date_max = df["date"].min().date(), df["date"].max().date()
    plage = st.date_input("Période", value=(date_min, date_max), min_value=date_min, max_value=date_max)

    if isinstance(plage, (list, tuple)) and len(plage) == 2:
        df_f = df[(df["date"].dt.date >= plage[0]) & (df["date"].dt.date <= plage[1])]
    else:
        df_f = df.copy()

    st.markdown("---")
    st.markdown('<p class="sidebar-info">Données : GDELT Project 2025<br>Équipe 6 — Bénin Insight Challenge</p>', unsafe_allow_html=True)

# ──────────────────────────────────────────────
# VUE D'ENSEMBLE
# ──────────────────────────────────────────────
if galerie == "Vue d'ensemble":
    st.title("🇧🇯 Vue d'ensemble — Bénin 2025")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Événements", f"{len(df_f):,}")
    c2.metric("Articles", f"{df_f['NumArticles'].sum():,.0f}")
    c3.metric("Tonalité moy.", f"{df_f['AvgTone'].mean():.2f}")
    c4.metric("Sources médiatiques", f"{df_f['domain'].nunique()}")

    # Évolution temporelle
    st.markdown("### Évolution de la couverture médiatique")
    monthly = df_f.groupby("mois").agg(
        evenements=("GLOBALEVENTID", "nunique"),
        articles=("NumArticles", "sum"),
        avg_tone=("AvgTone", "mean"),
    ).reset_index()

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        subplot_titles=("Volume d'événements", "Tonalité moyenne"),
                        vertical_spacing=0.10)
    fig.add_trace(go.Scatter(x=monthly["mois"], y=monthly["evenements"],
                             mode="lines+markers", name="Événements",
                             line=dict(color=COULEUR_PRINCIPALE)), row=1, col=1)
    fig.add_trace(go.Scatter(x=monthly["mois"], y=monthly["avg_tone"],
                             mode="lines+markers", name="AvgTone",
                             line=dict(color=COULEUR_POS)), row=2, col=1)
    fig.add_hline(y=0, line_dash="dot", line_color="gray", row=2, col=1)
    fig.update_layout(template=TEMPLATE, height=550, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

    # Thèmes dominants
    st.markdown("### Thèmes dominants")
    themes = df_f["Theme"].value_counts().head(10).reset_index()
    themes.columns = ["Thème", "Événements"]
    fig_t = px.bar(themes, x="Événements", y="Thème", orientation="h",
                    color="Événements", color_continuous_scale="Blues",
                    title="Top 10 des thèmes associés au Bénin")
    fig_t.update_layout(template=TEMPLATE, height=420)
    st.plotly_chart(fig_t, use_container_width=True)

    # Sentiment
    st.markdown("### Répartition du sentiment")
    sent = df_f["ton_label"].value_counts().reset_index()
    sent.columns = ["Sentiment", "Nombre"]
    colors = {"Positif": COULEUR_POS, "Neutre": COULEUR_NEUTRE, "Négatif": COULEUR_NEG}
    fig_s = px.pie(sent, names="Sentiment", values="Nombre", color="Sentiment",
                   color_discrete_map=colors, title="Classification de la couverture médiatique")
    fig_s.update_layout(template=TEMPLATE)
    st.plotly_chart(fig_s, use_container_width=True)

# ──────────────────────────────────────────────
# COUVERTURE MÉDIATIQUE
# ──────────────────────────────────────────────
elif galerie == "Couverture médiatique":
    st.title("📊 Couverture médiatique")

    daily = df_f.groupby("date").agg(
        evenements=("GLOBALEVENTID", "nunique"),
        articles=("NumArticles", "sum"),
    ).reset_index()

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        subplot_titles=("Événements quotidiens", "Articles quotidiens"),
                        vertical_spacing=0.10)
    fig.add_trace(go.Scatter(x=daily["date"], y=daily["evenements"],
                             mode="lines", name="Événements", line=dict(color=COULEUR_PRINCIPALE)), row=1, col=1)
    fig.add_trace(go.Scatter(x=daily["date"], y=daily["articles"],
                             mode="lines", name="Articles", line=dict(color="seagreen")), row=2, col=1)
    fig.update_layout(template=TEMPLATE, height=550, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

    # Détection de pics
    mean_e = daily["evenements"].mean()
    std_e = daily["evenements"].std()
    daily["z"] = (daily["evenements"] - mean_e) / std_e
    pics = daily[daily["z"] > 2]

    c1, c2 = st.columns(2)
    c1.metric("Pics détectés (Z>2)", f"{len(pics)}")
    c2.metric("Moy. quotidienne", f"{mean_e:.0f} événements/jour")

    if len(pics) > 0:
        st.markdown("### Jours de pic")
        st.dataframe(pics[["date","evenements","z"]].sort_values("z", ascending=False).head(10),
                     use_container_width=True, hide_index=True)

    # Top domaines
    st.markdown("### Top 15 domaines médiatiques")
    top_dom = df_f["domain"].value_counts().head(15).reset_index()
    top_dom.columns = ["Domaine", "Articles"]
    fig_d = px.bar(top_dom, x="Articles", y="Domaine", orientation="h",
                   color="Articles", color_continuous_scale="magma",
                   title="Sources médiatiques couvrant le Bénin")
    fig_d.update_layout(template=TEMPLATE, height=450)
    st.plotly_chart(fig_d, use_container_width=True)

# ──────────────────────────────────────────────
# SENTIMENT & PERCEPTION
# ──────────────────────────────────────────────
elif galerie == "Sentiment & Perception":
    st.title("💬 Sentiment & Perception")

    c1, c2, c3 = st.columns(3)
    c1.metric("AvgTone moyen", f"{df_f['AvgTone'].mean():.2f}")
    c2.metric("Goldstein moyen", f"{df_f['GoldsteinScale'].mean():.2f}")
    c3.metric("% Positif", f"{(df_f['ton_label']=='Positif').mean()*100:.1f}%")

    # Distribution
    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=("Distribution AvgTone", "Distribution GoldsteinScale"))
    fig.add_trace(go.Histogram(x=df_f["AvgTone"], nbinsx=60, marker_color=COULEUR_PRINCIPALE, name="AvgTone"), row=1, col=1)
    fig.add_trace(go.Histogram(x=df_f["GoldsteinScale"], nbinsx=60, marker_color="seagreen", name="Goldstein"), row=1, col=2)
    fig.update_layout(template=TEMPLATE, showlegend=False, height=380)
    st.plotly_chart(fig, use_container_width=True)

    # Évolution mensuelle
    monthly_s = df_f.groupby("mois").agg(
        avg_tone=("AvgTone", "mean"),
        avg_goldstein=("GoldsteinScale", "mean"),
    ).reset_index()

    fig2 = make_subplots(specs=[[{"secondary_y": True}]])
    fig2.add_trace(go.Scatter(x=monthly_s["mois"], y=monthly_s["avg_tone"],
                              mode="lines+markers", name="AvgTone", line=dict(color=COULEUR_PRINCIPALE)), secondary_y=False)
    fig2.add_trace(go.Scatter(x=monthly_s["mois"], y=monthly_s["avg_goldstein"],
                              mode="lines+markers", name="Goldstein", line=dict(color="seagreen")), secondary_y=True)
    fig2.add_hline(y=0, line_dash="dot", line_color="gray", secondary_y=False)
    fig2.update_layout(title="Évolution mensuelle de la perception", template=TEMPLATE, height=420)
    fig2.update_yaxes(title_text="AvgTone", secondary_y=False)
    fig2.update_yaxes(title_text="GoldsteinScale", secondary_y=True)
    st.plotly_chart(fig2, use_container_width=True)

    # Sentiment par pays
    st.markdown("### Tonalité par pays partenaire")
    df_sp = df_f.dropna(subset=["Actor1CountryCode", "AvgTone"])
    df_sp = df_sp[~df_sp["Actor1CountryCode"].isin(["BEN","BJ"])]
    top_c = df_sp["Actor1CountryCode"].value_counts().head(12).index
    df_top = df_sp[df_sp["Actor1CountryCode"].isin(top_c)]
    sent_c = df_top.groupby("Actor1CountryCode").agg(
        avg_tone=("AvgTone", "mean"), count=("GLOBALEVENTID", "nunique")
    ).reset_index()
    sent_c["Pays"] = sent_c["Actor1CountryCode"].map(code_pays).fillna(sent_c["Actor1CountryCode"])
    fig_c = px.bar(sent_c.sort_values("avg_tone"), x="avg_tone", y="Pays",
                   color="avg_tone", color_continuous_scale="RdYlGn",
                   title="Tonalité moyenne par pays (hors Bénin)")
    fig_c.update_layout(template=TEMPLATE, height=450)
    st.plotly_chart(fig_c, use_container_width=True)

    # Sentiment par type d'événement
    st.markdown("### Sentiment par type d'événement")
    sent_ev = df_f.groupby("Theme").agg(
        avg_tone=("AvgTone", "mean"), count=("GLOBALEVENTID", "nunique")
    ).reset_index().sort_values("count", ascending=False).head(10)
    fig_ev = px.bar(sent_ev, x="avg_tone", y="Theme", orientation="h",
                    color="avg_tone", color_continuous_scale="RdYlGn",
                    title="Tonalité par type d'événement (CAMEO)")
    fig_ev.update_layout(template=TEMPLATE, height=400)
    st.plotly_chart(fig_ev, use_container_width=True)

# ──────────────────────────────────────────────
# ACTEURS & DIPLOMATIE
# ──────────────────────────────────────────────
elif galerie == "Acteurs & Diplomatie":
    st.title("🌍 Acteurs & Diplomatie")

    # Pays les plus mentionnés
    st.markdown("### Pays les plus mentionnés avec le Bénin")
    countries = pd.concat([
        df_f["Actor1CountryCode"].map(code_pays).fillna(df_f["Actor1CountryCode"]),
        df_f["Actor2CountryCode"].map(code_pays).fillna(df_f["Actor2CountryCode"]),
    ], ignore_index=True)
    countries = countries[countries != "Bénin"].value_counts().head(15).reset_index()
    countries.columns = ["Pays", "Mentions"]
    fig_p = px.bar(countries, x="Mentions", y="Pays", orientation="h",
                   color="Mentions", color_continuous_scale="Blues",
                   title="Top 15 pays partenaires")
    fig_p.update_layout(template=TEMPLATE, height=450)
    st.plotly_chart(fig_p, use_container_width=True)

    # Acteurs
    st.markdown("### Acteurs / entités les plus cités")
    actors = pd.concat([df_f["Actor1Name"].dropna(), df_f["Actor2Name"].dropna()])
    actors = actors.str.strip().str.upper()
    actors = actors[actors != "BENIN"].value_counts().head(15).reset_index()
    actors.columns = ["Acteur", "Fréquence"]
    fig_a = px.bar(actors, x="Fréquence", y="Acteur", orientation="h",
                   color="Fréquence", color_continuous_scale="Viridis",
                   title="Top 15 des acteurs")
    fig_a.update_layout(template=TEMPLATE, height=420)
    st.plotly_chart(fig_a, use_container_width=True)

    # Sankey
    st.markdown("### Flux d'interactions médiatiques")
    flux = df_f[["Actor1CountryCode","Actor2CountryCode","NumArticles"]].dropna()
    flux = flux[flux["Actor1CountryCode"] != flux["Actor2CountryCode"]]
    flux_bj = flux[(flux["Actor1CountryCode"]=="BEN") | (flux["Actor2CountryCode"]=="BEN")].copy()

    if len(flux_bj) > 0:
        sources, targets, values = [], [], []
        for _, row in flux_bj.iterrows():
            a1, a2, val = row["Actor1CountryCode"], row["Actor2CountryCode"], row["NumArticles"]
            s = code_pays.get(a1, a1) if a1 == "BEN" else code_pays.get(a2, a2)
            t = code_pays.get(a2, a2) if a1 == "BEN" else code_pays.get(a1, a1)
            sources.append(s); targets.append(t); values.append(val)

        flux_df = pd.DataFrame({"source": sources, "target": targets, "value": values})
        flux_agg = flux_df.groupby(["source","target"])["value"].sum().reset_index()
        flux_agg = flux_agg.sort_values("value", ascending=False).head(20)
        all_nodes = list(pd.unique(flux_agg[["source","target"]].values.ravel()))
        node_idx = {n: i for i, n in enumerate(all_nodes)}

        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(label=all_nodes, color="lightblue"),
            link=dict(
                source=[node_idx[s] for s in flux_agg["source"]],
                target=[node_idx[t] for t in flux_agg["target"]],
                value=flux_agg["value"],
            ))])
        fig_sankey.update_layout(title="Flux d'interactions via le Bénin (Top 20)", template=TEMPLATE, height=500)
        st.plotly_chart(fig_sankey, use_container_width=True)
    else:
        st.info("Aucun flux trouvé pour le diagramme de Sankey.")

    # Diplomatie hors francophonie
    st.markdown("### Diplomatie hors francophonie")
    targets_d = ["USA","CHN","NGA","GBR","ARE","JPN","IND","DEU","RUS","BRA"]
    codes_t = targets_d + ["BEN"]
    flux_d = df_f[["Actor1CountryCode","Actor2CountryCode","AvgTone","NumArticles"]].dropna()
    flux_d = flux_d[(flux_d["Actor1CountryCode"].isin(codes_t)) & (flux_d["Actor2CountryCode"].isin(codes_t))]
    flux_d = flux_d[(flux_d["Actor1CountryCode"]=="BEN") | (flux_d["Actor2CountryCode"]=="BEN")].copy()
    flux_d["Paire"] = flux_d.apply(
        lambda r: " ↔ ".join(sorted([code_pays.get(r["Actor1CountryCode"], r["Actor1CountryCode"]),
                                      code_pays.get(r["Actor2CountryCode"], r["Actor2CountryCode"])])), axis=1)
    diplo = flux_d.groupby("Paire").agg(articles=("NumArticles","sum"), tone=("AvgTone","mean")).reset_index()
    diplo = diplo.sort_values("articles", ascending=False).head(10)
    fig_diplo = px.bar(diplo, x="articles", y="Paire", orientation="h",
                       color="tone", color_continuous_scale="RdYlGn",
                       title="Top relations diplomatiques du Bénin (hors francophonie)")
    fig_diplo.update_layout(template=TEMPLATE, height=400)
    st.plotly_chart(fig_diplo, use_container_width=True)

# ──────────────────────────────────────────────
# DIGITAL & TOURISME
# ──────────────────────────────────────────────
elif galerie == "Digital & Tourisme":
    st.title("🚀 Digital, Tourisme & Attractivité")

    # Digital
    st.markdown("### Rayonnement Digital")
    kw_digital = ['digital','technology','tech','innovation','semecity','semè city',
                   'e-service','internet','startup','fintech','cyber','smart city',
                   'numérique','informatique','transformation digitale']
    import re
    pat_digital = re.compile('|'.join(kw_digital), flags=re.IGNORECASE)
    mask = df_f["SOURCEURL"].str.contains(pat_digital, na=False) | df_f["Actor1Name"].str.contains(pat_digital, na=False)
    df_digital = df_f[mask].copy()
    c1, c2, c3 = st.columns(3)
    c1.metric("Articles digital", f"{len(df_digital):,}")
    if len(df_digital) > 0:
        c2.metric("AvgTone digital", f"{df_digital['AvgTone'].mean():.2f}")
        c3.metric("Indice Confiance Tech", f"{df_digital['AvgTone'].mean():.2f}")
        df_digital["mois_d"] = df_digital["date"].dt.to_period("M").astype(str)
        trend = df_digital.groupby("mois_d")["GLOBALEVENTID"].nunique().reset_index()
        trend.columns = ["mois", "nombre"]
        fig_dig = px.line(trend, x="mois", y="nombre", markers=True,
                          title="Évolution du digital au Bénin")
        fig_dig.update_layout(template=TEMPLATE, height=380)
        st.plotly_chart(fig_dig, use_container_width=True)
    else:
        st.info("Pas assez de données filtrées pour le digital.")

    # Tourisme
    st.markdown("### Émergence Touristique")
    kw_tourism = ['tourism','tourisme','travel','voyage','ouidah','pendjari',
                   'park','par national','heritage','patrimoine','unesco',
                   'culture','festival','beach','plage','destination','hotel']
    pat_tourism = re.compile('|'.join(kw_tourism), flags=re.IGNORECASE)
    mask_t = df_f["SOURCEURL"].str.contains(pat_tourism, na=False) | df_f["Actor1Name"].str.contains(pat_tourism, na=False)
    df_tourism = df_f[mask_t].copy()
    c1, c2 = st.columns(2)
    c1.metric("Articles tourisme", f"{len(df_tourism):,}")
    if len(df_tourism) > 0:
        barometre = df_tourism["AvgTone"].mean()
        c2.metric("Baromètre Attractivité", f"{barometre:.2f}")
        tour_geo = df_tourism.dropna(subset=["ActionGeo_Lat","ActionGeo_Long"])
        if len(tour_geo) > 0:
            fig_map = px.scatter_mapbox(tour_geo, lat="ActionGeo_Lat", lon="ActionGeo_Long",
                                       color="AvgTone", size="NumArticles",
                                       hover_data=["ActionGeo_FullName","SOURCEURL"],
                                       color_continuous_scale="RdYlGn",
                                       zoom=5, center={"lat":9.5,"lon":2.3},
                                       title="Carte des mentions touristiques au Bénin")
            fig_map.update_layout(mapbox_style="carto-positron", height=500, template=TEMPLATE)
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("Aucune donnée géolocalisée pour le tourisme.")
    else:
        st.info("Aucun article touristique détecté.")

# ──────────────────────────────────────────────
# CYBER-VIGILANCE
# ──────────────────────────────────────────────
elif galerie == "Cyber-Vigilance":
    st.title("🛡️ Cyber-Vigilance & Désinformation")

    kw_cyber = ['désinformation','fake news','cybersécurité','cyberattack','deepfake',
                 'hacker','propaganda','misinformation','rumeur','menace','attaque',
                 'fraud','arnaque','bot']
    pat_cyber = re.compile('|'.join(kw_cyber), flags=re.IGNORECASE)
    mask_c = df_f["SOURCEURL"].str.contains(pat_cyber, na=False)
    df_cyber = df_f[mask_c].copy()

    c1, c2, c3 = st.columns(3)
    c1.metric("Articles cyber", f"{len(df_cyber):,}")
    if len(df_cyber) > 0:
        c2.metric("AvgTone cyber", f"{df_cyber['AvgTone'].mean():.2f}")
        c3.metric("Sources distinctes", f"{df_cyber['domain'].nunique()}")

        df_cyber["mois_c"] = df_cyber["date"].dt.to_period("M").astype(str)
        cyber_trend = df_cyber.groupby("mois_c").agg(
            events=("GLOBALEVENTID","nunique"),
            avg_tone=("AvgTone","mean"),
        ).reset_index()

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            subplot_titles=("Volume d'articles cyber", "Tonalité moyenne"))
        fig.add_trace(go.Bar(x=cyber_trend["mois_c"], y=cyber_trend["events"],
                              name="Articles", marker_color="crimson"), row=1, col=1)
        fig.add_trace(go.Scatter(x=cyber_trend["mois_c"], y=cyber_trend["avg_tone"],
                                 mode="lines+markers", name="AvgTone", line=dict(color="darkred")), row=2, col=1)
        fig.update_layout(title="Radar de Cyber-Vigilance", template=TEMPLATE, height=550, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        # Pics négatifs
        st.markdown("### Signaux de risque réputationnel")
        neg_thresh = df_f["AvgTone"].quantile(0.10)
        df_neg = df_f[df_f["AvgTone"] <= neg_thresh]
        st.metric("Seuil négatif (10e percentile)", f"{neg_thresh:.2f}")
        st.metric("Événements sous le seuil", f"{len(df_neg):,}")

        if len(df_neg) > 0:
            neg_m = df_neg.groupby("mois").agg(
                count=("GLOBALEVENTID","nunique"), avg_tone=("AvgTone","mean")
            ).reset_index()
            fig_neg = px.bar(neg_m, x="mois", y="count", title="Événements les plus négatifs (bottom 10%)",
                             color="avg_tone", color_continuous_scale="Reds")
            fig_neg.update_layout(template=TEMPLATE, height=400)
            st.plotly_chart(fig_neg, use_container_width=True)
    else:
        st.info("Aucun article détecté avec les mots-clés cyber-vigilance.")

# PIED DE PAGE
st.markdown("---")
st.markdown(
    '<p style="text-align:center; color:#888; font-size:12px;">'
    "🇧🇯 Bénin Insight Challenge 2026 — Équipe 6 | Données : GDELT Project | Dashboard v2.0"
    "</p>", unsafe_allow_html=True
)
