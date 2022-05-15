import argparse
import json

import requests


def main(endpoint, key):
    # An array of new data cases
    print("Creating input data")
    x_new = [[7.1, 3.0, 5.9, 2.1], [4.7, 3.2, 1.3, 0.2]]
    # Convert the array to a serializable list in a JSON document
    json_data = json.dumps({"data": x_new})
    # Set the content type in the request headers
    request_headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + key,
    }

    # Call the service
    response = requests.post(url=endpoint, data=json_data, headers=request_headers)

    # Get the predictions from the JSON response
    predictions = response.json()
    # Print the predicted class for each case.
    for i in range(len(x_new)):
        print(f"data: {x_new[i]}; prediction: {predictions['predict'][i]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--scoring-url", type=str, help="Scoring URL")
    parser.add_argument("--primary-key", type=str, help="Auth key")
    args = parser.parse_args()
    main(endpoint=args.scoring_url, key=args.primary_key)
