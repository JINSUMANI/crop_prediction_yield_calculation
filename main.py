import os

import numpy as np
import pandas as pd
import requests
from flask import Flask, request, jsonify
from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


app = Flask(__name__)
#to get heroku port 
port = int(os.environ.get('PORT', 5000))

#decorator used to bind url to the function
@app.route("/values", methods=['POST', 'GET'])
def nameroute():
    
    location = request.args.get('city')
    print("location from the client is ",location)
    area = int(request.args.get('area'))
    user_api = "765fb6f4e326058496208ad4b995e5a0"
    complete_api_link = "https://api.openweathermap.org/data/2.5/weather?q=" + location + "&appid=" + user_api
    api_link = requests.get(complete_api_link)
    api_data = api_link.json()
    # create variables to store and display data
    print("!@#", api_data)
    if api_data['cod']=='404':
        return 'Invalid District!!'
    else:
        temp = ((api_data['main']['temp']) - 273.15)
        print(temp, "is ")
        humid = api_data['main']['humidity']
        wind = api_data['wind']['speed']
        rain = api_data['clouds']['all']
        df = pd.read_csv("cropsetss")
        df.head()
        features = df[['Rainfall', 'Temperature', 'Humidity', 'Windspeed']]
        target = df['Crop']
        labels = df['Crop']
        X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=2)
        RF = RandomForestClassifier(n_estimators=100, random_state=1)
        RF.fit(X_train, y_train)
        y_pred = RF.predict(X_test)
        predicted_values = RF.predict(X_test)
        #x = metrics.accuracy_score(y_test, predicted_values)
        df = np.array([[temp, humid, rain, wind]])
        prediction = RF.predict(df)
        cropname=''.join(prediction)
        # print(prediction)
        sug=pd.read_csv("suggestedcrop",index_col='Crop')
        scrop=sug.loc[cropname]
        set=scrop.Suggested
        print(set)
        new = pd.read_csv("cropandprodctns", index_col='Crop')
        pg = new.loc[prediction]
        n = pg.Production
        production = int(n)
        if area > 0:
            crop_yield = production / area
            print("::::::", prediction, crop_yield)
            return jsonify({'CropName': str(cropname), 'CropYield': str(round(crop_yield,6)), 'Suggestedcrops':set,'Temperature':temp,'Humidity':humid,'Rainfall':rain,'Windspeed':wind})
        # print(crop_yield)
        else:
            return "Some value is missing"

if __name__ == "__main__":
    app.run(debug=True, port=port)