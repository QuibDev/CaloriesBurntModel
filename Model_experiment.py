# imports

# libraries used -->
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import KFold


# models -->
from sklearn import linear_model
from sklearn.svm import SVR
from sklearn.model_selection import GridSearchCV
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import PolynomialFeatures
from xgboost import XGBRegressor


# loading data

calories = pd.read_csv('data/calories.csv')
exercise = pd.read_csv('data/exercise.csv')


# checking data

#print('\nCalories\n')
#print(calories.head())
#print(calories.shape)

#print('\nExercise\n')
#print(exercise.head())
#print(exercise.shape)


# combining both dataframes

calories_data = pd.concat([exercise, calories['Calories']], axis=1)
# axis = 1 means adding data row wise

# Outlier Check -->
#print("\nOutliers -->")
for k ,v in calories_data[['Age','Height','Duration','Heart_Rate','Body_Temp','Calories']].items():
    quarter_1 = v.quantile(0.25)
    quarter_3 = v.quantile(0.75)
    inter_quartile = quarter_3 - quarter_1
    value_columns = v[(v <= quarter_1 - 1.5*inter_quartile) | (v >= quarter_3 + 1.5*inter_quartile)]
    percentage = np.shape(value_columns)[0]*100.0 / np.shape(calories_data)[0]

    # Print out result -->
    #print("Column {} outliers = {:.2f}".format(k,percentage))

#print(calories_data.head())



#checking for missing values
calories_data.isnull().sum()


## Data Analysis

# getting some statistical measures about data
calories_data.describe()

# converting text data to numerical values
calories_data.replace({'Gender':{'male':0,'female':1}}, inplace=True)


## Data Visualization

# plotting the gender column in count plot
sns.set()

# plotting the gender column in count plot
sns.countplot(calories_data['Gender'])

# plotting distribution plot of age
sns.displot(calories_data['Age'])

# plotting distribution of weight
sns.displot(calories_data['Weight'])


## Finding Corelation between data

correlation = calories_data.corr()

# plotting corelation heatmap
plt.figure(figsize=(10,10))
sns.heatmap(correlation, cbar=True, square=True, fmt='.1f', annot=True, annot_kws={'size':8}, cmap='Blues')

# --> calories and duration have the highest corelation (1.0)
# --> so we might use them for corelation


# Separating features and target (calories)
X = calories_data.drop(columns=['User_ID','Calories'],axis=1)
Y = calories_data['Calories']


## Splitting test and train data
X_train, X_test, y_train, y_test = train_test_split(X,Y, test_size = 0.2, random_state = 2)


## Log Transformation

features = ['Age','Height','Duration','Heart_Rate','Body_Temp','Calories']
x_data = calories_data.loc[:,features]
y_label = calories_data['Calories']
min_max_scaler = MinMaxScaler()
x_data = pd.DataFrame(data=min_max_scaler.fit_transform(x_data), columns = features)
y_label = np.log1p(y_label)
for features in x_data.columns:
    if np.abs(x_data[features].skew()) > 0.5:
        x_data[features] = np.log1p(x_data[features])



## Training models

print('\nTraining Models')

# Polynomial Linear Regression -->
plr = make_pipeline(PolynomialFeatures(degree=3), linear_model.Ridge())
plr.fit(X_train, y_train)


print('\nSupport Vector Regression...')
# Support Vector Regression -->
svr_rbf = SVR(kernel='rbf',C=1e3,gamma=0.1)
grid_param = {'C':[1e0,1e1,1e2,1e3,1e4,1e5],'gamma':np.logspace(-2,2,5)}
grid_svr = GridSearchCV(svr_rbf, cv=KFold(n_splits=10), param_grid=grid_param)
svr = make_pipeline(StandardScaler(),grid_svr)
svr.fit(X_train,y_train)

print('\nSVR Done')
print('\nGradient Boosting Regressor...')
# Gradient boosting regressor -->
gbr = GradientBoostingRegressor(alpha=0.8,learning_rate=0.06,max_depth=2,min_samples_leaf=2,
                                min_samples_split=2, n_estimators=100, random_state=30)
param_grid_gbr = {'n_estimators':[100,200],'learning_rate':[0.1,0.05,0.02,0.005],'max_depth':[2,4,6],
                   'min_samples_leaf':[3,5,9]}
grid_gbr = GridSearchCV(gbr,param_grid=param_grid_gbr)
gbr = make_pipeline(StandardScaler(),grid_gbr)
gbr.fit(X_train,y_train)

print('Decision Tree Regression...')
# Descision tree regression -->
dtr = DecisionTreeRegressor(max_depth=5)
param_grid_dtr = {'max_depth':[1,2,3,4,5,6,7]}
grid_dtr = GridSearchCV(dtr, cv=KFold(n_splits=10),param_grid=param_grid_dtr)
dtr = make_pipeline(StandardScaler(),grid_dtr)
dtr.fit(X_train,y_train)


accuracy_plr = plr.score(X_test, y_test)
accuracy_dtr = dtr.score(X_test,y_test)
accuracy_svr = svr.score(X_test,y_test)
accuracy_gbr = gbr.score(X_test,y_test)
accuracy_xgb = xgb.score(X_test,y_test)


# print out results -->
print('\nStandard Accuracy Score (Higher Is Better) -->\n')
print('Polynomial Linear Regression: {:.2f}'.format(accuracy_plr))
print('Decision Tree Regression: {:.2f}'.format(accuracy_dtr))
print('Support Vector Regression: {:.2f}'.format(accuracy_svr))
print('Gradient Boost Regression: {:.2f}'.format(accuracy_gbr))
print('XGB Regression: {:.2f}'.format(accuracy_xgb))












