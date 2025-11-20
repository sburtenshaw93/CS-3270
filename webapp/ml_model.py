""" 
Machine Learning Module
Predicts weather it will rain tomorrow based on today's weather
Uses Random Forest Classified from scikit-learn
"""
import pandas as pd
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report

MODEL_PATH = 'webapp/rain_predictor_model.pkl'
ENCODERS_PATH = 'webapp/location_encoder.pkl'

def train_model():
    """ 
    Train the random forest model using the weather training data
    Saves the trained model to disk
    """
    print("\n" + "🤖"*30 + "\n" + " "*12 + "Training Machine Learning Model")
    
    # Load the training data
    df = pd.read_csv('archive/Weather Training Data.csv')
    
    # Features being used: Location, MinTemp,MaxTemp, Rainfall, RainToday
    features_to_use = ['Location', "MinTemp", 'MaxTemp', 'Rainfall', 'RainToday'] 
    target = 'RainTomorrow'
    
    # Remove rows with missing values in our selected columns
    df_clean = df[features_to_use + [target]].dropna().copy()

    print(f"Training data: {len(df_clean)} records (after removing missing values)")
    
    # Encode categorical variables
    location_encoder = LabelEncoder()
    df_clean['Location_Encoded'] = location_encoder.fit_transform(df_clean['Location']) 
    
    # Convert RainToday to binary --> No=0, Yes=1
    df_clean['RainToday_Binary'] = df_clean['RainToday'].map({'No': 0, 'Yes': 1})
    
    # Prepare features X and target y
    X = df_clean[['Location_Encoded', 'MinTemp', 'MaxTemp', 'Rainfall', 'RainToday_Binary']]
    y = df_clean[target]
    
    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Create and train the random forest model
    print("Training Random Forest Classifier")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Test the model accuracy
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Model trained successfully")
    print(f"Accuracy on test data: {accuracy * 100:.2f}%")
    print(f"Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save the model and encoders to disk
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
        
    with open(ENCODERS_PATH, 'wb') as f:
        pickle.dump(location_encoder, f)
    
    print(f"Model saved to {MODEL_PATH}")
    print(f"Encoders saved to {ENCODERS_PATH}")
    
    return model, location_encoder

def load_model():
    """ 
    Load the trained model from the disk
    Returns the model and location encoder
    """
    if not os.path.exists(MODEL_PATH):
        print("⚠️ Model not found. Training new model")
        return train_model
    
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    
    with open(ENCODERS_PATH, 'rb') as f:
        location_encoder = pickle.load(f)
    
    return model, location_encoder

def predict_rain(location, min_temp, max_temp, rainfall, rain_today):
    """ 
    Predict weather it will rain tomorrow
    """
    model, location_encoder = load_model()
    
    # Encode the location
    try:
        location_encoded = location_encoder.transform([location])[0]
    except:
        location_encoded = 0
        print(f"⚠️ Location '{location}' not found. Using default")
    # Convert rain_today to binary
    rain_today_binary = 1 if rain_today.lower() == 'yes' else 0
    
    # Create feature array
    features = [[location_encoded, min_temp, max_temp, rainfall, rain_today_binary]]
    
    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0]
    
    # probability[0] -> means its not likely to rain
    # probability[1] -> means its likely to rain
    
    result = {
        'prediction': 'Yes' if prediction == 1 else 'No',
        'confidence': max(probability) * 100,
        'rain_probability': probability[1] * 100 if len(probability) > 1 else 0,
        'no_rain_probability': probability[0] * 100
    }
    return result

if __name__ == "__main__":
    """ 
    Training the model when this file is run directly
    """
    train_model()
    
    # Test prediction
    print("\n Testing prediction")
    test_result = predict_rain(
        location='Sydney',
        min_temp=15.0,
        max_temp=25.0,
        rainfall=5.0,
        rain_today='Yes'
    )
    print(f"Test prediction: {test_result}")