import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="Fire Harmonization | Florida",
    page_icon="🔥",
    layout="wide"
)


# ============================================================
# FIRE THEME + TYPOGRAPHY
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
            radial-gradient(
                circle at 15% 10%,
                rgba(255, 70, 0, 0.14),
                transparent 28%
            ),
            radial-gradient(
                circle at 85% 80%,
                rgba(255, 140, 0, 0.08),
                transparent 25%
            ),
            linear-gradient(
                135deg,
                #080604 0%,
                #120b07 50%,
                #070504 100%
            );
    }

    /* ========================================================
       TYPOGRAPHY
       ======================================================== */

    html, body, [class*="css"] {
        font-family:
            "Inter",
            "Segoe UI",
            Arial,
            sans-serif;
    }

    h1 {
        font-family:
            "Arial Black",
            "Inter",
            sans-serif;

        font-weight: 900;
        letter-spacing: -1.5px;
        text-transform: uppercase;
    }

    h2 {
        font-family:
            "Inter",
            "Segoe UI",
            sans-serif;

        font-weight: 750;
        letter-spacing: -0.5px;
    }

    h3 {
        font-family:
            "Inter",
            "Segoe UI",
            sans-serif;

        font-weight: 650;
    }

    p {
        font-family:
            "Inter",
            "Segoe UI",
            Arial,
            sans-serif;

        line-height: 1.6;
    }

    /* ========================================================
       METRICS
       ======================================================== */

    [data-testid="stMetricValue"] {
        color: #ff8a3d;

        font-family:
            "Inter",
            "Segoe UI",
            sans-serif;

        font-weight: 800;
        letter-spacing: -1px;
    }

    [data-testid="stMetricLabel"] {
        color: #b9a08e;

        font-family:
            "Inter",
            "Segoe UI",
            sans-serif;

        font-weight: 500;
        letter-spacing: 0.3px;
    }

    /* ========================================================
       SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {
        background: #0b0705;
    }

    section[data-testid="stSidebar"] * {
        font-family:
            "Inter",
            "Segoe UI",
            Arial,
            sans-serif;
    }

    /* ========================================================
       NORMAL BUTTONS
       ======================================================== */

    .stButton > button {
        border: 1px solid #ff6a00;
        background: #1a0d05;
        color: #ff9d52;

        font-family:
            "Inter",
            "Segoe UI",
            sans-serif;

        font-weight: 650;
        letter-spacing: 0.2px;
    }

    .stButton > button:hover {
        border-color: #ff8c00;
        color: #ffb36b;
        background: #241106;
    }

    /* ========================================================
       DOWNLOAD BUTTONS
       ======================================================== */

    div[data-testid="stDownloadButton"] button {
        min-height: 52px;

        font-family:
            "Inter",
            "Segoe UI",
            sans-serif;

        font-weight: 700;

        border-radius: 10px;

        transition:
            background 0.2s ease,
            border-color 0.2s ease,
            transform 0.2s ease;
    }

    div[data-testid="stDownloadButton"] button:hover {
        transform: translateY(-2px);
    }

    /* QC */

    div[data-testid="stDownloadButton"]:nth-of-type(1) button {
        background:
            linear-gradient(
                135deg,
                #3b0d02,
                #7a1f05
            );

        border: 1px solid #ff4d00;
        color: #ffd0b3;
    }

    div[data-testid="stDownloadButton"]:nth-of-type(1) button:hover {
        background:
            linear-gradient(
                135deg,
                #591505,
                #a52a05
            );

        border-color: #ff6a00;
        color: white;
    }

    /* RAW */

    div[data-testid="stDownloadButton"]:nth-of-type(2) button {
        background:
            linear-gradient(
                135deg,
                #3d1800,
                #a44700
            );

        border: 1px solid #ff8c00;
        color: #ffe0bd;
    }

    div[data-testid="stDownloadButton"]:nth-of-type(2) button:hover {
        background:
            linear-gradient(
                135deg,
                #5c2300,
                #d45a00
            );

        border-color: #ff9d00;
        color: white;
    }

    /* ANNUAL */

    div[data-testid="stDownloadButton"]:nth-of-type(3) button {
        background:
            linear-gradient(
                135deg,
                #4a2100,
                #c96a00
            );

        border: 1px solid #ffb000;
        color: #fff0d0;
    }

    div[data-testid="stDownloadButton"]:nth-of-type(3) button:hover {
        background:
            linear-gradient(
                135deg,
                #693000,
                #ed8500
            );

        border-color: #ffc400;
        color: white;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    qc = pd.read_csv(
        "florida_fire_harmonized_qc.csv"
    )

    raw = pd.read_csv(
        "florida_fire_harmonized_raw.csv"
    )

    overlap = pd.read_csv(
        "florida_calibration_overlap_qc.csv"
    )

    qc["acq_date"] = pd.to_datetime(
        qc["acq_date"]
    )

    raw["acq_date"] = pd.to_datetime(
        raw["acq_date"]
    )

    overlap["acq_date"] = pd.to_datetime(
        overlap["acq_date"]
    )

    return qc, raw, overlap


try:

    harmonized_qc, harmonized_raw, overlap_qc = load_data()

except Exception:

    st.error(
        "Could not load the datasets."
    )

    st.write(
        "Make sure these files are beside app.py:"
    )

    st.code(
        """
florida_fire_harmonized_qc.csv
florida_fire_harmonized_raw.csv
florida_calibration_overlap_qc.csv
        """
    )

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "🔥 Fire Harmonization"
)

