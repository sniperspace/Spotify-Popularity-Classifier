
# 🎵 Spotify Popularity Classifier

An end-to-end machine-learning system that predicts whether a Spotify track is likely to be **POPULAR** or **NOT POPULAR**.

## How It Works

Spotify Track URL
        ↓
Spotify API
        ↓
Track information
        ↓
Main model or Cold-Start model
        ↓
Calibrated probability
        ↓
Decision threshold
        ↓
POPULAR / NOT POPULAR

## Models

### Main Model

The main XGBoost model uses 96 engineered features.

Decision threshold:

0.46

### Cold-Start Model

The cold-start model handles tracks that are not present in the trained feature database.

It uses:

1. year
2. duration_ms
3. artist_popularity
4. genre_popularity
5. artist_track_count
6. genre_track_count

Decision threshold:

0.28

## Main Model Performance

| Metric | Score |
|---|---:|
| Accuracy | 0.8259 |
| Precision | 0.6586 |
| Recall | 0.6865 |
| F1 | 0.6723 |
| ROC-AUC | 0.8726 |
| PR-AUC | 0.7161 |

## Cold-Start Validation

The packaged cold-start model successfully predicted an unseen Spotify track:

- Model: Cold-Start XGBoost
- Probability: 0.328004
- Threshold: 0.280000
- Prediction: POPULAR

## Project Structure

Spotify-Popularity-Classifier/

    app.py
    requirements.txt
    README.md
    .gitignore

    model/
        main_xgb.json
        cold_start_xgb.json
        calibrator.pkl
        feature_config.json
        deployment_config.json

    src/
        __init__.py
        predictor.py
        spotify.py

    assets/
        artist_lookup.csv
        genre_lookup.csv

## Streamlit Dashboard

The dashboard is designed to provide:

- Spotify track URL input
- Track information
- Album artwork
- Popularity probability
- POPULAR / NOT POPULAR result
- Model information
- Decision threshold

## Installation

Clone the repository:

    git clone https://github.com/YOUR_USERNAME/Spotify-Popularity-Classifier.git

Enter the project:

    cd Spotify-Popularity-Classifier

Install dependencies:

    pip install -r requirements.txt

Run Streamlit:

    streamlit run app.py

## Spotify API Configuration

The application requires Spotify API authentication.

Do not commit API credentials to GitHub.

For Streamlit deployment, configure the required credential using Streamlit Secrets.

## Dataset

The original multi-gigabyte Spotify dataset is not included in this repository.

Only the deployment artifacts and compact lookup tables required for inference are included.

## Machine Learning Workflow

1. Data exploration
2. Feature engineering
3. Temporal validation
4. Main XGBoost training
5. Cold-start modeling
6. Probability calibration
7. Threshold optimization
8. Final test evaluation
9. Model serialization
10. Saved-model round-trip testing
11. Spotify track testing
12. Streamlit deployment preparation

## Project Status

Machine-learning pipeline: Complete

Deployment package: Complete

Cold-start inference: Complete

Packaged model test: Complete

Streamlit application: Final deployment stage
