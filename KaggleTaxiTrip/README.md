## New York City Taxi Trip Duration

Kaggle playground to predict the total ride duration of taxi trips in New York City. 

### First part - Data exploration
The first part is to analyze the dataframe and observe correlation between variables.
![Distributions](https://github.com/alexattia/Data-Science-Projects/blob/master/KaggleTaxiTrip/pic/download.png)
![Rush Hour](https://github.com/alexattia/Data-Science-Projects/blob/master/KaggleTaxiTrip/pic/rush_hour.png)

### Second part - Clustering
The goal of this playground is to predict the trip duration of test set. We know that some neighborhoods are more congested. So, I used K-Means to compute geo-clusters for pickup and drop off.
![Cluster](https://github.com/alexattia/Data-Science-Projects/blob/master/KaggleTaxiTrip/pic/nyc_clusters.png)

### Third part - Cleaning and feature selection 
I have found some odd long trips : one day trip with a mean spead < 1km/h.   
![Outliners](https://github.com/alexattia/Data-Science-Projects/blob/master/KaggleTaxiTrip/pic/outliners.png)
I have removed these outliners.  

I also added features from the data available : Haversine distance, Manhattan distance, means for clusters, PCA for rotation.

### Forth part - Prediction
I compared Random Forest and XGBoost.  
Current Root Mean Squared Logarithmic error : 0.391