dataset_mode = st.sidebar.radio(
    "Dataset",
    [
        "Primary · QC",
        "Raw · Sensitivity"
    ]
)


if dataset_mode == "Primary · QC":

    data = harmonized_qc

else:

    data = harmonized_raw


min_year = int(
    data["acq_date"]
    .dt
    .year
    .min()
)

max_year = int(
    data["acq_date"]
    .dt
    .year
    .max()
)


year_range = st.sidebar.slider(
    "Analysis period",
    min_year,
    max_year,
    (min_year, max_year)
)


filtered = data[
    data["acq_date"]
    .dt
    .year
    .between(
        year_range[0],
        year_range[1]
    )
].copy()


# ============================================================
# TITLE
# ============================================================

st.title(
    "🔥 FIRE HARMONIZATION"
)

st.subheader(
    "Florida active-fire activity from MODIS and Suomi-NPP VIIRS"
)

st.write(
    "A harmonized satellite record designed to reduce the apparent "
    "discontinuity associated with the MODIS → VIIRS sensor transition."
)


# ============================================================
# 01 · SYSTEM OVERVIEW
# ============================================================

st.header(
    "01 · System Overview"
)


total_frp = (
    filtered["frp_harmonized"]
    .sum()
)

cell_days = len(
    filtered
)

mean_frp = (
    filtered["frp_harmonized"]
    .mean()
)

median_frp = (
    filtered["frp_harmonized"]
    .median()
)


c1, c2, c3, c4 = st.columns(4)


c1.metric(
    "Cell-days",
    f"{cell_days:,}"
)

c2.metric(
    "Total FRP",
    f"{total_frp:,.0f} MW"
)

c3.metric(
    "Mean FRP",
    f"{mean_frp:,.1f} MW"
)

c4.metric(
    "Median FRP",
    f"{median_frp:,.1f} MW"
)


# ============================================================
# 02 · SPATIAL DISTRIBUTION
# ============================================================

st.header(
    "02 · Spatial Distribution"
)

st.write(
    "Total harmonized fire activity across the common 0.05° grid."
)


spatial_summary = (
    filtered
    .groupby(
        [
            "grid_lat",
            "grid_lon"
        ],
        as_index=False
    )
    .agg(
        total_frp=(
            "frp_harmonized",
            "sum"
        ),

        cell_days=(
            "frp_harmonized",
            "count"
        )
    )
)


spatial_summary["latitude"] = (
    spatial_summary["grid_lat"]
    + 0.025
)

spatial_summary["longitude"] = (
    spatial_summary["grid_lon"]
    + 0.025
)

spatial_summary["log_total_frp"] = (
    np.log10(
        spatial_summary[
            "total_frp"
        ].clip(lower=0)
        + 1
    )
)


