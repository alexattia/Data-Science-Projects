## New York City Taxi Trip Duration

Kaggle playground to predict the total ride duration of taxi trips in New York City. 

### First part - Data exploration
The first part is to analyze the dataframe and observe correlation between variables.
![Distributions](https://github.com/alexattia/Data-Science-Projects/blob/master/KaggleTaxiTrip/pic/download.png)
![Rush Hour](https://github.com/alexattia/Data-Science-Projects/blob/master/KaggleTaxiTrip/pic/rush_hour.png)

### Second part - Cleaning and feature selection 
I have found some odd long trips : one day trip with a mean spead < 1km/h.   
![Outliners](https://github.com/alexattia/Data-Science-Projects/blob/master/KaggleTaxiTrip/pic/outliners.png)
I have removed these outliners.  

I also added two features from the data available : Haversine distance and Manhattan distance.

### Third part - Prediction
I am currently using a Random Forest.  
Current Root Mean Squared Logarithmic error : 0.45