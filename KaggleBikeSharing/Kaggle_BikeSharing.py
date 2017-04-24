## coding: utf8
## Kaggle Challenge
## Utilisation de Python 3.5

## Chargement des bibliothèques
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import collections
import sklearn
from sklearn import linear_model
from sklearn import svm
from sklearn import learning_curve
from sklearn import ensemble
#%matplotlib inline

## Chargement de la base de données
df= pd.read_csv('data.csv')

## Transformation de la date sous 
## format string au format de date
df['date']=pd.to_datetime(df['datetime'])

## Extraction du mois, de l'heure et 
## du jour de la semaine 
df.set_index('date', inplace=True)
df['month']=df.index.month
df['hours']=df.index.hour
df['dayOfWeek']=df.index.weekday

################### 
################### Influence du temps 
################### 

## Création d'une classe pour tracer
## la moyenne du nombre de locations 
## de velos heure par heure pour les 
## jours ouvrés ou non

class mean_30():
    def __init__(self, df):
        self.df=df
    def mean_hours_min(self,h):
        a = self.df["hours"] == h
        return self.df[a]["count"].mean() 
    def transf(self, t):
        return self.mean_hours_min(t)
    def transfc(self, t):
        return self.err_hours_min(t)
    def vector_day(self):
        k = []
        for i in range(0,24):
            k.append(i)
        hour_day = pd.DataFrame()
        hour_day["A"] = k
        return hour_day["A"] 
    def view(self):
        plt.plot(self.vector_day().apply(self.transf))

## Tracer des graphes

fig=plt.figure()
fig.suptitle('Location de velo selon l\'heure, jours ouvrables ou non', fontsize=13)
plt.ylabel('nombre de locations de vélos')
plt.xlabel('heure de la journée')
moy0=mean_30(df[df['workingday']==0])
moy0.view()
moy1=mean_30(df[df['workingday']==1])
moy1.view()
plt.legend(['0','1'])
plt.show()

## Création d'une classe pour tracer
## la deviation standard du nombre de
## locations  de velos heure par heure 
## pour un jour

## Changer cette valeur entre 0 et 6 pour
## pour obtenir un autre jour de la
## semaine

j=0

class std_30():
    def __init__(self, df):
        self.df=df
    def mean_hours_std(self,j,h):
        y = self.df[self.df["dayOfWeek"]==j]["hours"] == h
        return self.df[self.df["dayOfWeek"]==j][y]["count"].mean()
    def err_hours(self,j,h):
        y = self.df[self.df["dayOfWeek"]==j]["hours"] == h
        return self.df[self.df["dayOfWeek"]==j][y]["count"].std()
    def transf_err(self,t):
        return self.mean_hours_std(j,t)
    def transf_err2(self,t):
        return self.err_hours(j,t)
    def vector_day(self):
        k = []
        for i in range(0,24):
            k.append(i)
        hour_std = pd.DataFrame()
        hour_std["A"] = k
        return hour_std["A"] 
    def view(self):
        errors=self.vector_day().apply(self.transf_err2)
        fig, ax = plt.subplots()
        self.vector_day().apply(self.transf_err).plot(yerr=errors, ax=ax,label=str(j))
        plt.legend('0',loc=2,prop={'size':9})

fig.suptitle('Deviation standard des locations de velo selon l\'heure', fontsize=13)
std0=std_30(df)
std0.view()
plt.ylabel('nombre de locations de vélos')
plt.xlabel('heure de la journée')
plt.show()

################### 
################### Influence du mois
################### 

## Création d'une classe pour tracer
## la moyenne du nombre de locations 
## de velos par mois

class month_30():
    def __init__(self, df):
        self.df=df
    def mean_hours_min(self,m):
        a = self.df["month"] == m
        return self.df[a]["count"].mean() 
    def transf(self, t):
        return self.mean_hours_min(t)
    def transfc(self, t):
        return self.err_hours_min(t)
    def vector_day(self):
        k = []
        for i in range(0,13):
            k.append(i)
        hour_day = pd.DataFrame()
        hour_day["A"] = k
        return hour_day["A"] 
    def view(self):
        plt.plot(self.vector_day().apply(self.transf))

