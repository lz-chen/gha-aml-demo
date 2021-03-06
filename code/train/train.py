import argparse
import itertools
import json
import os
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import sklearn
from azureml.core import Model, Run
from config.constants import MODEL_NAME
from sklearn import datasets
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

run = Run.get_context()


# test
def log_confusion_matrix_image(
    cm,
    labels,
    normalize=False,
    log_name="confusion_matrix",
    title="Confusion matrix",
    cmap=plt.cm.Blues,
):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if normalize:
        cm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print("Confusion matrix, without normalization")
    print(cm)

    plt.figure()
    plt.imshow(cm, interpolation="nearest", cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(labels))
    plt.xticks(tick_marks, labels, rotation=45)
    plt.yticks(tick_marks, labels)

    fmt = ".2f" if normalize else "d"
    thresh = cm.max() / 2.0
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(
            j,
            i,
            format(cm[i, j], fmt),
            horizontalalignment="center",
            color="white" if cm[i, j] > thresh else "black",
        )

    plt.ylabel("True label")
    plt.xlabel("Predicted label")
    plt.tight_layout()
    run.log_image(log_name, plot=plt)
    plt.savefig(os.path.join("outputs", "{0}.png".format(log_name)))


def log_confusion_matrix(cm, labels):
    # log confusion matrix as object
    cm_json = {
        "schema_type": "confusion_matrix",
        "schema_version": "v1",
        "data": {"class_labels": labels, "matrix": cm.tolist()},
    }
    run.log_confusion_matrix("confusion_matrix", cm_json)

    # log confusion matrix as image
    log_confusion_matrix_image(
        cm,
        labels,
        normalize=False,
        log_name="confusion_matrix_unnormalized",
        title="Confusion matrix",
    )

    # log normalized confusion matrix as image
    log_confusion_matrix_image(
        cm,
        labels,
        normalize=True,
        log_name="confusion_matrix_normalized",
        title="Normalized confusion matrix",
    )


def main(params):
    # create the outputs folder
    os.makedirs("outputs", exist_ok=True)

    # Log arguments
    kernel_type = params["kernel"]
    penalty = params["penalty"]
    run.log("Kernel type", np.str(kernel_type))
    run.log("Penalty", np.float(penalty))

    # Load iris dataset
    X, y = datasets.load_iris(return_X_y=True)

    # dividing X,y into train and test data
    x_train, x_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=223
    )
    data = {"train": {"X": x_train, "y": y_train}, "test": {"X": x_test, "y": y_test}}

    # train a SVM classifier
    svm_model = SVC(kernel=kernel_type, C=penalty, gamma="scale").fit(
        data["train"]["X"], data["train"]["y"]
    )
    svm_predictions = svm_model.predict(data["test"]["X"])

    # accuracy for X_test
    accuracy = svm_model.score(data["test"]["X"], data["test"]["y"])
    print("Accuracy of SVM classifier on test set: {:.2f}".format(accuracy))
    run.log("Accuracy", np.float(accuracy))

    # precision for X_test
    precision = precision_score(svm_predictions, data["test"]["y"], average="weighted")
    print("Precision of SVM classifier on test set: {:.2f}".format(precision))
    run.log("precision", precision)

    # recall for X_test
    recall = recall_score(svm_predictions, data["test"]["y"], average="weighted")
    print("Recall of SVM classifier on test set: {:.2f}".format(recall))
    run.log("recall", recall)

    # f1-score for X_test
    f1 = f1_score(svm_predictions, data["test"]["y"], average="weighted")
    print("F1-Score of SVM classifier on test set: {:.2f}".format(f1))
    run.log("f1-score", f1)

    # create a confusion matrix
    labels = ["Iris-setosa", "Iris-versicolor", "Iris-virginica"]
    labels_numbers = [0, 1, 2]
    cm = confusion_matrix(y_test, svm_predictions, labels_numbers)
    log_confusion_matrix(cm, labels)

    # files saved in the "outputs" folder are automatically uploaded into run history
    ws_model_path = os.path.join("outputs", "model.pkl")
    joblib.dump(svm_model, ws_model_path)
    run.log("Model Name", np.str(MODEL_NAME))

    run.upload_file(ws_model_path, ws_model_path)

    run.register_model(
        model_name=MODEL_NAME,
        model_path=ws_model_path,  # run outputs path
        description="A classification model for iris dataset",
        model_framework=Model.Framework.SCIKITLEARN,
        model_framework_version=sklearn.__version__,
    )


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--param-file",
        type=str,
        default="dev_params.json",
        help="Json file that contains training parameters",
    )
    args = parser.parse_args()
    train_dir = Path(__file__).parent
    param_file = train_dir.joinpath("config").joinpath(args.param_file)
    with param_file.open() as f:
        params = json.load(f)
    print(params)
    return params


if __name__ == "__main__":
    params = parse_args()
    main(params=params)
