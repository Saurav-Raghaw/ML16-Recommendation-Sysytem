from flask import Flask, render_template, request
import pickle
import numpy as np
from numpy.core.numeric import moveaxis
import pandas as pd
# import urllib library
from urllib.request import urlopen
import os
from numpy import load
# import json
import json

app = Flask(__name__)

api_key = ""   #Your API key

if os.path.isfile('cosine_sim1.npz'):
    print("It is already present in my local repository. Loading...\n\n")
    dict_data = load("cosine_sim1.npz")
    cosine_sim = dict_data['arr_0']
    print("DONE..")
  
# store the response of URL
  
@app.route('/')
@app.route('/home', methods=['POST','GET'])
def man():
    return render_template('home.html')


# #Functions to get movie title from movie index.
# def get_title_from_index(index):
#     return df[df.index == index]["title"].values[0]

# #Functions to get movie index from movie title.
# def get_index_from_title(title):
#     return df[df.title == title]["index"].values[0]

#     #Functions to get movie homepage from movie index.
# def get_homepage_from_index(index):
#     return df[df.index == index]["homepage"].values[0]

# IMBD_Data= pd.read_csv('modified_movies.csv')
df = pd.read_csv("new_movie_dataset.csv")
df2=pd.read_csv('movie_reviews.csv')
print(df.columns)
IMBD_Data=pd.read_csv('modified_movies.csv')
def search_movie(name):
    name=name.lower()
    movie=IMBD_Data.loc[IMBD_Data['titles']==name]
    if len(movie)==0 :
        return 0
    print(movie)
    x=[x for x in movie['movie_id']]
    print(x)
    return x

def load_movie_details(id):
    url = "https://api.themoviedb.org/3/movie/"+str(id)+"?api_key="+api_key
    print(url)
    # store the response of URL
    response = urlopen(url)
    
    # storing the JSON response 
    # from url in data
    data_json = json.loads(response.read())
    rating= data_json['vote_average']
    overview=data_json['overview']
    genre = []
    for i in data_json['genres']:
        genre.append(i['name'])
    img="https://image.tmdb.org/t/p/w500/"+str(data_json['backdrop_path'])
    data={'backdrop_image' :img,'tagline':data_json['tagline'], 'rating':rating, 'overview':overview, 'genre':genre}
    return data

def get_movie_image(id):
    print(id)
    url = "https://api.themoviedb.org/3/movie/"+str(id.values[0])+"?api_key="+api_key
    print(url)
    # store the response of URL
    response = urlopen(url)
    
    # storing the JSON response 
    # from url in data
    data_json = json.loads(response.read())
    img="https://image.tmdb.org/t/p/w500/"+str(data_json['poster_path'])
    return img

def get_cast_details(id):
    url = "https://api.themoviedb.org/3/movie/"+str(id)+"/credits?api_key="+api_key+"&language=en-US"
    # store the response of URL
    response4 = urlopen(url)
    
    # storing the JSON response 
    # from url in data
    data_json = json.loads(response4.read())
    x = data_json['cast']
    c=1
    cast=[]
    for i in x:
        print(i['name'])
        img="https://image.tmdb.org/t/p/w500/"+str(i['profile_path'])
        cast.append({'name':i['name'] , 'known_for':i['known_for_department'], "profile_path":img })
        c+=1
        if c>6:
            break 
    return cast
def get_imdb_id(x):
    url = "https://api.themoviedb.org/3/movie/"+str(x)+"?api_key="+api_key

    # store the response of URL
    response = urlopen(url)

    # storing the JSON response 
    # from url in data
    data_json = json.loads(response.read())
    return data_json['imdb_id']

#Function to get review of movie
def get_review(title):
    id=get_id_from_title(title)
    if id==0:
        return 0
    imdb_id=get_imdb_id(id)
    review=df2[df2['movie_id']==imdb_id]
    if review.shape[0] == 0:
        return 0
    comment=review[['sentence2','label']]
    comments=[]
    comments=[]
    for i,j in zip(comment['sentence2'], comment['label']):
    #     print(i,j)
        comments.append({'review':i, 'label':j})
    return comments

#Functions to get movie title from movie index.
def get_title_from_index(index):
    return df[df.index == index]["title"].values[0]
#Functions to get movie index from movie title.
def get_index_from_title(title):
    return df[df.new_title == title]["index"].values[0]

    #Functions to get movie homepage from movie index.
def get_homepage_from_index(index):
    return df[df.index == index]["homepage"].values[0]

#Functions to get movie id from movie title.
def get_id_from_title(title):
    title=title.title()
    id = df[df.title == title]["id"]
    if(len(id)==0):
        return 0
    return id.values[0]

def get_recommendation(name):
    #getting the movie index
    name=name.title()
    movie_index = get_index_from_title(name)
    similar_movies = list(enumerate(cosine_sim[movie_index]))    
    i=0
    l=[]
    #We will sort the list similar_movies according to similarity scores in descending order. 
    sorted_similar_movies = sorted(similar_movies,key=lambda x:x[1],reverse=True)[1:]
    print("Top 10 similar movies to "+name+" are:\n")
    for element in sorted_similar_movies:
        print(get_title_from_index(element[0]), element[0])
        name=get_title_from_index(element[0])
        name=name.title()
        id=df[df['new_title']==name]['id']
        rating=df[df['new_title']==name]['vote_average'].values[0]
        release_date = df[df['new_title']==name]['release_date'].values[0]
        img=get_movie_image(id)
        l.append({ 'name':name , 'poster':img , 'rating':rating, "release_date":release_date})
        print(get_title_from_index(element[0]))
        i=i+1
        if i>11:
            break
    return l

@app.route('/recommend', methods=['POST'])
def recommend():
    name = request.form['movie_name']
    # name=name.lower()
    name=name.title()
    id=df[df['new_title']==name]['id']
    if(len(id)==0):
        id=0
    else:
        id=id.values[0]
    print(id)
    if(id==0):
        name='not found'
        return render_template('home.html',data=name)
    if request.form['submit_button'] == 'Recommendation':
        movie_details=load_movie_details(id)
        recomd=get_recommendation(name)
        cast=get_cast_details(id)
        data={'name':name , 'recomend':recomd,'cast':cast,'movie_details':movie_details}
        return render_template('recommendation.html', data=data)
    elif request.form['submit_button'] == 'Review':
        review=get_review(name)
        data={'review':review, 'name':name}
        for i in data['review']:
            print(i['label'])
        return render_template('review.html', data=data)
    return render_template('home.html', data=name)


@app.route('/review', methods=['POST'])
def review():
    comment=request.form['comment']
    df=pd.read_csv('custom_review.csv')
    df.drop(['Unnamed: 0'],axis=1,inplace=True)
    df.loc[len(df.index)] = [comment]
    df.to_csv('custom_review.csv')
    print('comment saved successfully')
    return render_template('home.html', data="comment")

if __name__ == "__main__":
    app.run(debug=True)



