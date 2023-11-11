from flask import Flask, request, jsonify
import joblib
from datetime import datetime
import pandas as pd

import pandas as pd
from flask import Flask, request, jsonify
from datetime import datetime
import joblib

# Load the DataFrame from the CSV file
df = pd.read_csv("API/fornecedoras.csv")

# Initialize the Flask application
app = Flask(__name__)

# Load the trained model (make sure the model is available)
model = joblib.load("API/modelo_recomendacao.joblib")

# Variable to generate unique identifiers
prediction_counter = 1

def perform_prediction(school, df, model):
    # Initialize variables to track the best supplier and its rating
    best_supplier = None
    highest_rating = float('-inf')

    # Iterate over all suppliers in the DataFrame
    for supplier in df['CNPJ']:
        prediction_result = model.predict(school, supplier).est

        # Update if the current rating is higher than the previous one
        if prediction_result > highest_rating:
            highest_rating = prediction_result
            best_supplier = supplier

    return best_supplier, highest_rating

@app.route("/predictSupplier", methods=["POST"])
def predict():
    global prediction_counter  # Variable to generate unique identifiers
    # Receive the data sent in the request
    data = request.json  # Assuming the data is sent in JSON format

    # Perform data preprocessing if necessary

    # Make predictions with the model
    school = data.get("CIE")

    # Check if the "CIE" key is present in the data
    if school is None:
        return jsonify({"Error": "Key 'CIE' is missing in the data"}), 400

    try:
        best_supplier, highest_rating = perform_prediction(school, df, model)

        # Generate a unique identifier for the prediction
        identifier = f"{prediction_counter}"
        prediction_counter += 1

        # Get the current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Return the predictions, timestamp, identifier, and status code 200 (OK)
        result = {
            "id": identifier,
            "timestamp": timestamp,
            "best_supplier": best_supplier,
            "highest_rating": highest_rating
        }
        return jsonify(result), 200  # 200 OK as the status code
    except Exception as e:
        # Handle errors and return an appropriate status code (e.g., 400 for Bad Request)
        return jsonify({"Error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)

