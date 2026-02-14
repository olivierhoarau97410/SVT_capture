import streamlit as st
import random
import pandas as pd

# Configuration de la page
st.set_page_config(page_title="Simulateur CMR - Capture-Marquage-Recapture", layout="centered")

# --- CSS POUR ANIMATIONS CLIGNOTANTES ---
st.markdown("""
<style>
@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

.blink-box {
    animation: blink 1.5s ease-in-out infinite;
    padding: 20px;
    border-radius: 10px;
    border: 3px solid;
    font-size: 1.3em;
    font-weight: bold;
    margin: 20px 0;
    text-align: center;
}

.blink-success {
    background-color: #d4edda;
    border-color: #28a745;
    color: #155724;
}

.blink-warning {
    background-color: #fff3cd;
    border-color: #ffc107;
    color: #856404;
}

.blink-info {
    background-color: #d1ecf1;
    border-color: #17a2b8;
    color: #0c5460;
}

.blink-error {
    background-color: #f8d7da;
    border-color: #dc3545;
    color: #721c24;
}
</style>
""", unsafe_allow_html=True)

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
st.title("🐟 Simulateur Capture-Marquage-Recapture (CMR)")

# INTRODUCTION GÉNÉRALE
st.info("""
**Principe de la méthode CMR** : Pour estimer une population **N** inconnue, on capture et marque **M** individus, 
puis lors d'une seconde capture de **n** individus, on compte **m** individus marqués. 
Si les marqués se répartissent uniformément, alors **p = M/N = m/n**, d'où **N ≈ (M × n) / m**.
""")

st.divider()

module = st.sidebar.radio("Choisir le mode", ["Module 1 (N connu)", "Module 2 (N inconnu)"])