## Tracer des graphes

fig=plt.figure()
fig.suptitle('Location de velo selon le mois', fontsize=13)
moy0=month_30(df)
moy0.view()
plt.ylabel('nombre de locations de vélos')
plt.xlabel('mois de l\' année')
plt.show()

################### 
################### Influence de la météo 
################### 
plt.figure()

## Moyenne de la demande en vélos
## Pour les 4 conditions grâce
## à un dictionnaire Python

a={u'Degage/nuageux':df[df['weather']==1]['count'].mean(), 
     u'Brouillard': df[df['weather']==2]['count'].mean(), 
     u'Legere pluie':df[df['weather']==3]['count'].mean()
    }

width = 1/1.6
plt.bar(range(len(a)), a.values(),width,color="blue",align='center')
plt.xticks(range(len(a)), a.keys())
plt.ylabel('nombre de locations de vélos')
plt.title('Moyenne des locations de velos pour differentes conditions meteorologiques')
plt.show()

################### 
################### Influence du vent, de la température et de l'humidité
################### 

## Moyenne de la demande en vélos
## Pour certains paramètres grâce
## à un dictionnaire Python

D = {u'V>13k/h':df[df['windspeed']>13]['count'].mean(), 
     u'V<13k/h': df[df['windspeed']<13]['count'].mean(), 
     u'T<24°C':df[df['atemp']<24]['count'].mean(), 
     u'T>24°C':df[df['atemp']>24]['count'].mean(), 
     u'H>62%': df[df['humidity']>62]['count'].mean(), 
     u'H<62%':df[df['humidity']<62]['count'].mean()
    }
od = collections.OrderedDict(sorted(D.items()))
width = 1/1.6
plt.figure()
plt.bar(range(len(od)), od.values(),width,color="blue",align='center')
plt.xticks(range(len(od)), od.keys())
plt.title('Variation de la demande en fonction de 3 variables')
plt.show()

################### 
################### Conclusion et choix des paramètres influents
################### 

##On calcule matrice de corrélation pour 
##retirer les variables corrélées

df.corr()
plt.matshow(df.corr())
plt.yticks(range(len(df.corr().columns)), df.corr().columns); 
plt.colorbar()
plt.show()

df1=df.drop(['workingday','datetime','season','atemp','holiday','registered','casual'],axis=1)

target=df1['count'].values #ensemble des outputs à prédire (yi)

train=df1.drop('count',axis=1) #ensemble des données (xi)

## Split aléatoire entre données d'entrainement
## et donnes test 
X_train, X_test, Y_train, Y_test = sklearn.cross_validation.train_test_split(
    train, target, test_size=0.33, random_state=42)

## Creation d'une classe pour tracer
## les courbes d'apprentissages

def plot_learning_curve(estimator, title, X, y, cv=None, n_jobs=1, train_sizes=np.linspace(.1, 1.0, 5)):
    plt.figure()
    plt.title(title)
    plt.xlabel("Training examples")
    plt.ylabel("Score")
    train_sizes, train_scores, test_scores = sklearn.learning_curve.learning_curve(
        estimator, X, y, cv=cv, n_jobs=n_jobs, train_sizes=train_sizes)
    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)
    plt.grid()
    plt.plot(train_sizes, train_scores_mean, 'o-', color="r", label="Training score")
    plt.plot(train_sizes, test_scores_mean, 'o-', color="g", label="Cross-validation score")
    plt.legend(loc="best")
    return plt

################### 
################### Regression Linéaire
################### 

linreg=linear_model.LinearRegression()
linreg.fit(X_train,Y_train)
tableau=[['Paramètre', 'Coefficient']] #liste pour voir les valeurs des coefficients
col=list(train.columns.values)
for i in range(7):
    tableau.append([col[i],linreg.coef_[i]])

