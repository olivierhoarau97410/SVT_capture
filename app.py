import streamlit as st
import random
import pandas as pd

# Configuration de la page
st.set_page_config(page_title="Simulateur CMR", layout="centered")

# --- INITIALISATION ROBUSTE ---
if 'poissons' not in st.session_state:
    st.session_state.poissons = []
if 'etape' not in st.session_state:
    st.session_state.etape = "reglage"
if 'M' not in st.session_state:
    st.session_state.M = 0
if 'n' not in st.session_state:
    st.session_state.n = 0
if 'm' not in st.session_state:
    st.session_state.m = 0
if 'df_lagon' not in st.session_state:
    st.session_state.df_lagon = pd.DataFrame()
if 'df_filet' not in st.session_state:
    st.session_state.df_filet = pd.DataFrame()

# --- FONCTIONS ---
def generer_population(N):
    st.session_state.poissons = [{'id': i, 'marque': False} for i in range(N)]
    st.session_state.df_lagon = pd.DataFrame({
        'x': [random.random() for _ in range(N)],
        'y': [random.random() for _ in range(N)]
    })
    st.session_state.etape = "marquage"
    st.session_state.M = 0
    st.session_state.m = 0
    st.session_state.df_filet = pd.DataFrame()

def marquer_poissons(quantite):
    non_marques = [p for p in st.session_state.poissons if not p['marque']]
    a_marquer = random.sample(non_marques, min(quantite, len(non_marques)))
    for p in a_marquer:
        p['marque'] = True
    st.session_state.M += len(a_marquer)

def recapturer(quantite):
    indices = random.sample(range(len(st.session_state.poissons)), min(quantite, len(st.session_state.poissons)))
    st.session_state.n = len(indices)
    st.session_state.m = sum(1 for i in indices if st.session_state.poissons[i]['marque'])
    st.session_state.df_filet = pd.DataFrame({
        'x': [random.random() for _ in range(st.session_state.n)],
        'y': [random.random() for _ in range(st.session_state.n)],
        'Statut': ['Marqué' if st.session_state.poissons[i]['marque'] else 'Non marqué' for i in indices]
    })

# --- INTERFACE ---
st.title("🐟 Simulateur Capture-Recapture")

module = st.sidebar.radio("Choisir le mode", ["Module 1 (N connu)", "Module 2 (N inconnu)"])

# ---------------------------------------------------------
# MODULE 1 : N CONNU
# ---------------------------------------------------------
if module == "Module 1 (N connu)":
    st.header("Module 1 : Fluctuations et Probabilités")
    
    if st.session_state.etape == "reglage":
        N_init = st.number_input("Population totale (N)", value=1000, step=100)
        if st.button("Lancer la simulation"):
            generer_population(N_init)
            st.rerun()

    if st.session_state.etape in ["marquage", "recapture"]:
        N_reel = len(st.session_state.poissons)
        st.subheader("1. Marquage (Capture initiale)")
        col1, col2 = st.columns([1, 1.5])
        with col1:
            nb_a_marquer = st.number_input("Nombre à marquer (M)", value=100, key="m1_M")
            if st.button("Lancer le marquage", key="btn_m1_M"):
                marquer_poissons(nb_a_marquer)
        with col2:
            if N_reel > 0:
                p_theorique = st.session_state.M / N_reel
                st.info(f"**p = M / N = {p_theorique:.3f}**\n\nM={st.session_state.M}, N={N_reel}")

        if not st.session_state.df_lagon.empty:
            st.session_state.df_lagon['Statut'] = ['Marqué' if p['marque'] else 'Non marqué' for p in st.session_state.poissons]
            st.write("### 🌊 Vue générale du lagon")
            st.scatter_chart(st.session_state.df_lagon, x='x', y='y', color='Statut', height=300)

        if st.session_state.M > 0:
            st.divider()
            st.subheader("2. Recapture (Échantillonnage)")
            nb_recap = st.number_input("Taille de la recapture (n)", value=50, key="m1_n")
            if st.button("Lancer la recapture", key="btn_m1_n"):
                recapturer(nb_recap)
                st.session_state.etape = "recapture"
                st.rerun()

            if st.session_state.etape == "recapture":
                if not st.session_state.df_filet.empty:
                    st.write("### 🕸️ Contenu de votre filet (échantillon n)")
                    st.scatter_chart(st.session_state.df_filet, x='x', y='y', color='Statut', height=200)
                    f_obs = st.session_state.m / st.session_state.n
                    c1, c2 = st.columns([1, 1.5])
                    c1.metric("Recapturés marqués (m)", st.session_state.m)
                    c2.info(f"**p' = m / n = {f_obs:.3f}**\nm={st.session_state.m}, n={st.session_state.n}")
                    if st.session_state.m > 0:
                        N_est = (st.session_state.M * st.session_state.n) / st.session_state.m
                        st.success(f"### Estimation : N ≈ **{int(N_est)}**")

    if st.sidebar.button("Réinitialiser le module"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

# ---------------------------------------------------------
# MODULE 2 : N INCONNU
# ---------------------------------------------------------
if module == "Module 2 (N inconnu)":
    st.header("Module 2 : Mode Scientifique (N caché)")
    
    if st.session_state.etape == "reglage":
        st.write("Le système va générer une population de poissons entre 500 et 3000. À vous de trouver N !")
        if st.button("Générer la population mystère"):
            generer_population(random.randint(500, 3000))
            st.rerun()

    if st.session_state.etape in ["marquage", "recapture"]:
        # Zone de Marquage (N est caché ici)
        st.subheader("1. Marquage")
        col1, col2 = st.columns([1, 1.5])
        with col1:
            nb_m2 = st.number_input("Nombre à marquer (M)", value=100, key="m2_M")
            if st.button("Marquer et relâcher", key="btn_m2_M"):
                marquer_poissons(nb_m2)
        with col2:
            st.metric("Poissons marqués (M)", st.session_state.M)
            st.caption("Vous ne connaissez pas N, donc p = M/N est inconnu.")

        if st.session_state.M > 0:
            st.divider()
            st.subheader("2. Recapture")
            n_m2 = st.number_input("Taille de la recapture (n)", value=100, key="m2_n")
            if st.button("Lancer le filet", key="btn_m2_n"):
                recapturer(n_m2)
                st.session_state.etape = "recapture"
                st.rerun()

            if st.session_state.etape == "recapture":
                if not st.session_state.df_filet.empty:
                    st.write("### 🕸️ Contenu de votre filet")
                    st.scatter_chart(st.session_state.df_filet, x='x', y='y', color='Statut', height=200)
                    
                    c1, c2 = st.columns(2)
                    c1.metric("Recapturés marqués (m)", st.session_state.m)
                    c2.metric("Total recapturés (n)", st.session_state.n)
                    
                    if st.session_state.m > 0:
                        N_est = (st.session_state.M * st.session_state.n) / st.session_state.m
                        st.success(f"### Votre estimation : N ≈ **{int(N_est)}**")
                        
                        # LE BOUTON FINAL POUR LA RÉVÉLATION
                        if st.checkbox("Révéler la population réelle (N)"):
                            N_vrai = len(st.session_state.poissons)
                            st.warning(f"La population réelle était de **{N_vrai}** poissons.")
                            st.write(f"Écart : {abs(int(N_est) - N_vrai)} individus.")

    if st.sidebar.button("Nouvelle mission mystère"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()