# ---------------------------------------------------------
# MODULE 1 : N CONNU
# ---------------------------------------------------------
if module == "Module 1 (N connu)":
    st.header("Module 1 : Fluctuations et Probabilités")
    
    if st.session_state.etape == "reglage":
        N_init = st.number_input("Population totale (N)", min_value=1000, max_value=50000, value=10000, step=1000)
        st.caption(f"Population choisie : **{N_init:,}** poissons".replace(',', ' '))
        if st.button("Lancer la simulation"):
            generer_population(N_init)
            st.rerun()

    if st.session_state.etape in ["marquage", "recapture"]:
        N_reel = len(st.session_state.poissons)
        
        # Limite progressive : 10% au début, 20% si l'élève a déjà fait une tentative
        if st.session_state.M == 0:
            # Premier essai : limite stricte à 10%
            max_marquage = int(N_reel * 0.10)
            message_limite = "première tentative"
        else:
            # Deuxième essai et + : le boss lâche du lest, 20%
            max_marquage = int(N_reel * 0.20)
            message_limite = "deuxième tentative (le boss est plus cool maintenant)"
        
        # --- ÉTAPE 1 : MARQUAGE ---
        st.subheader("**Étape 1 : Capture et Marquage**")
        col1, col2 = st.columns([1, 1.5])
        with col1:
            nb_a_marquer = st.number_input("Nombre à marquer (M)", value=min(100, max_marquage), key="m1_M", step=10)
            
            # Vérification de la contrainte budgétaire
            if nb_a_marquer > max_marquage:
                if st.session_state.M == 0:
                    # Message strict pour le 1er essai
                    st.error(f"""
### 🤵 MESSAGE DU BOSS :

"Hé ! Tu sais combien ça coûte de marquer **{nb_a_marquer}** poissons ?! 💸💸💸

On n'a pas le budget pour ça ! Le marquage, c'est du temps, des équipes, des bateaux...

**Maximum autorisé : {max_marquage} poissons (10% de la population)**

Fais un premier essai avec ça, et reviens me voir si à la fin, c'est pas assez !"
""")
                else:
                    # Message plus cool pour le 2ème essai
                    st.warning(f"""
### 🤵 MESSAGE DU BOSS :

"OK, je vois que tu galères... Bon, je vais être sympa. 😊

Cette fois, je t'autorise **jusqu'à {max_marquage} poissons (20% de la population)**.

Mais pas plus hein ! Le budget a des limites quand même..."
""")
            else:
                if st.button("🎣 Lancer le marquage", key="btn_m1_M"):
                    marquer_poissons(nb_a_marquer)
        with col2:
            if N_reel > 0 and st.session_state.M > 0:
                p_theorique = st.session_state.M / N_reel
                st.info(f"""
**Nombre marqué = M = {st.session_state.M}**

Soit la probabilité qu'un poisson soit marqué :
**p = M / N = {p_theorique:.4f}**

avec marqués M = {st.session_state.M} et population totale N = {N_reel:,}

_Mais pour N, seul nous le savons_ 🤫
""".replace(',', ' '))

        # Visualisation du lagon (avec GROS POINTS)
        if not st.session_state.df_lagon.empty:
            st.session_state.df_lagon['Statut'] = ['Marqué' if p['marque'] else 'Non marqué' for p in st.session_state.poissons]
            st.write("### 🌊 Vue générale du lagon")
            st.scatter_chart(st.session_state.df_lagon, x='x', y='y', color='Statut', height=300, size=15)

        # --- ÉTAPE 2 : RECAPTURE ---
        if st.session_state.M > 0:
            st.divider()
            st.subheader("**Étape 2 : Recapture et Estimation**")
            
            # Limite progressive : 10% au début, 20% si l'élève a déjà fait une tentative
            if st.session_state.n == 0:
                # Premier essai de recapture : limite stricte à 10%
                max_recapture = int(N_reel * 0.10)
            else:
                # Deuxième essai et + : le boss lâche du lest, 20%
                max_recapture = int(N_reel * 0.20)
            
            nb_recap = st.number_input("Taille de la recapture (n)", value=min(100, max_recapture), key="m1_n", step=10)
            
            # Vérification de la contrainte budgétaire
            if nb_recap > max_recapture:
                if st.session_state.n == 0:
                    # Message strict pour le 1er essai
                    st.error(f"""
### 🤵 MESSAGE DU BOSS (encore lui !) :

"Déjà pour le marquage, vous y alliez fort les amis... 😤

Et maintenant tu veux recapturer **{nb_recap}** poissons ?! On va ruiner l'entreprise !

**Maximum autorisé : {max_recapture} poissons (10% de la population)**

Tente avec ça et on voit, OK ? Si c'est pas assez précis, on avisera..."
""")
                else:
                    # Message plus cool pour le 2ème essai
                    st.warning(f"""
### 🤵 MESSAGE DU BOSS :

"Bon OK, je vois que c'était pas assez... 🤝

Allez, cette fois je t'autorise **jusqu'à {max_recapture} poissons (20% de la population)**.

Mais c'est vraiment le max du max, compris ?!"
""")
            else:
                if st.button("🕸️ Lancer la recapture", key="btn_m1_n"):
                    recapturer(nb_recap)
                    st.session_state.etape = "recapture"
                    st.rerun()

            if st.session_state.etape == "recapture":
                if not st.session_state.df_filet.empty:
                    st.write("### 🕸️ Contenu de votre filet (échantillon n)")
                    st.scatter_chart(st.session_state.df_filet, x='x', y='y', color='Statut', height=200, size=25)
                    
                    # Affichage des résultats
                    col_a, col_b = st.columns([1, 1.5])
                    
                    with col_a:
                        st.metric("Nombre de recapturés (n)", st.session_state.n)
                        st.metric("Recapturés marqués (m)", st.session_state.m)
                    
                    with col_b:
                        if st.session_state.n > 0:
                            p_prime = st.session_state.m / st.session_state.n if st.session_state.m > 0 else 0
                            st.info(f"""
**Et donc la probabilité de marquage ici est :**

**p' = m / n = {p_prime:.4f}**

avec m = {st.session_state.m}, n = {st.session_state.n}
""")
                    
                    # ESTIMATION DE N
                    if st.session_state.m > 0:
                        N_est = (st.session_state.M * st.session_state.n) / st.session_state.m
                        st.success(f"""
### 🎯 Estimation : N ≈ **{int(N_est):,}**

**Car p = p'**, donc **M/N = m/n**, donc **N = (M × n) / m** 🤓
""".replace(',', ' '))
                        
                        # Calcul de l'écart
                        ecart = abs(int(N_est) - N_reel)
                        pourcentage_ecart = (ecart / N_reel) * 100
                        
                        # CAS 1 : Estimation proche (±5%)
                        if pourcentage_ecart <= 5:
                            st.balloons()
                            st.success(f"""
### 🏆 C'est excellent !

**Votre estimation : {int(N_est):,}**  
**Population réelle : {N_reel:,}**  
**Écart : {ecart:,} poissons ({pourcentage_ecart:.1f}%)**

Vous avez fait un excellent travail ! Votre estimation est très proche de la réalité.
La méthode CMR fonctionne bien quand on respecte les hypothèses (mélange uniforme, pas de mortalité...).
""".replace(',', ' '))
                            
                            # Message clignotant de félicitations
                            st.markdown("""
<div class="blink-box blink-success">
    ✨ BRAVO ! Estimation très précise ! ✨
</div>
""", unsafe_allow_html=True)
                        
                        # CAS 2 : Surestimation (N_est > N_reel et écart > 5%)
                        elif int(N_est) > N_reel:
                            st.warning(f"""
### 📊 On a un problème... Surestimation !

**Votre estimation : {int(N_est):,}**  
**Population réelle : {N_reel:,}**  
**Écart : +{ecart:,} poissons (+{pourcentage_ecart:.1f}%)**

Vous **surestimez** la population. D'où ça peut venir ?

🤔 **Causes possibles :**
- **Problème d'échantillonnage** : Votre recapture n'était peut-être pas aléatoire
- **m trop faible** : Vous avez recapturé trop peu de poissons marqués par hasard
- **Les marqués ne se sont pas bien mélangés** à la population
""".replace(',', ' '))
                            
                            # Message clignotant d'action
                            st.markdown("""
<div class="blink-box blink-warning">
    💡 SOLUTION : Recommencez avec un M plus grand ou un n plus grand pour réduire l'incertitude !
</div>
""", unsafe_allow_html=True)
                        
                        # CAS 3 : Sous-estimation (N_est < N_reel et écart > 5%)
                        else:
                            st.info(f"""
### 📉 Sous-estimation de la population

**Votre estimation : {int(N_est):,}**  
**Population réelle : {N_reel:,}**  
**Écart : -{ecart:,} poissons (-{pourcentage_ecart:.1f}%)**

Vous **sous-estimez** la population.

🤔 **Causes possibles :**
- **M trop faible** : Vous n'avez pas marqué assez de poissons au départ
- **m trop élevé par hasard** : Vous avez recapturé "trop" de marqués par chance
- **Échantillonnage biaisé** : Les poissons marqués étaient plus faciles à recapturer
""".replace(',', ' '))
                            
                            # Message clignotant d'action
                            st.markdown("""
<div class="blink-box blink-info">
    💡 SOLUTION : Retournez marquer PLUS de poissons (augmenter M) et/ou recapturez PLUS (augmenter n) !
</div>
""", unsafe_allow_html=True)
                    
                    else:
                        # CAS m = 0
                        st.error("""
### 🤔 Que se passe-t-il ? 

**Vous n'avez recapturé AUCUN poisson marqué (m = 0) !**

Cela peut arriver si :
- Vous n'avez pas marqué **assez** de poissons à l'étape 1
- Votre échantillon de recapture est trop petit
""")
                        
                        # Message clignotant d'urgence
                        st.markdown("""
<div class="blink-box blink-error">
    ⚠️ IMPOSSIBLE DE CALCULER N ! Retournez à l'étape 1 et marquez DAVANTAGE de poissons, puis recapturez-en PLUS !
</div>
""", unsafe_allow_html=True)

    if st.sidebar.button("🔄 Réinitialiser le module"):
        for key in list(st.session_state.keys()): 
            del st.session_state[key]
        st.rerun()