spatial_map = (
    alt.Chart(
        spatial_summary
    )
    .mark_square(
        size=55
    )
    .encode(

        longitude=alt.Longitude(
            "longitude:Q",
            title="Longitude"
        ),

        latitude=alt.Latitude(
            "latitude:Q",
            title="Latitude"
        ),

        color=alt.Color(
            "log_total_frp:Q",
            title="log₁₀(Total FRP + 1)",

            scale=alt.Scale(
                scheme="inferno"
            )
        ),

        tooltip=[

            alt.Tooltip(
                "latitude:Q",
                title="Latitude",
                format=".3f"
            ),

            alt.Tooltip(
                "longitude:Q",
                title="Longitude",
                format=".3f"
            ),

            alt.Tooltip(
                "total_frp:Q",
                title="Total FRP",
                format=",.1f"
            ),

            alt.Tooltip(
                "cell_days:Q",
                title="Cell-days",
                format=","
            )
        ]
    )
    .properties(
        height=560
    )
    .project(
        type="mercator"
    )
    .interactive()
)


st.altair_chart(
    spatial_map,
    use_container_width=True
)


# ============================================================
# 03 · 3D FIRE ACTIVITY MAP
# ============================================================

st.header(
    "🔥 3D Fire Activity Map"
)

st.write(
    "Interactive 3D view of harmonized fire activity. Each column represents "
    "a 0.05° grid cell; column height uses a logarithmic FRP scale so extreme "
    "fire values do not hide lower-intensity activity."
)

if not spatial_summary.empty:

    fire_3d = spatial_summary.copy()

    # Use the 99th percentile as a visual ceiling so a few extreme cells
    # do not flatten the rest of the map.
    p99_frp = fire_3d["total_frp"].quantile(0.99)

    if not np.isfinite(p99_frp) or p99_frp <= 0:
        p99_frp = max(float(fire_3d["total_frp"].max()), 1.0)

    fire_3d["display_frp"] = fire_3d["total_frp"].clip(
        lower=0,
        upper=p99_frp
    )

    fire_3d["log_display_frp"] = np.log10(
        fire_3d["display_frp"] + 1
    )

    max_log = max(
        float(fire_3d["log_display_frp"].max()),
        1.0
    )

   # Height is intentionally logarithmic. Tooltip values remain the
    # original FRP values.
    fire_3d["elevation"] = (
        fire_3d["log_display_frp"]
        / max_log
        * 40000
        + 100
    )
    

    # Fire-style RGB ramp: dark red -> orange -> yellow.
    intensity = (
        fire_3d["log_display_frp"]
        / max_log
    ).clip(0, 1)

    fire_3d["color"] = intensity.apply(
        lambda x: [
            255,
            int(35 + 180 * x),
            int(15 + 55 * x),
            210
        ]
    )

    layer_3d = pdk.Layer(
        "ColumnLayer",
        data=fire_3d,
        get_position="[longitude, latitude]",
        get_elevation="elevation",
        elevation_scale=1,
        radius=2200,
        coverage=0.85,
        get_fill_color="color",
        pickable=True,
        auto_highlight=True,
    )

    view_state_3d = pdk.ViewState(
        latitude=27.75,
        longitude=-82.5,
        zoom=5.7,
        pitch=55,
        bearing=-8
    )

    deck_3d = pdk.Deck(
        layers=[layer_3d],
        initial_view_state=view_state_3d,
        tooltip={
            "html": (
                "<b>Florida Fire Activity</b><br/>"
                "Latitude: {latitude}<br/>"
                "Longitude: {longitude}<br/>"
                "Total FRP: {total_frp} MW<br/>"
                "Cell-days: {cell_days}<br/>"
                "Visual height: logarithmic FRP"
            ),
            "style": {
                "backgroundColor": "#160b05",
                "color": "#ffffff"
            }
        },
        map_style=None
    )

    st.pydeck_chart(
        deck_3d,
        use_container_width=True
    )

    st.caption(
        "Drag to rotate · Scroll to zoom · Right-drag to tilt. "
        "Column height is a visual encoding of total harmonized FRP; "
        "the tooltip reports the actual FRP."
    )

else:

    st.info(
        "No fire activity is available for the selected analysis period."
    )



# ============================================================
# 03 · FIRE ACTIVITY THROUGH TIME
# ============================================================

st.header(
    "03 · Fire Activity Through Time"
)

st.write(
    "Annual harmonized FRP across the selected period."
)


