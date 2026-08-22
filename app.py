
import streamlit as st
import os
import sys

# Allow imports from src/
sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "src"
    )
)

from predictor import predict_cold_start
from spotify import get_track


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Spotify Popularity Predictor",
    page_icon="🎵",
    layout="wide"
)


# --------------------------------------------------
# Styling
# --------------------------------------------------

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(
            circle at top right,
            #183d2b 0,
            #0b0f0d 35%,
            #080b09 100%
        );
}

.block-container {
    max-width: 1200px;
    padding-top: 3rem;
    padding-bottom: 3rem;
}

.hero {
    padding: 2.5rem;
    border-radius: 24px;
    background: rgba(20, 30, 25, 0.90);
    border: 1px solid #294238;
    margin-bottom: 2rem;
}

.hero-title {
    font-size: 3.2rem;
    font-weight: 800;
    margin-bottom: 0.5rem;
}

.hero-subtitle {
    color: #aebbb4;
    font-size: 1.15rem;
}

.result-card {
    padding: 2rem;
    border-radius: 22px;
    background: rgba(18, 25, 21, 0.95);
    border: 1px solid #294238;
    text-align: center;
}

.track-name {
    font-size: 1.8rem;
    font-weight: 700;
}

.artist-name {
    color: #aebbb4;
    font-size: 1.05rem;
}

.probability {
    font-size: 4rem;
    font-weight: 800;
    margin: 0.5rem 0;
}

.popular {
    color: #55d98a;
}

.not-popular {
    color: #ff7676;
}

.model-box {
    padding: 1rem;
    border-radius: 14px;
    background: #111814;
    border: 1px solid #26382f;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.markdown("""
<div class="hero">

<div class="hero-title">
🎵 Spotify Popularity Predictor
</div>

<div class="hero-subtitle">
AI-powered popularity prediction using calibrated XGBoost
models and live Spotify track data.
</div>

</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# Input
# --------------------------------------------------

st.subheader("Analyze a Spotify Track")

spotify_url = st.text_input(
    "Spotify Track URL",
    placeholder="https://open.spotify.com/track/..."
)

predict_button = st.button(
    "🔮 Predict Popularity",
    type="primary",
    use_container_width=True
)


# --------------------------------------------------
# Prediction
# --------------------------------------------------

if predict_button:

    if not spotify_url.strip():

        st.warning(
            "Please paste a Spotify track URL."
        )
        st.stop()

    # Get Spotify token
    access_token = (
        st.secrets.get(
            "SPOTIFY_ACCESS_TOKEN",
            os.getenv(
                "SPOTIFY_ACCESS_TOKEN"
            )
        )
    )

    if not access_token:

        st.error(
            "Spotify API access token is not configured."
        )

        st.info(
            "Add SPOTIFY_ACCESS_TOKEN to "
            "Streamlit Secrets."
        )

        st.stop()

    with st.spinner(
        "Fetching track information..."
    ):

        track = get_track(
            spotify_url,
            access_token
        )

    if track["status"] != "success":

        st.error(
            track.get(
                "message",
                "Could not retrieve the Spotify track."
            )
        )

        st.stop()

    # --------------------------------------------------
    # Display track
    # --------------------------------------------------

    col1, col2 = st.columns(
        [1, 3],
        gap="large"
    )

    with col1:

        if track.get("image"):

            st.image(
                track["image"],
                use_container_width=True
            )

    with col2:

        artists = ", ".join(
            track.get("artists", [])
        )

        st.markdown(
            f"""
            <div class="track-name">
                {track.get("name", "Unknown Track")}
            </div>

            <div class="artist-name">
                {artists}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write(
            f"Album: {track.get('album', 'Unknown')}"
        )

        st.write(
            f"Release date: "
            f"{track.get('release_date', 'Unknown')}"
        )

    st.divider()

    # --------------------------------------------------
    # Cold-start prediction
    # --------------------------------------------------

    release_date = track.get(
        "release_date"
    )

    try:
        year = int(
            str(release_date)[:4]
        )
    except Exception:
        year = 0

    duration_ms = track.get(
        "duration_ms"
    )

    artist_list = track.get(
        "artists",
        []
    )

    artist_name = (
        artist_list[0]
        if artist_list
        else "Unknown"
    )

    result = predict_cold_start(
        year=year,
        duration_ms=duration_ms,
        artist_name=artist_name
    )

    probability = result[
        "probability"
    ]

    prediction = result[
        "prediction"
    ]

    # --------------------------------------------------
    # Result
    # --------------------------------------------------

    if prediction == "POPULAR":

        result_class = "popular"
        emoji = "🟢"

    else:

        result_class = "not-popular"
        emoji = "🔴"

    st.markdown(
        f"""
        <div class="result-card">

        <div style="font-size:1rem;color:#aebbb4;">
        PREDICTED POPULARITY
        </div>

        <div class="probability {result_class}">
        {probability:.1%}
        </div>

        <div style="font-size:1.8rem;font-weight:700;">
        {emoji} {prediction}
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.progress(
        min(max(probability, 0.0), 1.0)
    )

    st.write("")

    # --------------------------------------------------
    # Model information
    # --------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Model",
            "Cold-Start XGBoost"
        )

    with col2:

        st.metric(
            "Probability",
            f"{probability:.1%}"
        )

    with col3:

        st.metric(
            "Decision Threshold",
            f"{result['threshold']:.0%}"
        )

    st.caption(
        "Prediction generated using the calibrated "
        "production model."
    )