print ("Training Score Regression Linéare : ", str(linreg.score(X_train,Y_train)))
print ("Test Score Regression Linéare : " , str(linreg.score(X_test,Y_test)))
print ("Coefficients Regression Linéare :")
print (tableau)

################### 
################### Gradient Boosting Regression
################### 

gbr = ensemble.GradientBoostingRegressor(n_estimators=2000)
gbr.fit(X_train,Y_train)
print ("Training Score GradientBoosting: ", str(gbr.score(X_train,Y_train)))
print ("Test Score GradientBoosting: " , str(gbr.score(X_test,Y_test)))

title = "Learning Curves (GradientBoosting)"
estimator = ensemble.GradientBoostingRegressor(n_estimators=2000)
plot_learning_curve(estimator, title, X_train, Y_train)
plt.show()

################### 
################### Support Vector Regression
################### 
svr=svm.SVR(kernel='linear')
svr.fit(X_train,Y_train)
print ("Training Score SVR: ", str(svr.score(X_train,Y_train)))
print ("Test Score SVR : " , str(svr.score(X_test,Y_test)))

################### 
################### Random Forest Regression
################### 

rf=ensemble.RandomForestRegressor(n_estimators=30,oob_score=True) #30 arbres et OOB Estimation
rf.fit(train,target)
print ("Training Score RandomForest: ", str(rf.score(train,target)))
print ("OOB Score RandomForest: " , str(rf.oob_score_))

################### 
################### Améliorations
################### 

## On cherche le paramètre le plus influent de notre modèle
## Pour cela on utilise deux algorithmes qu'on a utilisé :
## la régréssio linéaire et Random Forest
def param_import():
    col=list(train.columns.values)
    #on trouve d'abord les coefficients de la régréssion linéaire
    index1=linreg.coef_.argsort()[-2:][-1] #renvoie la liste triée des coef et on prend le premier élement
    index2=linreg.coef_.argsort()[-2:][0] #renvoie la liste triée des coef et on prend le deuxieme élement
    print('Pour les améliorations, calculons les paramètres les plus influents : ')
    print('...')
    print('Pour la regréssion linéaire, les paramètres les plus influents sont :', col[index1],' et ',col[index2])
    #on trouve ensuite les coefficients de la RF
    index3=rf.feature_importances_.argsort()[-2:][-1] 
    index4=rf.feature_importances_.argsort()[-2:][0] 
    print('Pour l\'algorithme de RF, les paramètres les plus influents sont :', col[index3],' et ',col[index4])
    #on trouve ensuite les coefficients de Gradient Boosting
    index5=gbr.feature_importances_.argsort()[-2:][-1]
    index6=gbr.feature_importances_.argsort()[-2:][0]
    print('Pour l\'algorithme de Gradient Boosting, les paramètres les plus influents sont :', col[index5],' et ',col[index6])
    if index3==index5:
        plus_import=index3
    elif index5==index4:
        plus_import=index4
    return plus_import

print('Le paramètre le plus important est donc : ', col[param_import()])

## On cherche à prouver que certains creneaux sont
##plus importants pour la demande en vélo

soir = df[df['hours'].isin([17,18,19])]
peak_soir=soir[soir['workingday']==1]
matin = df[df['hours'].isin([7,8,9])]
peak_matin=matin[matin['workingday']==1]
we = df[df['hours'].isin([12,13,14,15,16])]
peak_we=we[we['workingday']==0]

print('Calculons ensuite la moyenne du nombre de vélos pour plusieurs créneaux horaires : ')
print('...')
print('La moyenne totale de la demande est : ', df['count'].mean())
print('En semaine, entre 17 et 19h : ', peak_soir['count'].mean())
print('En semaine, entre 7 et 9h : ', peak_matin['count'].mean())
print('En week-end, entre 12 et 16h : ', peak_we['count'].mean())