annual = (
    filtered
    .assign(
        year=filtered[
            "acq_date"
        ].dt.year
    )
    .groupby(
        "year",
        as_index=False
    )
    .agg(

        total_frp=(
            "frp_harmonized",
            "sum"
        ),

        cell_days=(
            "frp_harmonized",
            "count"
        )
    )
)


annual_chart = (
    alt.Chart(
        annual
    )
    .mark_bar()
    .encode(

        x=alt.X(
            "year:O",
            title="Year"
        ),

        y=alt.Y(
            "total_frp:Q",
            title="Total Harmonized FRP (MW)"
        ),

        color=alt.Color(
            "total_frp:Q",

            scale=alt.Scale(
                scheme="inferno"
            ),

            legend=None
        ),

        tooltip=[

            "year",

            alt.Tooltip(
                "total_frp:Q",
                title="Total FRP",
                format=",.0f"
            ),

            alt.Tooltip(
                "cell_days:Q",
                title="Cell-days",
                format=","
            )
        ]
    )
    .properties(
        height=420
    )
)


st.altair_chart(
    annual_chart,
    use_container_width=True
)


# ============================================================
# 04 · MODIS–VIIRS DETECTION MISMATCH
# ============================================================

st.header(
    "04 · MODIS–VIIRS Detection Mismatch"
)

st.write(
    "Coincident cell-days are only a subset of the combined detections. "
    "A missing detection should not automatically be interpreted as zero FRP."
)


both = 28027
modis_only = 71237
viirs_only = 80400


m1, m2, m3 = st.columns(3)


m1.metric(
    "Both detected",
    f"{both:,}"
)

m2.metric(
    "MODIS only",
    f"{modis_only:,}"
)

m3.metric(
    "VIIRS only",
    f"{viirs_only:,}"
)


detection_data = pd.DataFrame(
    [
        [2012, 1540, 2006, 3764],
        [2013, 1897, 2046, 4310],
        [2014, 1966, 2047, 4496],
        [2015, 1766, 2015, 4472],
        [2016, 1921, 2117, 5445],
        [2017, 2461, 2234, 5824],
        [2018, 2058, 1962, 5114],
        [2019, 1872, 1969, 5466],
        [2020, 2072, 2001, 5541],
        [2021, 2136, 2204, 5809],
        [2022, 2114, 2331, 5969],
        [2023, 2031, 2291, 6175],
        [2024, 1747, 2119, 6576],
        [2025, 1733, 2250, 7651],
        [2026, 713, 1532, 3788]
    ],

    columns=[
        "year",
        "Both",
        "MODIS-only",
        "VIIRS-only"
    ]
)


detection_long = detection_data.melt(
    id_vars="year",
    var_name="category",
    value_name="count"
)


detection_chart = (
    alt.Chart(
        detection_long
    )
    .mark_bar()
    .encode(

        x=alt.X(
            "year:O",
            title="Year"
        ),

        y=alt.Y(
            "count:Q",
            title="Cell-days"
        ),

        color=alt.Color(
            "category:N",

            title="Detection",

            scale=alt.Scale(
                scheme="inferno"
            )
        ),

        tooltip=[
            "year",
            "category",

            alt.Tooltip(
                "count:Q",
                title="Cell-days",
                format=","
            )
        ]
    )
    .properties(
        height=420
    )
)


st.altair_chart(
    detection_chart,
    use_container_width=True
)


st.caption(
    "2026 is partial-year data through September 25."
)


# ============================================================
# 05 · SENSOR TRANSITION
# ============================================================

st.header(
    "05 · 2011 → 2012 Sensor Transition"
)


transition = data[
    data["acq_date"]
    .dt
    .year
    .isin(
        [2011, 2012]
    )
].copy()


transition_yearly = (
    transition
    .assign(
        year=transition[
            "acq_date"
        ].dt.year
    )
    .groupby(
        "year",
        as_index=False
    )
    .agg(

        total_frp=(
            "frp_harmonized",
            "sum"
        ),

        cell_days=(
            "frp_harmonized",
            "count"
        ),

        mean_frp=(
            "frp_harmonized",
            "mean"
        ),

        median_frp=(
            "frp_harmonized",
            "median"
        )
    )
)


