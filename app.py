import streamlit as st
import openai

# OpenAI API Key
openai.api_key = "your_openai_api_key"

# Streamlit Page Config
st.set_page_config(page_title="Series A Readiness", layout="centered", page_icon="📈")

# Custom CSS for Background
def add_background_color():
    background_css = """
    <style>
    body {
        background-color: #EAE8E8;
    }
    </style>
    """
    st.markdown(background_css, unsafe_allow_html=True)

# Add background color
add_background_color()

# Title and subtitle
st.title("📊 Cherry's Guide to Assessing Series A Readiness")
st.subheader("Fill in the metrics below to assess your score and get an overview on whether you are ready to raise a Series A round.")

# Initialize session state for skip buttons
if "skipped_metrics" not in st.session_state:
    st.session_state["skipped_metrics"] = {}

# Function to toggle skip status in session state
def toggle_skip(kpi_name):
    st.session_state["skipped_metrics"][kpi_name] = not st.session_state["skipped_metrics"].get(kpi_name, False)

# Function to create a slider with skip functionality
def create_slider_with_skip(number, label, min_val, max_val, default_val, step, format_string):
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### {number}. {label}")
        value = st.slider(
            label,
            min_value=min_val,
            max_value=max_val,
            value=default_val,
            step=step,
            format=format_string,
            key=f"slider_{label}"
        )
    with col2:
        skip_label = "Skip" if not st.session_state["skipped_metrics"].get(label, False) else "Unskip"
        if st.button(skip_label, key=f"skip_{label}", on_click=toggle_skip, args=(label,)):
            pass  # Skip state toggled via `toggle_skip`

    # Return None if KPI is skipped
    if st.session_state["skipped_metrics"].get(label, False):
        return None
    return value

# Function to create a categorical slider with skip functionality
def create_categorical_slider_with_skip(number, label, options, default_index=0):
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### {number}. {label}")
        value = st.select_slider(
            label,
            options=options,
            value=options[default_index],
            key=f"slider_{label}"
        )
    with col2:
        skip_label = "Skip" if not st.session_state["skipped_metrics"].get(label, False) else "Unskip"
        if st.button(skip_label, key=f"skip_{label}", on_click=toggle_skip, args=(label,)):
            pass  # Skip state toggled via `toggle_skip`

    # Return None if KPI is skipped
    if st.session_state["skipped_metrics"].get(label, False):
        return None
    return value

# Initialize dictionaries for quartile checks and metric scores
quartile_values = {}
metrics_values = {}

# ARR Metric
arr_value = create_slider_with_skip(1, "Annual Recurring Revenue (ARR)", 1.0, 3.0, 1.0, 0.01, "%.2fm")
quartile_values["ARR"] = arr_value is not None and arr_value >= 2.25
metrics_values["ARR"] = ((arr_value - 1.0) / (3.0 - 1.0) * 10) if arr_value is not None else None

# ARR Growth Metric
arr_growth_value = create_slider_with_skip(2, "ARR Growth", 150, 500, 150, 10, "%d%%")
quartile_values["ARR Growth"] = arr_growth_value is not None and arr_growth_value >= 375
metrics_values["ARR Growth"] = ((arr_growth_value - 150) / (500 - 150) * 10) if arr_growth_value is not None else None

# Late Stage Pipeline Growth Metric
pipeline_growth_value = create_slider_with_skip(3, "Late Stage Pipeline Growth", 100, 300, 100, 10, "%d%%")
quartile_values["Late Stage Pipeline Growth"] = pipeline_growth_value is not None and pipeline_growth_value >= 225
metrics_values["Late Stage Pipeline Growth"] = ((pipeline_growth_value - 100) / (300 - 100) * 10) if pipeline_growth_value is not None else None

# Fully Ramped Quota Carriers Metric
quota_carriers_value = create_slider_with_skip(4, "Fully Ramped Quota Carriers", 0.0, 3.0, 0.0, 0.1, "%.1f months")
quartile_values["Fully Ramped Quota Carriers"] = quota_carriers_value is not None and quota_carriers_value <= 1.0
metrics_values["Fully Ramped Quota Carriers"] = ((quota_carriers_value - 0.0) / (3.0 - 0.0) * 10) if quota_carriers_value is not None else None

