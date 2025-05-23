import pandas as pd
from joblib import load
from flask import Flask, request, jsonify
from flask_cors import CORS
from category_encoders import BinaryEncoder

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load the model and dataset
try:
    model = load('decision_tree_model.joblib')
    data = pd.read_csv('brain_stroke.csv')
    
    # Define expected features (both categorical and numerical)
    categorical_features = ['gender', 'ever_married', 'work_type', 'Residence_type', 'smoking_status']
    numerical_features = ['age', 'hypertension', 'heart_disease', 'avg_glucose_level', 'bmi']
    expected_features = numerical_features + categorical_features
    
    # Fit the encoder
    encoder = BinaryEncoder(cols=categorical_features)
    encoder.fit(data[categorical_features])
    
    print("Model and encoder loaded successfully")
except Exception as e:
    print(f"Error during initialization: {str(e)}")
    raise

@app.route('/api/hfp_prediction', methods=['POST'])
def predict_brain_stroke():
    try:
        # Get input data
        request_data = request.json
        input_data = request_data['inputs']
        input_df = pd.DataFrame(input_data)
        
        # Validate input features
        missing_features = set(expected_features) - set(input_df.columns)
        if missing_features:
            return jsonify({"error": f"Missing features: {missing_features}"}), 400
        
        # Ensure correct data types for numerical features
        for feature in numerical_features:
            input_df[feature] = pd.to_numeric(input_df[feature], errors='coerce')
            if input_df[feature].isnull().any():
                return jsonify({"error": f"Invalid value for {feature}"}), 400
        
        # Reorder columns to match training data
        input_df = input_df[expected_features]
        
        # Encode categorical features
        input_encoded = encoder.transform(input_df[categorical_features])
        
        # Combine with numerical features
        final_input = pd.concat([input_df[numerical_features], input_encoded], axis=1)
        
        # Predict probabilities
        prediction = model.predict_proba(final_input)
        
        # Prepare response
        response = []
        for probs in prediction:
            # Assuming class 1 is stroke, class 0 is no stroke
            stroke_prob = round(float(probs[1]) * 100, 2)
            no_stroke_prob = round(float(probs[0]) * 100, 2)
            
            response.append({
                "stroke_risk_percentage": stroke_prob,
                "no_stroke_risk_percentage": no_stroke_prob
            })
        
        return jsonify({"predictions": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)