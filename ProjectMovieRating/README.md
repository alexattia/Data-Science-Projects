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

As we can see in the pictures above, the imdb score is correlated to the number of awards and the gross but not really to the production budget and the number of facebook likes of the casting.  
Obviously, domestic and worlwide gross are highly correlated. However, the more important the production budget, the more important the gross.  
As it is shown in the notebook, the budget is not really correlated to the number of awards.  
What's funny is that the popularity of the third most famous actor is more important for the IMDB score than the popularity of the most famous score (Correlation 0.2 vs 0.08).  
(Many other charts in the Jupyter notebook)

## Third Part - Predict the IMDB score

Machine Learning to predict the IMDB score with the meaningful variables.  
Using a Random Forest algorithm (500 estimators). 
![Most important features](https://github.com/alexattia/Data-Science-Projects/blob/master/pics/features.png)