if len(transition_yearly) == 2:

    row_2011 = transition_yearly[
        transition_yearly["year"] == 2011
    ].iloc[0]

    row_2012 = transition_yearly[
        transition_yearly["year"] == 2012
    ].iloc[0]


    total_change = (
        row_2012["total_frp"]
        /
        row_2011["total_frp"]
        - 1
    ) * 100


    cell_change = (
        row_2012["cell_days"]
        /
        row_2011["cell_days"]
        - 1
    ) * 100


    mean_change = (
        row_2012["mean_frp"]
        /
        row_2011["mean_frp"]
        - 1
    ) * 100


    median_change = (
        row_2012["median_frp"]
        /
        row_2011["median_frp"]
        - 1
    ) * 100


    t1, t2, t3, t4 = st.columns(4)


    t1.metric(
        "Cell-days",
        f"{cell_change:+.1f}%"
    )

    t2.metric(
        "Total FRP",
        f"{total_change:+.1f}%"
    )

    t3.metric(
        "Mean FRP",
        f"{mean_change:+.1f}%"
    )

    t4.metric(
        "Median FRP",
        f"{median_change:+.1f}%"
    )


st.info(
    "This is treated as an apparent sensor-transition discontinuity, "
    "rather than assuming that underlying fire activity suddenly changed."
)


# ============================================================
# 06 · MODIS → VIIRS CALIBRATION
# ============================================================

st.header(
    "06 · MODIS → VIIRS Calibration"
)


OLS_SLOPE = 0.316162
OLS_INTERCEPT = 24.701681


c1, c2, c3, c4 = st.columns(4)


c1.metric(
    "Training period",
    "2012–2021"
)

c2.metric(
    "Training observations",
    "19,689"
)

c3.metric(
    "Slope",
    "0.3162"
)

c4.metric(
    "Intercept",
    "24.70 MW"
)


st.code(
    "VIIRS = 0.316162 × MODIS + 24.701681",
    language="text"
)


# ============================================================
# CALIBRATION SCATTER
# ============================================================

scatter = overlap_qc.copy()


scatter["predicted_viirs"] = (
    OLS_SLOPE
    * scatter["frp_modis"]
    + OLS_INTERCEPT
)


scatter_chart = (
    alt.Chart(
        scatter
    )
    .mark_circle(
        opacity=0.25,
        size=25
    )
    .encode(

        x=alt.X(
            "frp_modis:Q",
            title="MODIS FRP (MW)",

            scale=alt.Scale(
                domain=[0, 5000]
            )
        ),

        y=alt.Y(
            "frp_viirs:Q",
            title="VIIRS FRP (MW)",

            scale=alt.Scale(
                domain=[0, 5000]
            )
        ),

        tooltip=[

            alt.Tooltip(
                "frp_modis:Q",
                title="MODIS",
                format=".2f"
            ),

            alt.Tooltip(
                "frp_viirs:Q",
                title="VIIRS",
                format=".2f"
            )
        ]
    )
    .properties(
        height=500
    )
)


line_data = pd.DataFrame(
    {
        "x": [
            0,
            5000
        ],

        "y": [
            OLS_INTERCEPT,
            OLS_SLOPE * 5000
            + OLS_INTERCEPT
        ]
    }
)


line = (
    alt.Chart(
        line_data
    )
    .mark_line(
        strokeDash=[
            6,
            4
        ]
    )
    .encode(
        x="x:Q",
        y="y:Q"
    )
)


st.altair_chart(
    scatter_chart + line,
    use_container_width=True
)


# ============================================================
# 07 · MODEL VALIDATION
# ============================================================

st.header(
    "07 · Model Validation"
)


metrics = pd.DataFrame(
    {
        "Model": [
            "Proportional",
            "OLS",
            "Log-Log",
            "Huber"
        ],

        "RMSE": [
            112.51,
            109.43,
            113.73,
            111.21
        ],

        "MAE": [
            39.26,
            45.13,
            37.82,
            38.59
        ],

        "R²": [
            0.1440,
            0.1902,
            0.1253,
            0.1637
        ],

        "Bias": [
            -23.91,
            -1.66,
            -24.20,
            -19.89
        ]
    }
)


