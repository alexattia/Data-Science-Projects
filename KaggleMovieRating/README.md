# Predict IMDB movie rating

Project inspired by Chuan Sun [work](https://www.kaggle.com/deepmatrix/imdb-5000-movie-dataset) without Scrappy

Main question : How can we tell the greatness of a movie before it is released in cinema?

## First Part - Parsing data

The first part aims to parse data from the imdb and the numbers websites : casting information, directors, production companies, awards, genres, budget, gross, description, imdb_rating, etc.  
To create the movie_contents.json file :  
``python3 parser.py nb_elements``  

## Second Part - Data Analysis

The second part is to analyze the dataframe and observe correlation between variables. For example, are the movie awards correlated to the worlwide gross ? Does the more a movie is a liked, the more the casting is liked ? 
See the jupyter notebook file.  

![Correlation Matrix](https://github.com/alexattia/Data-Science-Projects/blob/master/pics/corr_matrix.png)

## Third Part - Predict the IMDB score

Machine Learning to predict the IMDB score with the meaningful variables

