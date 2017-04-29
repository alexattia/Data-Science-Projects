# Predict IMDB movie rating

Project inspired by Chuan Sun [work](https://www.kaggle.com/deepmatrix/imdb-5000-movie-dataset) without Scrappy

Main question : How can we tell the greatness of a movie before it is released in cinema?

## First Part - Parsing data

The first part aims to parse data from the imdb and the numbers websites : casting information, directors, production companies, awards, genres, budget, gross, description, imdb_rating, etc.  
To create the movie_contents.json file :  
``python3 parser.py nb_elements``  

## Second Part - Predicting imdb rating