st.dataframe(
    metrics,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 08 · 2026 VALIDATION
# ============================================================

st.header(
    "08 · 2026 Untouched Validation"
)


v1, v2, v3, v4 = st.columns(4)


v1.metric(
    "Observations",
    "713"
)

v2.metric(
    "RMSE",
    "173.86 MW"
)

v3.metric(
    "MAE",
    "60.46 MW"
)

v4.metric(
    "R²",
    "0.076"
)


# ============================================================
# 09 · DATASET COMPOSITION
# ============================================================

st.header(
    "09 · Dataset Composition"
)


source_counts = (
    data[
        "source_sensor"
    ]
    .value_counts()
    .rename_axis(
        "source_sensor"
    )
    .reset_index(
        name="cell_days"
    )
)


source_chart = (
    alt.Chart(
        source_counts
    )
    .mark_bar()
    .encode(

        x=alt.X(
            "source_sensor:N",
            title=None
        ),

        y=alt.Y(
            "cell_days:Q",
            title="Cell-days"
        ),

        color=alt.Color(
            "source_sensor:N",

            scale=alt.Scale(
                scheme="inferno"
            ),

            legend=None
        ),

        tooltip=[

            "source_sensor",

            alt.Tooltip(
                "cell_days:Q",
                title="Cell-days",
                format=","
            )
        ]
    )
    .properties(
        height=350
    )
)


st.altair_chart(
    source_chart,
    use_container_width=True
)


st.write(
    "**2002–2011:** calibrated MODIS"
)

st.write(
    "**2012–2026:** native Suomi-NPP VIIRS"
)

st.write(
    "The overlapping period is not double-counted."
)


# ============================================================
# 10 · ANNUAL HISTORICAL SUMMARY
# ============================================================

st.header(
    "10 · Annual Historical Summary"
)


annual_full = (
    data
    .assign(
        year=data[
            "acq_date"
        ].dt.year
    )
    .groupby(
        "year",
        as_index=False
    )
    .agg(

        cell_days=(
            "frp_harmonized",
            "count"
        ),

        total_frp=(
            "frp_harmonized",
            "sum"
        ),

        mean_frp=(
            "frp_harmonized",
            "mean"
        ),

        median_frp=(
            "frp_harmonized",
            "median"
        )
    )
)


st.dataframe(
    annual_full.round(2),
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 11 · DOWNLOAD DATA
# ============================================================

st.header(
    "11 · Download Data"
)


d1, d2, d3 = st.columns(3)


with d1:

    st.download_button(
        "🔥 Download QC Dataset",

        harmonized_qc.to_csv(
            index=False
        ),

        "florida_fire_harmonized_qc.csv",

        "text/csv",

        use_container_width=True
    )


with d2:

    st.download_button(
        "🌋 Download Raw Dataset",

        harmonized_raw.to_csv(
            index=False
        ),

        "florida_fire_harmonized_raw.csv",

        "text/csv",

        use_container_width=True
    )


with d3:

    st.download_button(
        "📊 Download Annual Summary",

        annual_full.to_csv(
            index=False
        ),

        "florida_annual_harmonized_summary.csv",

        "text/csv",

        use_container_width=True
    )


# ============================================================
# 12 · DATA EXPLORER
# ============================================================

st.header(
    "12 · Data Explorer"
)


preview_n = st.slider(
    "Rows to display",
    5,
    100,
    20
)


st.dataframe(
    filtered.head(
        preview_n
    ),
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 13 · METHODOLOGY
# ============================================================

st.header(
    "13 · Methodology"
)


with st.expander(
    "How does the harmonization work?"
):

    st.markdown(
        """
        **Satellite data**

        MODIS Collection 6.1 and Suomi-NPP VIIRS 375 m active-fire
        data are used for Florida.

        **Spatial harmonization**

        Detections are aggregated into a common 0.05° × 0.05° grid.

        **Temporal harmonization**

        Detections are aggregated by grid cell and acquisition date,
        producing cell-day observations.

        **Calibration**

        Coincident MODIS and VIIRS observations from 2012–2021 are
        used to estimate the calibration relationship.

        **Calibration equation**

        VIIRS = 0.316162 × MODIS + 24.701681

        **Final timeline**

        2002–2011 → calibrated MODIS

        2012–2026 → native VIIRS

        **Important limitation**

        Harmonization places the records on a common FRP reference
        scale, but does not eliminate every difference in satellite
        detection.
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🔥 NASA Space Apps Challenge 2026 · MODIS + Suomi-NPP VIIRS · Florida"
)