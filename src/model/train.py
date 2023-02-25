# Import libraries

import argparse
import glob
import os

import mlflow
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split


# define functions
def main(args):
    # TO DO: enable autologging
    mlflow.autolog(log_models=False)

    # read data
    df = get_csvs_df(args.training_data)

    # split data
    X_train, X_test, y_train, y_test = split_data(df)

    # train model
    model = train_model(args.reg_rate, X_train, X_test, y_train, y_test)

    # register model
    mlflow.sklearn.log_model(
        sk_model=model,
        registered_model_name=args.model_name,
        artifact_path=args.model_name,
    )


def get_csvs_df(path):
    if not os.path.exists(path):
        raise RuntimeError(f"Cannot use non-existent path provided: {path}")
    csv_files = glob.glob(f"{path}/*.csv")
    if not csv_files:
        raise RuntimeError(f"No CSV files found in provided data path: {path}")
    return pd.concat((pd.read_csv(f) for f in csv_files), sort=False)


# TO DO: add function to split data
def split_data(df):
    X, y = (
        df[
            [
                "Pregnancies",
                "PlasmaGlucose",
                "DiastolicBloodPressure",
                "TricepsThickness",
                "SerumInsulin",
                "BMI",
                "DiabetesPedigree",
                "Age",
            ]
        ].values,
        df["Diabetic"].values,
    )
    return train_test_split(X, y, test_size=0.30, random_state=0)


def train_model(reg_rate, X_train, X_test, y_train, y_test):
    model = LogisticRegression(C=1 / reg_rate, solver="liblinear")
    # train model
    model.fit(X_train, y_train)
    return model


def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    # add arguments
    parser.add_argument("--training_data", dest="training_data", type=str)
    parser.add_argument("--reg_rate", dest="reg_rate", type=float, default=0.01)
    parser.add_argument(
        "--model_name", dest="model_name", type=str, default="diabetes-sklearn-log-reg"
    )

    # parse args
    args = parser.parse_args()

    # return args
    return args


# run script
if __name__ == "__main__":
    # add space in logs
    print("\n\n")
    print("*" * 60)

    # parse args
    args = parse_args()

    # run main function
    main(args)

    # add space in logs
    print("*" * 60)
    print("\n\n")
