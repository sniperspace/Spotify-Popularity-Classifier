
import json
import joblib
import pandas as pd
from pathlib import Path
from xgboost import XGBClassifier


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "model"
ASSET_DIR = BASE_DIR / "assets"


# -----------------------------
# Load production models
# -----------------------------

main_model = XGBClassifier()
main_model.load_model(
    str(MODEL_DIR / "main_xgb.json")
)

cold_start_model = XGBClassifier()
cold_start_model.load_model(
    str(MODEL_DIR / "cold_start_xgb.json")
)

calibrator = joblib.load(
    MODEL_DIR / "calibrator.pkl"
)


# -----------------------------
# Load configuration
# -----------------------------

with open(
    MODEL_DIR / "feature_config.json",
    "r"
) as f:
    feature_config = json.load(f)

with open(
    MODEL_DIR / "deployment_config.json",
    "r"
) as f:
    deployment_config = json.load(f)


# -----------------------------
# Load cold-start statistics
# -----------------------------

artist_lookup = pd.read_csv(
    ASSET_DIR / "artist_lookup.csv",
    index_col=0
)

genre_lookup = pd.read_csv(
    ASSET_DIR / "genre_lookup.csv",
    index_col=0
)


# -----------------------------
# Main-model prediction
# -----------------------------

def predict_main(X):

    raw_probability = float(
        main_model.predict_proba(X)[0, 1]
    )

    probability = float(
        calibrator.predict_proba(
            [[raw_probability]]
        )[0, 1]
    )

    threshold = float(
        deployment_config["main_threshold"]
    )

    return {
        "model": "Main XGBoost",
        "probability": probability,
        "threshold": threshold,
        "prediction": (
            "POPULAR"
            if probability >= threshold
            else "NOT POPULAR"
        )
    }


# -----------------------------
# Cold-start prediction
# -----------------------------

def predict_cold_start(
    year,
    duration_ms,
    artist_name
):

    # Duration fallback
    if duration_ms is None:
        duration_ms = 225740.5

    # Artist statistics
    if artist_name in artist_lookup.index:

        artist_popularity = float(
            artist_lookup.loc[
                artist_name,
                "artist_popularity"
            ]
        )

        artist_track_count = int(
            artist_lookup.loc[
                artist_name,
                "artist_track_count"
            ]
        )

    else:

        artist_popularity = float(
            artist_lookup[
                "artist_popularity"
            ].mean()
        )

        artist_track_count = int(
            artist_lookup[
                "artist_track_count"
            ].median()
        )

    # Genre statistics
    #
    # The current Spotify track endpoint used by
    # this project does not provide the training
    # genre directly, so use the training-wide
    # genre baseline.

    genre_popularity = float(
        genre_lookup[
            "genre_popularity"
        ].mean()
    )

    genre_track_count = int(
        genre_lookup[
            "genre_track_count"
        ].median()
    )

    X = pd.DataFrame([{
        "year": year,
        "duration_ms": duration_ms,
        "artist_popularity":
            artist_popularity,
        "genre_popularity":
            genre_popularity,
        "artist_track_count":
            artist_track_count,
        "genre_track_count":
            genre_track_count
    }])

    X = X[
        feature_config[
            "cold_start_features"
        ]
    ]

    probability = float(
        cold_start_model.predict_proba(
            X
        )[0, 1]
    )

    threshold = float(
        deployment_config[
            "cold_start_threshold"
        ]
    )

    return {
        "model": "Cold-Start XGBoost",
        "probability": probability,
        "threshold": threshold,
        "prediction": (
            "POPULAR"
            if probability >= threshold
            else "NOT POPULAR"
        )
    }
