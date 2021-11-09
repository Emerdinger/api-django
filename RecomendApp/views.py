from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse

# Imports to recommendations
import numpy as np
import nltk
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import ast
import pandas as pd
import json

ps = PorterStemmer()
cv = CountVectorizer(max_features = 5000, stop_words='english')
recetas = pd.read_csv('./RecomendApp/recetas.csv')
recetas = recetas[['_id', 'nombre', 'calorias', 'carbohidratos', 'categoria', 'grasa', 'proteina', 'tiempoPreparacion', 'ingredientes']]

def convert(obj):
    L = []
    for i in ast.literal_eval(obj):
        L.append(i['idIngrediente'])
    return L

def convert2(obj):
    L = []
    for i in json.loads(obj):
        if i['vegetarian'] == "true":
            L.append('vegetarian')
        else:
            L.append('novegetarian')

        if i['vegan'] == "true":
            L.append('vegan')
        else:
            L.append('novegan')

        if i['glutenFree'] == "true":
            L.append('glutenfree')
        else:
            L.append('noglutenfree')

        if i['dairyFree'] == "true":
            L.append('dairyfree')
        else:
            L.append('nodairyfree')

        if i['veryHealthy'] == "true":
            L.append('veryHealthy')
        else:
            L.append('noveryHealthy')

    return L

def convert3(obj):
    L = []
    L.append(str(obj))
    return L

def stem(text):
    y = []

    for i in text.split():
        y.append(ps.stem(i))
    return " ".join(y)

def recommend(receta):
    recomend = []
    receta = int(receta)
    receta_index = new_df[new_df['_id'] == receta].index[0]
    distances = similarity[receta_index]
    recetas_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    for i in recetas_list:
        recomend.append(recetas.iloc[i[0]]._id)

    return recomend

recetas['ingredientes'] = recetas['ingredientes'].apply(convert)
recetas['categoria'] = recetas['categoria'].apply(convert2)

recetas['categoria'] = recetas['categoria'].apply(lambda x:[i.replace(" ","") for i in x])
recetas['ingredientes'] = recetas['ingredientes'].apply(lambda x:[i.replace(" ","") for i in x])

recetas['calorias'] = recetas['calorias'].apply(convert3)
recetas['carbohidratos'] = recetas['carbohidratos'].apply(convert3)
recetas['grasa'] = recetas['grasa'].apply(convert3)
recetas['proteina'] = recetas['proteina'].apply(convert3)
recetas['tiempoPreparacion'] = recetas['tiempoPreparacion'].apply(convert3)

recetas['tags'] = recetas['calorias'] + recetas['carbohidratos'] + recetas['grasa'] + recetas['proteina'] + recetas['tiempoPreparacion'] + recetas['ingredientes'] + recetas['categoria']
new_df = recetas[['_id', 'nombre', 'tags']]
new_df['tags'] = new_df['tags'].apply(lambda x:" ".join(x))
new_df['tags'] = new_df['tags'].apply(lambda x:x.lower())
new_df['tags'] = new_df['tags'].apply(stem)

vectors = cv.fit_transform(new_df['tags']).toarray()
similarity = cosine_similarity(vectors)

# Create your views here.

@csrf_exempt
def recomendarApi(request, title):
    if request.method=='GET':
        recomendacion = recommend(title)
        response = np.array(recomendacion, dtype=np.int32)
        return JsonResponse({"response": response.tolist()}, safe=False)

@csrf_exempt
def recomendarHistorialApi(request,historial):
    if request.method=='GET':
        x = historial.split(',')
        y = []
        for i in x:
            recommendation = recommend(i)
            for j in recommendation:
                y.append(j)

        response = np.array(y, dtype=np.int32)
        return JsonResponse({"recomend": response.tolist()},safe=False)