# ---------------------------------------------------------
# MODULE 2 : N INCONNU
# ---------------------------------------------------------
if module == "Module 2 (N inconnu)":
    st.header("Module 2 : Mode Scientifique (N caché)")
    
    if st.session_state.etape == "reglage":
        st.write("Le système va générer une population de poissons entre **500 et 3000**. À vous de trouver N !")
        if st.button("🎲 Générer la population mystère"):
            generer_population(random.randint(500, 3000))
            st.rerun()

    if st.session_state.etape in ["marquage", "recapture"]:
        N_reel = len(st.session_state.poissons)
        
        # Limite progressive : 10% au début, 20% si l'élève a déjà marqué
        if st.session_state.M == 0:
            max_marquage = int(N_reel * 0.10)
        else:
            max_marquage = int(N_reel * 0.20)
        
        # --- ÉTAPE 1 : MARQUAGE (N caché) ---
        st.subheader("**Étape 1 : Capture et Marquage**")
        col1, col2 = st.columns([1, 1.5])
        with col1:
            nb_m2 = st.number_input("Nombre à marquer (M)", value=100, key="m2_M", step=10)
            
            # Vérification de la contrainte budgétaire (sans révéler N)
            if nb_m2 > max_marquage:
                if st.session_state.M == 0:
                    st.error(f"""
### 🤵 MESSAGE DU BOSS :

"Stop ! Tu veux marquer **{nb_m2}** poissons ?! 💸💸💸

Le budget est limité ! On ne peut pas se permettre de marquer autant...

**Conseil du boss** : Commence avec **{max_marquage} poissons maximum**, 
fais ton estimation, et reviens me voir si c'est pas assez précis !"
""")
                else:
                    st.warning(f"""
### 🤵 MESSAGE DU BOSS :

"Bon, je vois que ton estimation était pas terrible... OK. 😊

Je te laisse marquer **jusqu'à {max_marquage} poissons cette fois**.

Mais après, faudra faire avec hein !"
""")
            else:
                if st.button("🎣 Marquer et relâcher", key="btn_m2_M"):
                    marquer_poissons(nb_m2)
        with col2:
            st.metric("Poissons marqués (M)", st.session_state.M)
            st.caption("⚠️ Vous ne connaissez pas N, donc **p = M/N est inconnu**.")

        # --- ÉTAPE 2 : RECAPTURE ---
        if st.session_state.M > 0:
            st.divider()
            st.subheader("**Étape 2 : Recapture et Estimation**")
            
            # Limite progressive : 10% au début, 20% si l'élève a déjà fait une recapture
            if st.session_state.n == 0:
                max_recapture = int(N_reel * 0.10)
            else:
                max_recapture = int(N_reel * 0.20)
            
            n_m2 = st.number_input("Taille de la recapture (n)", value=100, key="m2_n", step=10)
            
            # Vérification de la contrainte budgétaire
            if n_m2 > max_recapture:
                if st.session_state.n == 0:
                    st.error(f"""
### 🤵 MESSAGE DU BOSS :

"Encore toi ! Écoute, déjà pour le marquage, c'était limite niveau budget... 😤

Et là tu veux recapturer **{n_m2}** poissons ?! Non mais allô quoi !

**Maximum autorisé : {max_recapture} poissons**

Fais avec ça, et si ton estimation est pourrie, on en reparle..."
""")
                else:
                    st.warning(f"""
### 🤵 MESSAGE DU BOSS :

"Bon... Je sens que tu vas encore me demander plus, pas vrai ? 😏

Allez, tiens : **{max_recapture} poissons maxi**.

Mais c'est VRAIMENT le dernier effort budget que je peux faire !"
""")
            else:
                if st.button("🕸️ Lancer le filet", key="btn_m2_n"):
                    recapturer(n_m2)
                    st.session_state.etape = "recapture"
                    st.rerun()

            if st.session_state.etape == "recapture":
                if not st.session_state.df_filet.empty:
                    st.write("### 🕸️ Contenu de votre filet")
                    st.scatter_chart(st.session_state.df_filet, x='x', y='y', color='Statut', height=200, size=25)
                    
                    col_a, col_b = st.columns([1, 1.5])
                    
                    with col_a:
                        st.metric("Nombre de recapturés (n)", st.session_state.n)
                        st.metric("Recapturés marqués (m)", st.session_state.m)
                    
                    with col_b:
                        if st.session_state.n > 0:
                            p_prime = st.session_state.m / st.session_state.n if st.session_state.m > 0 else 0
                            st.info(f"""
**Probabilité de marquage observée :**

**p' = m / n = {p_prime:.4f}**

avec m = {st.session_state.m}, n = {st.session_state.n}
""")
                    
                    # ESTIMATION DE N
                    if st.session_state.m > 0:
                        N_est = (st.session_state.M * st.session_state.n) / st.session_state.m
                        st.success(f"""
### 🎯 Votre estimation : N ≈ **{int(N_est):,}**

**Car p = p'**, donc **M/N = m/n**, donc **N = (M × n) / m** 🤓
""".replace(',', ' '))
                        
                        # RÉVÉLATION DE LA VRAIE VALEUR
                        if st.checkbox("🔓 Révéler la population réelle (N)"):
                            N_vrai = len(st.session_state.poissons)
                            ecart = abs(int(N_est) - N_vrai)
                            pourcentage_ecart = (ecart / N_vrai) * 100
                            
                            st.warning(f"""
### 🎉 Révélation !

La population réelle était de **{N_vrai:,}** poissons.

**Écart** : {ecart:,} individus ({pourcentage_ecart:.1f}%)
""".replace(',', ' '))
                            
                            if pourcentage_ecart < 10:
                                st.success("🏆 **Excellent !** Votre estimation est très proche de la réalité !")
                            elif pourcentage_ecart < 25:
                                st.info("👍 **Bien joué !** Estimation correcte.")
                            else:
                                st.warning("📊 **Pas mal**, mais vous pouvez faire mieux en augmentant M ou n.")
                    
                    else:
                        # CAS m = 0
                        st.error("""
### 🤔 Que se passe-t-il ? 

**Vous n'avez recapturé AUCUN poisson marqué (m = 0) !**

Cela peut arriver si :
- Vous n'avez pas marqué **assez** de poissons à l'étape 1
- Votre échantillon de recapture est trop petit
""")
                        
                        # Message clignotant d'urgence
                        st.markdown("""
<div class="blink-box blink-error">
    ⚠️ IMPOSSIBLE DE CALCULER N ! Retournez à l'étape 1 et marquez DAVANTAGE de poissons, puis recapturez-en PLUS !
</div>
""", unsafe_allow_html=True)

    if st.sidebar.button("🔄 Nouvelle mission mystère"):
        for key in list(st.session_state.keys()): 
            del st.session_state[key]
        st.rerun()

# --- FOOTER PÉDAGOGIQUE ---
st.divider()
st.markdown("""
### 📚 Pour aller plus loin

La méthode CMR repose sur l'hypothèse que :
- Les poissons marqués se mélangent uniformément à la population
- Il n'y a pas de mortalité ni de migration entre les deux captures
- Les marques ne tombent pas et sont bien visibles

**Formule clé** : Si **p = M/N** (proportion de marqués) = **p' = m/n** (proportion observée), alors **N = (M × n) / m**
""")
