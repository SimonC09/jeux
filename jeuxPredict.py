### LES IMPORTS ###

from sklearn.neighbors import NearestNeighbors # Voisin proche (?)
import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from st_clickable_images import clickable_images


# Les session_state
if 'Id' not in st.session_state:
    st.session_state['Id']=""



### LES DATAFRAMES ###
jeuxPredict = pd.read_csv('jeuxPredict.csv')

### LES FONCTION ###

# Prediction
def predict(index):
    
    X = jeuxPredict["Tags"] + " " + jeuxPredict["lemAbout"]

    # Applique un TfidfVectorizer

    tfidf = TfidfVectorizer()
    X_tfidf = tfidf.fit_transform(X)

    # et entraine des modèles de classification.

    modelJeu = NearestNeighbors(n_neighbors=3)
    modelJeu.fit(X_tfidf)

    jeu = X_tfidf[index]

    dist, ind = modelJeu.kneighbors(jeu, n_neighbors = 10)
    return ind

# Fonction affichage des jeux recommandés
def affiche(listJeux):
    row1 , row2, row3, row4, row5= st.columns(2), st.columns(2),st.columns(2),st.columns(2),st.columns(2)
    for i, col in zip(range (len(listJeux[0])-1), row1 + row2 + row3 + row4 + row5):
        with col.container():
            col1, col2 = st.columns(2)
            # Utilisez directement la clé de lisTitreFilm au lieu de listTconstFilm[i]
            jeu = jeuxPredict.iloc[listJeux[0][i+1]]
            with col1:
                st.subheader(f"{jeu['Name']}")
                Url = jeu['Header image']#.iloc[0]
                if pd.isna(Url) :
                    st.image('https://i.ibb.co/2568XWc/notFound.png', use_column_width=True)
                else:
                    st.image(Url, use_column_width=True)
            with col2:
                st.write(f"Date de sortie : {jeu['Release date']}")
                st.write(f"Prix : {int(jeu['Price'])}$")
                st.write(f"Estimation des revenus : {int(jeu['estimation_moyenne_revenu'])}") 
                st.write(f"Estimation du nombre de joueurs : {int(jeu['estimation_moyenne_joueurs'])}")


###################################################################################################################
################################# CONTENU DU STREAMLIT ############################################################
###################################################################################################################
                

st.title("SYSTEME DE RECOMMANDATION DE JEUX")
st.header('parfait, infaillible et fantastique !')
st.header('(ou presque)')

col1, col2 = st.columns(2)
Idtest = []
# Verification qu'on trouve bien le film dans la table 
with st.sidebar:
    if len(Idtest)==0:
        nomJeu = st.selectbox('Veuillez entrer le jeu recherché : ', jeuxPredict['Name'], index = None, placeholder="Choose an option")
        Idtest = jeuxPredict[jeuxPredict['Name'] == nomJeu]['AppID']
    if len(Idtest)==1:
        Id = jeuxPredict[jeuxPredict['Name'] == nomJeu]['AppID'].values[0]
        Index = jeuxPredict[jeuxPredict['Name'] == nomJeu].index[0]
        Url = jeuxPredict[jeuxPredict['AppID'] == Id]['Header image'].iloc[0]
        if pd.isna(Url) :
            st.image('https://i.ibb.co/2568XWc/notFound.png', use_column_width=True)
        else:
            st.image(Url, use_column_width=True)

# Verification que le titre correspond bien à un unique film

if len(Idtest)==1:
    listJeux = predict(Index)
    st.subheader(f"Voici des jeux dont la thematique est proche de {nomJeu} : ")
    affiche(listJeux)
elif len(Idtest) > 1:
    if st.session_state['Id'] =="":
        st.write(f"il semblerais qu'il y a plusieurs jeux correspondant à votre recherche dans la base")
        st.write(f"Voici les differents jeux répondants au nom de {nomJeu}")
        listJeuxHomo = list(Idtest)
        dicoHomo = {}
        for i in range(len(listJeuxHomo)):
            titre = jeuxPredict[jeuxPredict['AppID']==listJeuxHomo[i]]['Name'].iloc[0]
            dicoHomo[listJeuxHomo[i]] = titre
        listHomo = []
        # Recuperation et disposition des images de films
        for i in range(len(dicoHomo)):
            cle = list(dicoHomo.keys())[i]
            url = jeuxPredict[jeuxPredict['AppID'] == cle]["Header image"].iloc[0]
            if pd.isna(url) :
                urlPoster = 'https://i.ibb.co/2568XWc/notFound.png'
            else:
                urlPoster = url
            
            listHomo.append(urlPoster)
        # Tentative d'affichage d'image cliquable
        clicked = clickable_images(listHomo,
        titles=[f"Image #{str(i)}" for i in range(4)],    
        div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"},
        img_style={"margin": "5px", "height": "300px"},
        )
        if clicked > -1:
            st.session_state['Id'] = list(dicoHomo.keys())[clicked]
            st.rerun()


    elif st.session_state['Id'] != "":
        index = jeuxPredict[jeuxPredict['AppID'] == st.session_state['Id']].index[0]
        listFilm = predict(index)
        st.subheader(f"Voici des jeux dont la thematique est proche de {nomJeu} : ")
        affiche(listFilm)
        st.session_state['Id'] = ""