# Net Revenue Retention Metric
nrr_value = create_slider_with_skip(5, "Net Revenue Retention (NRR)", 100, 300, 100, 10, "%d%%")
quartile_values["Net Revenue Retention"] = nrr_value is not None and nrr_value >= 250
metrics_values["Net Revenue Retention"] = ((nrr_value - 100) / (300 - 100) * 10) if nrr_value is not None else None

# ACV Expansion Metric
acv_expansion_value = create_slider_with_skip(6, "ACV Expansion", 15, 50, 15, 1, "%d%%")
quartile_values["ACV Expansion"] = acv_expansion_value is not None and acv_expansion_value >= 35
metrics_values["ACV Expansion"] = ((acv_expansion_value - 15) / (50 - 15) * 10) if acv_expansion_value is not None else None

# Repeatability Metric
repeatability_value = create_categorical_slider_with_skip(7, "Repeatability", ["Early", "Moderate", "Strong"], default_index=0)
quartile_values["Repeatability"] = repeatability_value == "Strong"
metrics_values["Repeatability"] = {"Early": 0, "Moderate": 5, "Strong": 10}[repeatability_value] if repeatability_value is not None else None

# CAC Payback Metric
cac_payback_value = create_slider_with_skip(8, "CAC Payback", 6.0, 15.0, 15.0, 0.1, "%.1f months")
quartile_values["CAC Payback"] = cac_payback_value is not None and cac_payback_value <= 9.0
metrics_values["CAC Payback"] = ((15.0 - cac_payback_value) / (15.0 - 6.0) * 10) if cac_payback_value is not None else None

# Burn Multiple Metric
burn_multiple_value = create_slider_with_skip(9, "Burn Multiple", 1.5, 2.0, 2.0, 0.01, "%.2f")
quartile_values["Burn Multiple"] = burn_multiple_value is not None and burn_multiple_value <= 1.7
metrics_values["Burn Multiple"] = ((2.0 - burn_multiple_value) / (2.0 - 1.5) * 10) if burn_multiple_value is not None else None

# Compute Average Score for Non-Skipped Metrics
valid_scores = [v for v in metrics_values.values() if v is not None]
average_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0

# Determine Categories for Series A Readiness
categories = []
if sum(1 for k, v in quartile_values.items() if v and k in ["ARR Growth", "Late Stage Pipeline Growth", "Fully Ramped Quota Carriers", "ACV Expansion"]) >= 2:
    categories.append("exciting growth potential")
if sum(1 for k, v in quartile_values.items() if v and k in ["CAC Payback", "Burn Multiple", "Repeatability"]) >= 2:
    categories.append("upcoming profitability perspectives")
if sum(1 for k, v in quartile_values.items() if v and k in ["ARR", "Net Revenue Retention", "Repeatability"]) >= 2:
    categories.append("significant market confirmation")

# Display "You are raising a Series A based on..."
if categories:
    categories_display = " & ".join(categories)
    st.markdown(f"<h3 style='color: green;'>You are raising a Series A round based on {categories_display}.</h3>", unsafe_allow_html=True)
else:
    st.markdown("<h3 style='color: red;'>You are not ready to raise a Series A round but are doing so based on feels.</h3>", unsafe_allow_html=True)

# Display Average Score
st.markdown(f"<h2 style='color: blue;'>Your overall Cherry Score: {average_score:.2f}/10</h2>", unsafe_allow_html=True)

# Recommendations (Expanded ChatGPT advice)
def generate_advice(metrics_values, quartile_values):
    strengths = [k for k, v in quartile_values.items() if v]
    weaknesses = [k for k, v in quartile_values.items() if not v]

    strength_text = f"The metrics {', '.join(strengths)} are performing strongly, showcasing your readiness in these areas."
    weakness_text = ". ".join([f"The metric {k} needs improvement to better align with investor expectations." for k in weaknesses])

    recommendation_text = (
        "Focus on leveraging your strong metrics to highlight growth and profitability potential. Engage with investors "
        "by presenting clear data and a compelling narrative around your success metrics.\n\n"
        "For weaker metrics, consider targeted strategies such as enhancing customer retention, streamlining CAC, and expanding "
        "your pipeline through strategic partnerships or market expansion. Addressing these areas will make your pitch more robust."
    )

    return f"### Strengths:\n{strength_text}\n\n### Weaknesses:\n{weakness_text}\n\n### Recommendations:\n{recommendation_text}"

st.markdown(generate_advice(metrics_values, quartile_values))
