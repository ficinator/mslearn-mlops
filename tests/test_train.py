import os

import pandas as pd
import pytest

from model.train import get_csvs_df, split_data


def test_csvs_no_files():
    with pytest.raises(RuntimeError) as error:
        get_csvs_df("./")
    assert error.match("No CSV files found in provided data")


def test_csvs_no_files_invalid_path():
    with pytest.raises(RuntimeError) as error:
        get_csvs_df("/invalid/path/does/not/exist/")
    assert error.match("Cannot use non-existent path provided")


def test_csvs_creates_dataframe():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    datasets_directory = os.path.join(current_directory, "datasets")
    result = get_csvs_df(datasets_directory)
    assert len(result) == 20


def test_split_data():
    df = pd.DataFrame(
        data=[
            (1142956, 1, 78, 41, 33, 311, 50.79639151, 0.420803683, 24, 0),
            (1823377, 0, 116, 92, 16, 184, 18.60362975, 0.131156495, 22, 0),
            (1916381, 8, 171, 42, 29, 160, 35.48224692, 0.082671083, 22, 1),
        ],
        columns=[
            "PatientID",
            "Pregnancies",
            "PlasmaGlucose",
            "DiastolicBloodPressure",
            "TricepsThickness",
            "SerumInsulin",
            "BMI",
            "DiabetesPedigree",
            "Age",
            "Diabetic",
        ],
    )
    X_train, X_test, y_train, y_test = split_data(df)
    assert len(X_train) == 2
    assert len(X_test) == 1
    assert len(y_train) == 2
    assert len(y_test) == 1
