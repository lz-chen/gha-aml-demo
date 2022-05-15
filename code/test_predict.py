import argparse
import json

import requests


def main(endpoint):
    # An array of new data cases
    print("Creating input data")
    x_new = [[0.1, 2.3, 4.1, 2.0], [0.2, 1.8, 3.9, 2.1]]
    # Convert the array to a serializable list in a JSON document
    json_data = json.dumps({"data": x_new})
    # Set the content type in the request headers
    request_headers = {"Content-Type": "application/json"}

    # Call the service
    response = requests.post(url=endpoint, data=json_data, headers=request_headers)

    # Get the predictions from the JSON response
    predictions = json.loads(response.json())

    # Print the predicted class for each case.
    for i in range(len(x_new)):
        print((x_new[i]), predictions[i])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--scoring-url", type=str, help="Scoring URL")
    args = parser.parse_args()
    main(endpoint=args.scoring_url)
