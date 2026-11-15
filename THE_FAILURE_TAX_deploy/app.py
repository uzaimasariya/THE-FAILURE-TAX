
import os
import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# THE FAILURE TAX
# Reliability-to-Profit Intelligence Dashboard
# --------------------------------------------------

st.set_page_config(
    page_title="THE FAILURE TAX | VoltRelay",
    page_icon="⚡",
    layout="wide"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "outputs")

st.markdown("""
<style>
.main {
    background-color: #0b1120;
}
[data-testid="stMetric"] {
    background: #172238;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #263750;
}
[data-testid="stMetricLabel"] {
    color: #a9bad2;
}
[data-testid="stMetricValue"] {
    color: #ffffff;
}
h1, h2, h3 {
    color: #f1f5f9;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()


rdi = load_data("reliability_debt.csv")
failure_tax = load_data("failure_tax.csv")
priority = load_data("investment_priority.csv")
scenarios = load_data("investment_scenarios.csv")
ml_results = load_data("ml_model_comparison.csv")
importance = load_data("ml_feature_importance.csv")
station_metrics = load_data("station_metrics.csv")


def money(value):
    return f"₹{value:,.0f}"


def show_missing(message):
    st.info(message)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("⚡ THE FAILURE TAX")
st.sidebar.caption("VoltRelay | Reliability Intelligence")

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Executive Overview",
        "Reliability Intelligence",
        "Failure Tax",
        "Investment Simulator",
        "ML Intelligence"
    ]
)

st.sidebar.divider()
st.sidebar.caption("EV Battery-Swapping Network")
st.sidebar.caption("Data period: Jan 2024 – Jun 2025")


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("⚡ THE FAILURE TAX")
st.markdown(
    "### An Explainable Reliability-to-Profit Intelligence System"
)
st.caption(
    "Turning operational failures into measurable financial decisions."
)

st.divider()


# --------------------------------------------------
# 1. EXECUTIVE OVERVIEW
# --------------------------------------------------

if page == "Executive Overview":

    st.subheader("Network performance at a glance")

    if not failure_tax.empty:
        total_attempts = failure_tax["total_attempts"].sum()
        completed = failure_tax["completed_swaps"].sum()
        failed = failure_tax["failed_swaps"].sum()
        revenue = failure_tax["completed_revenue_inr"].sum()
        exposure = failure_tax[
            "estimated_failed_attempt_revenue_exposure"
        ].sum()

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Total Attempts", f"{total_attempts:,.0f}")
        c2.metric("Completed Swaps", f"{completed:,.0f}")
        c3.metric("Failed Swaps", f"{failed:,.0f}")
        c4.metric("Failure Rate", f"{failed / total_attempts * 100:.2f}%")

        st.divider()

        c1, c2 = st.columns(2)
        c1.metric("Completed Revenue", money(revenue))
        c2.metric("Estimated Gross Failure Exposure", money(exposure))

        st.caption(
            "Failure exposure is an estimated gross opportunity, "
            "not confirmed lost revenue or profit."
        )

        if "city" in failure_tax.columns:
            city_data = (
                failure_tax.groupby("city", as_index=False)
                .agg(
                    failed_swaps=("failed_swaps", "sum"),
                    exposure=(
                        "estimated_failed_attempt_revenue_exposure",
                        "sum"
                    )
                )
            )

            st.subheader("Failure exposure by city")
            fig = px.bar(
                city_data.sort_values("exposure", ascending=False),
                x="city",
                y="exposure",
                color="exposure",
                labels={
                    "city": "City",
                    "exposure": "Estimated exposure (₹)"
                },
                title="Where is the failure tax concentrated?"
            )
            st.plotly_chart(fig, use_container_width=True)

    else:
        show_missing("Export failure_tax_df from Colab to display network KPIs.")

    if not rdi.empty:
        st.subheader("Network reliability risk")

        if "risk_category" in rdi.columns:
            risk_counts = (
                rdi["risk_category"]
                .value_counts()
                .rename_axis("Risk category")
                .reset_index(name="Stations")
            )

            fig = px.pie(
                risk_counts,
                names="Risk category",
                values="Stations",
                hole=0.55,
                title="Station risk distribution"
            )
            st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# 2. RELIABILITY INTELLIGENCE
# --------------------------------------------------

elif page == "Reliability Intelligence":

    st.subheader("Reliability Debt Index")

    if not rdi.empty:
        if "risk_category" in rdi.columns:
            risk_filter = st.multiselect(
                "Filter risk category",
                sorted(rdi["risk_category"].dropna().unique()),
                default=sorted(rdi["risk_category"].dropna().unique())
            )
            filtered = rdi[
                rdi["risk_category"].isin(risk_filter)
            ].copy()
        else:
            filtered = rdi.copy()

        if "RDI" in filtered.columns:
            st.metric("Average Reliability Debt Index",
                      f"{filtered['RDI'].mean():.2f}")

        if {"station_id", "RDI"}.issubset(filtered.columns):
            top_risk = filtered.sort_values(
                "RDI", ascending=False
            ).head(20)

            fig = px.bar(
                top_risk,
                x="RDI",
                y="station_id",
                color="RDI",
                orientation="h",
                title="Top 20 stations by Reliability Debt Index"
            )
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Station risk register")
        st.dataframe(filtered, use_container_width=True)

        if "city" in rdi.columns and "RDI" in rdi.columns:
            city_risk = (
                rdi.groupby("city", as_index=False)
                .agg(
                    average_RDI=("RDI", "mean"),
                    stations=("station_id", "nunique")
                )
                .sort_values("average_RDI", ascending=False)
            )

            fig = px.bar(
                city_risk,
                x="city",
                y="average_RDI",
                color="average_RDI",
                title="Average Reliability Debt by city"
            )
            st.plotly_chart(fig, use_container_width=True)

    else:
        show_missing("Export rdi_df to display station reliability intelligence.")


# --------------------------------------------------
# 3. FAILURE TAX
# --------------------------------------------------

elif page == "Failure Tax":

    st.subheader("The financial cost of unreliability")

    if not failure_tax.empty:

        if "estimated_failed_attempt_revenue_exposure" in failure_tax.columns:
            total_exposure = failure_tax[
                "estimated_failed_attempt_revenue_exposure"
            ].sum()

            st.metric(
                "Estimated Gross Failure Exposure",
                money(total_exposure)
            )

        if "city" in failure_tax.columns:
            city_filter = st.selectbox(
                "Select city",
                ["All cities"] + sorted(
                    failure_tax["city"].dropna().unique().tolist()
                )
            )

            selected = failure_tax.copy()
            if city_filter != "All cities":
                selected = selected[
                    selected["city"] == city_filter
                ]

            st.dataframe(
                selected.sort_values(
                    "estimated_failed_attempt_revenue_exposure",
                    ascending=False
                ),
                use_container_width=True
            )

            city_exposure = (
                failure_tax.groupby("city", as_index=False)
                ["estimated_failed_attempt_revenue_exposure"].sum()
            )

            fig = px.bar(
                city_exposure,
                x="city",
                y="estimated_failed_attempt_revenue_exposure",
                title="Estimated failure exposure by city"
            )
            st.plotly_chart(fig, use_container_width=True)

        st.warning(
            "This is a gross opportunity estimate. It assumes a failed "
            "attempt could have become a completed swap at the station's "
            "average realized revenue. It is not audited lost revenue."
        )

    else:
        show_missing("Export failure_tax_df to display financial exposure.")


# --------------------------------------------------
# 4. INVESTMENT SIMULATOR
# --------------------------------------------------

elif page == "Investment Simulator":

    st.subheader("Turn reliability risk into investment priorities")

    if not priority.empty:

        st.markdown("#### Highest-priority stations")

        display_cols = [
            col for col in [
                "station_id", "city", "zone", "RDI",
                "estimated_failed_attempt_revenue_exposure",
                "investment_priority_score"
            ]
            if col in priority.columns
        ]

        st.dataframe(
            priority[display_cols].head(20),
            use_container_width=True
        )

    else:
        show_missing("Export investment_df to show station priorities.")

    if not scenarios.empty:

        st.divider()
        st.markdown("#### Investment cost and payback scenarios")

        scenario_name = st.selectbox(
            "Choose improvement scenario",
            scenarios["scenario"].dropna().unique()
        )

        selected_scenario = scenarios[
            scenarios["scenario"] == scenario_name
        ].copy()

        st.dataframe(
            selected_scenario,
            use_container_width=True
        )

        if {
            "upgrade_cost_per_station",
            "estimated_payback_months"
        }.issubset(selected_scenario.columns):

            fig = px.bar(
                selected_scenario,
                x="upgrade_cost_per_station",
                y="estimated_payback_months",
                title="Estimated payback period by upgrade cost",
                labels={
                    "upgrade_cost_per_station": "Upgrade cost per station (₹)",
                    "estimated_payback_months": "Payback (months)"
                }
            )
            st.plotly_chart(fig, use_container_width=True)

        st.caption(
            "Scenario estimates depend on assumed improvement rates, "
            "upgrade costs and historical contribution. They are not "
            "measured intervention results."
        )

    else:
        show_missing("Export investment_scenarios_df to show the simulator.")


# --------------------------------------------------
# 5. ML INTELLIGENCE
# --------------------------------------------------

elif page == "ML Intelligence":

    st.subheader("Machine-learning failure intelligence")

    if not ml_results.empty:

        st.markdown("#### Model comparison")

        st.dataframe(
            ml_results.round(4),
            use_container_width=True
        )

        metric_columns = [
            col for col in [
                "Accuracy", "Failure Precision",
                "Failure Recall", "F1 Score",
                "ROC-AUC", "PR-AUC"
            ]
            if col in ml_results.columns
        ]

        if metric_columns and "Model" in ml_results.columns:
            plot_data = ml_results.melt(
                id_vars="Model",
                value_vars=metric_columns,
                var_name="Metric",
                value_name="Score"
            )

            fig = px.bar(
                plot_data,
                x="Metric",
                y="Score",
                color="Model",
                barmode="group",
                title="Model performance comparison"
            )
            st.plotly_chart(fig, use_container_width=True)

    else:
        show_missing("Export results_df to display ML model results.")

    if not importance.empty:

        st.divider()
        st.markdown("#### Most important failure predictors")

        top_features = importance.head(20).sort_values(
            "importance", ascending=True
        )

        fig = px.bar(
            top_features,
            x="importance",
            y="feature",
            orientation="h",
            title="Top 20 Random Forest feature importances"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.caption(
            "Feature importance indicates predictive contribution in this "
            "model, not causation. The model without queue wait has limited "
            "predictive performance."
        )

    else:
        show_missing("Export importance_df to display feature importance.")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()
st.caption(
    "THE FAILURE TAX | VoltRelay | "
    "Explainable Reliability-to-Profit Intelligence"
)
st.caption(
    "Research prototype. Financial and predictive estimates are "
    "subject to stated assumptions and data limitations."
)
