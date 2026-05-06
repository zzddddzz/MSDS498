from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Portfolio Action Console",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)


ACTION_COLORS = {
    "Retain": "#1f7a5c",
    "Reprice": "#a15c22",
    "Review": "#b83f48",
    "Monitor": "#37658f",
}


@dataclass(frozen=True)
class PortfolioScope:
    records: int = 228_711
    variables: int = 42
    years: str = "2017-2019"
    mid_year_lapse: float = 0.071
    any_lapse: float = 0.181


SCOPE = PortfolioScope()


def add_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ink: #15211e;
            --muted: #65736e;
            --line: #d9e1dd;
            --surface: #ffffff;
            --wash: #f4f7f5;
            --green: #1f7a5c;
            --gold: #b6862f;
            --coral: #b83f48;
            --blue: #37658f;
        }

        .stApp {
            background: linear-gradient(180deg, #f7faf8 0%, #eef4f1 100%);
            color: var(--ink);
        }

        .block-container {
            max-width: 1280px;
            padding-top: 1.25rem;
            padding-bottom: 2rem;
        }

        h1, h2, h3, p {
            letter-spacing: 0;
        }

        div[data-testid="stVerticalBlock"] > div:has(.console-shell) {
            gap: 0.85rem;
        }

        .console-shell {
            border: 1px solid var(--line);
            background: rgba(255, 255, 255, 0.96);
            border-radius: 8px;
            box-shadow: 0 20px 45px rgba(36, 58, 50, 0.08);
            padding: 18px;
        }

        .topbar {
            align-items: start;
            display: grid;
            gap: 16px;
            grid-template-columns: minmax(0, 1fr) auto;
            margin-bottom: 16px;
        }

        .title-block h1 {
            color: var(--ink);
            font-size: 2rem;
            font-weight: 740;
            line-height: 1.05;
            margin: 0 0 8px;
        }

        .title-block p {
            color: var(--muted);
            font-size: 0.98rem;
            line-height: 1.5;
            margin: 0;
            max-width: 820px;
        }

        .status-card {
            align-self: stretch;
            background: var(--wash);
            border: 1px solid var(--line);
            border-left: 5px solid var(--green);
            border-radius: 8px;
            min-width: 260px;
            padding: 12px 14px;
        }

        .status-card span,
        .metric-card span,
        .segment-card span,
        .action-card span,
        .method-card span {
            color: var(--muted);
            display: block;
            font-size: 0.72rem;
            font-weight: 720;
            letter-spacing: 0.08em;
            line-height: 1.25;
            margin-bottom: 8px;
            text-transform: uppercase;
        }

        .status-card strong {
            color: var(--ink);
            display: block;
            font-size: 1rem;
            line-height: 1.35;
        }

        .metric-grid {
            display: grid;
            gap: 12px;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            margin-bottom: 16px;
        }

        .metric-card {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 8px;
            min-height: 138px;
            padding: 14px;
        }

        .metric-card strong {
            color: var(--ink);
            display: block;
            font-size: 1.65rem;
            font-weight: 760;
            line-height: 1.1;
            margin-bottom: 8px;
            overflow-wrap: anywhere;
        }

        .metric-card p {
            color: var(--muted);
            font-size: 0.85rem;
            line-height: 1.42;
            margin: 0;
        }

        .metric-card.accent-green {
            border-top: 4px solid var(--green);
        }

        .metric-card.accent-gold {
            border-top: 4px solid var(--gold);
        }

        .metric-card.accent-coral {
            border-top: 4px solid var(--coral);
        }

        .metric-card.accent-blue {
            border-top: 4px solid var(--blue);
        }

        .section-title {
            align-items: center;
            display: flex;
            gap: 10px;
            justify-content: space-between;
            margin: 8px 0 10px;
        }

        .section-title h2 {
            color: var(--ink);
            font-size: 1.08rem;
            font-weight: 740;
            line-height: 1.2;
            margin: 0;
        }

        .section-title p {
            color: var(--muted);
            font-size: 0.82rem;
            line-height: 1.35;
            margin: 0;
            text-align: right;
        }

        .panel {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 14px;
        }

        .segment-list {
            display: grid;
            gap: 10px;
        }

        .segment-card {
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 12px;
        }

        .segment-card strong {
            color: var(--ink);
            display: block;
            font-size: 1rem;
            font-weight: 740;
            line-height: 1.3;
            margin-bottom: 6px;
            overflow-wrap: anywhere;
        }

        .segment-meta {
            color: var(--muted);
            display: grid;
            font-size: 0.82rem;
            gap: 4px;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            line-height: 1.35;
        }

        .segment-foot {
            align-items: center;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            justify-content: space-between;
            margin-top: 10px;
        }

        .action-pill {
            border-radius: 999px;
            color: #ffffff;
            display: inline-flex;
            font-size: 0.76rem;
            font-weight: 740;
            line-height: 1;
            padding: 7px 9px;
        }

        .priority-score {
            color: var(--ink);
            font-size: 0.86rem;
            font-weight: 720;
        }

        .action-grid {
            display: grid;
            gap: 12px;
            grid-template-columns: repeat(4, minmax(0, 1fr));
        }

        .action-card,
        .method-card {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 14px;
        }

        .action-card strong,
        .method-card strong {
            color: var(--ink);
            display: block;
            font-size: 1rem;
            line-height: 1.35;
            margin-bottom: 7px;
        }

        .action-card p,
        .method-card p {
            color: var(--muted);
            font-size: 0.86rem;
            line-height: 1.45;
            margin: 0;
        }

        .source-note {
            color: var(--muted);
            font-size: 0.78rem;
            line-height: 1.45;
            margin-top: 10px;
        }

        div[data-testid="stSelectbox"] label,
        div[data-testid="stMultiSelect"] label {
            color: var(--ink);
            font-size: 0.82rem;
            font-weight: 700;
        }

        @media (max-width: 980px) {
            .topbar,
            .metric-grid,
            .action-grid {
                grid-template-columns: 1fr;
            }

            .status-card {
                min-width: 0;
            }

            .section-title {
                align-items: start;
                flex-direction: column;
            }

            .section-title p {
                text-align: left;
            }
        }

        @media (max-width: 640px) {
            .block-container {
                padding-left: 0.75rem;
                padding-right: 0.75rem;
            }

            .console-shell {
                padding: 13px;
            }

            .title-block h1 {
                font-size: 1.55rem;
            }

            .segment-meta {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def load_segment_data() -> pd.DataFrame:
    segment_summary = Path(__file__).with_name("data") / "segment_summary.csv"
    if segment_summary.exists():
        return pd.read_csv(segment_summary)

    records = [
        {
            "year": 2017,
            "segment": "Broker PPO, age 55-64",
            "product": "PPO",
            "channel": "Broker",
            "age_band": "55-64",
            "policy_years": 24430,
            "mid_year_lapse_rate": 0.089,
            "any_lapse_rate": 0.214,
            "claim_pm": 624,
            "premium_pm": 701,
            "expected_value": 0.86,
            "retention_urgency": 0.81,
            "premium_adequacy": 0.11,
            "utilization_index": 1.28,
            "recommended_action": "Retain",
            "owner": "Retention lead",
            "next_action": "Prioritize outreach and broker-specific renewal review.",
        },
        {
            "year": 2017,
            "segment": "Employer HMO, age 45-54",
            "product": "HMO",
            "channel": "Employer",
            "age_band": "45-54",
            "policy_years": 21980,
            "mid_year_lapse_rate": 0.057,
            "any_lapse_rate": 0.162,
            "claim_pm": 588,
            "premium_pm": 557,
            "expected_value": 0.44,
            "retention_urgency": 0.62,
            "premium_adequacy": -0.06,
            "utilization_index": 1.19,
            "recommended_action": "Reprice",
            "owner": "Pricing lead",
            "next_action": "Review premium adequacy and claim concentration before renewal.",
        },
        {
            "year": 2017,
            "segment": "Direct family PPO, age 35-44",
            "product": "PPO",
            "channel": "Direct",
            "age_band": "35-44",
            "policy_years": 18610,
            "mid_year_lapse_rate": 0.104,
            "any_lapse_rate": 0.229,
            "claim_pm": 532,
            "premium_pm": 546,
            "expected_value": 0.55,
            "retention_urgency": 0.74,
            "premium_adequacy": 0.03,
            "utilization_index": 1.06,
            "recommended_action": "Review",
            "owner": "Portfolio lead",
            "next_action": "Investigate why profitable policies are leaving early.",
        },
        {
            "year": 2017,
            "segment": "Digital HDHP, age 26-34",
            "product": "HDHP",
            "channel": "Digital",
            "age_band": "26-34",
            "policy_years": 20575,
            "mid_year_lapse_rate": 0.068,
            "any_lapse_rate": 0.171,
            "claim_pm": 318,
            "premium_pm": 391,
            "expected_value": 0.72,
            "retention_urgency": 0.48,
            "premium_adequacy": 0.19,
            "utilization_index": 0.74,
            "recommended_action": "Monitor",
            "owner": "Portfolio lead",
            "next_action": "Track utilization drift before applying retention spend.",
        },
        {
            "year": 2018,
            "segment": "Broker HMO, age 55-64",
            "product": "HMO",
            "channel": "Broker",
            "age_band": "55-64",
            "policy_years": 17745,
            "mid_year_lapse_rate": 0.082,
            "any_lapse_rate": 0.205,
            "claim_pm": 641,
            "premium_pm": 609,
            "expected_value": 0.38,
            "retention_urgency": 0.86,
            "premium_adequacy": -0.05,
            "utilization_index": 1.33,
            "recommended_action": "Reprice",
            "owner": "Pricing lead",
            "next_action": "Separate pricing action from blanket retention incentives.",
        },
        {
            "year": 2018,
            "segment": "Employer PPO, age 45-54",
            "product": "PPO",
            "channel": "Employer",
            "age_band": "45-54",
            "policy_years": 19420,
            "mid_year_lapse_rate": 0.061,
            "any_lapse_rate": 0.177,
            "claim_pm": 574,
            "premium_pm": 664,
            "expected_value": 0.79,
            "retention_urgency": 0.68,
            "premium_adequacy": 0.14,
            "utilization_index": 1.08,
            "recommended_action": "Retain",
            "owner": "Retention lead",
            "next_action": "Protect profitable group renewals with targeted outreach.",
        },
        {
            "year": 2018,
            "segment": "Direct HDHP, age 35-44",
            "product": "HDHP",
            "channel": "Direct",
            "age_band": "35-44",
            "policy_years": 15470,
            "mid_year_lapse_rate": 0.052,
            "any_lapse_rate": 0.139,
            "claim_pm": 402,
            "premium_pm": 416,
            "expected_value": 0.53,
            "retention_urgency": 0.42,
            "premium_adequacy": 0.03,
            "utilization_index": 0.88,
            "recommended_action": "Monitor",
            "owner": "Portfolio lead",
            "next_action": "Keep in baseline monitoring unless lapse accelerates.",
        },
        {
            "year": 2018,
            "segment": "Digital PPO, age 26-34",
            "product": "PPO",
            "channel": "Digital",
            "age_band": "26-34",
            "policy_years": 16890,
            "mid_year_lapse_rate": 0.118,
            "any_lapse_rate": 0.251,
            "claim_pm": 355,
            "premium_pm": 449,
            "expected_value": 0.81,
            "retention_urgency": 0.77,
            "premium_adequacy": 0.21,
            "utilization_index": 0.79,
            "recommended_action": "Retain",
            "owner": "Retention lead",
            "next_action": "Use low-cost digital retention before renewal window closes.",
        },
        {
            "year": 2019,
            "segment": "Broker PPO, age 65+",
            "product": "PPO",
            "channel": "Broker",
            "age_band": "65+",
            "policy_years": 18240,
            "mid_year_lapse_rate": 0.047,
            "any_lapse_rate": 0.153,
            "claim_pm": 711,
            "premium_pm": 635,
            "expected_value": 0.31,
            "retention_urgency": 0.58,
            "premium_adequacy": -0.12,
            "utilization_index": 1.46,
            "recommended_action": "Reprice",
            "owner": "Pricing lead",
            "next_action": "Review claim burden and premium adequacy before growth push.",
        },
        {
            "year": 2019,
            "segment": "Employer HDHP, age 45-54",
            "product": "HDHP",
            "channel": "Employer",
            "age_band": "45-54",
            "policy_years": 14380,
            "mid_year_lapse_rate": 0.073,
            "any_lapse_rate": 0.181,
            "claim_pm": 486,
            "premium_pm": 512,
            "expected_value": 0.57,
            "retention_urgency": 0.64,
            "premium_adequacy": 0.05,
            "utilization_index": 0.96,
            "recommended_action": "Review",
            "owner": "Portfolio lead",
            "next_action": "Confirm whether lapse is concentrated by employer size.",
        },
        {
            "year": 2019,
            "segment": "Direct HMO, age 35-44",
            "product": "HMO",
            "channel": "Direct",
            "age_band": "35-44",
            "policy_years": 20515,
            "mid_year_lapse_rate": 0.095,
            "any_lapse_rate": 0.233,
            "claim_pm": 462,
            "premium_pm": 503,
            "expected_value": 0.68,
            "retention_urgency": 0.73,
            "premium_adequacy": 0.08,
            "utilization_index": 0.93,
            "recommended_action": "Retain",
            "owner": "Retention lead",
            "next_action": "Focus retention on members with positive margin and early churn.",
        },
        {
            "year": 2019,
            "segment": "Digital HMO, age 26-34",
            "product": "HMO",
            "channel": "Digital",
            "age_band": "26-34",
            "policy_years": 20456,
            "mid_year_lapse_rate": 0.065,
            "any_lapse_rate": 0.158,
            "claim_pm": 336,
            "premium_pm": 363,
            "expected_value": 0.61,
            "retention_urgency": 0.46,
            "premium_adequacy": 0.07,
            "utilization_index": 0.76,
            "recommended_action": "Monitor",
            "owner": "Portfolio lead",
            "next_action": "Watch movement but avoid high-touch intervention for now.",
        },
    ]

    df = pd.DataFrame.from_records(records)
    df["priority_score"] = (
        (df["retention_urgency"] * 42)
        + (df["mid_year_lapse_rate"] * 260)
        + ((1 - df["expected_value"]) * 16)
        + (df["utilization_index"] * 7)
    ).round(1)
    return df


def weighted_average(df: pd.DataFrame, column: str) -> float:
    if df.empty or df["policy_years"].sum() == 0:
        return 0.0
    return float((df[column] * df["policy_years"]).sum() / df["policy_years"].sum())


def pct(value: float) -> str:
    return f"{value:.1%}"


def money(value: float) -> str:
    return f"${value:,.0f}"


def metric_card(label: str, value: str, note: str, accent: str) -> str:
    return (
        f"<section class='metric-card accent-{accent}'>"
        f"<span>{escape(label)}</span>"
        f"<strong>{escape(value)}</strong>"
        f"<p>{escape(note)}</p>"
        "</section>"
    )


def segment_card(row: pd.Series) -> str:
    color = ACTION_COLORS.get(str(row["recommended_action"]), "#65736e")
    return (
        "<article class='segment-card'>"
        f"<span>{escape(str(row['recommended_action']))} candidate</span>"
        f"<strong>{escape(str(row['segment']))}</strong>"
        "<div class='segment-meta'>"
        f"<div>Mid-year lapse: <b>{pct(float(row['mid_year_lapse_rate']))}</b></div>"
        f"<div>Claim PMPM: <b>{money(float(row['claim_pm']))}</b></div>"
        f"<div>Premium PMPM: <b>{money(float(row['premium_pm']))}</b></div>"
        f"<div>Value index: <b>{float(row['expected_value']):.2f}</b></div>"
        "</div>"
        "<div class='segment-foot'>"
        f"<span class='action-pill' style='background:{color};'>{escape(str(row['recommended_action']))}</span>"
        f"<span class='priority-score'>Priority {float(row['priority_score']):.1f}</span>"
        "</div>"
        "</article>"
    )


def render_header(filtered: pd.DataFrame) -> None:
    highest_action = (
        filtered.groupby("recommended_action")["policy_years"].sum().sort_values(ascending=False).index[0]
        if not filtered.empty
        else "Review"
    )
    st.markdown(
        f"""
        <div class="console-shell">
            <div class="topbar">
                <div class="title-block">
                    <h1>Portfolio Action Console</h1>
                    <p>
                        Executive dashboard for health insurance retention, pricing, claims, and portfolio profitability.
                        Segment results are translated into retain, reprice, monitor, and review actions.
                    </p>
                </div>
                <aside class="status-card">
                    <span>Current view</span>
                    <strong>{len(filtered):,} segments in view</strong>
                    <strong>{escape(highest_action)} is the largest action lane</strong>
                </aside>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_grid(filtered: pd.DataFrame) -> None:
    records_in_view = int(filtered["policy_years"].sum()) if not filtered.empty else 0
    avg_mid_lapse = weighted_average(filtered, "mid_year_lapse_rate")
    avg_any_lapse = weighted_average(filtered, "any_lapse_rate")
    avg_claim = weighted_average(filtered, "claim_pm")
    cards = [
        metric_card(
            "Portfolio scope",
            f"{SCOPE.records:,}",
            f"{SCOPE.variables} variables across {SCOPE.years}; filtered view contains {records_in_view:,} policy-years.",
            "green",
        ),
        metric_card(
            "Mid-year lapse",
            pct(avg_mid_lapse or SCOPE.mid_year_lapse),
            "Early lapse pressure used for retention urgency and action ranking.",
            "gold",
        ),
        metric_card(
            "Any lapse",
            pct(avg_any_lapse or SCOPE.any_lapse),
            "Combined lapse exposure across early and expiration-related lapses.",
            "coral",
        ),
        metric_card(
            "Claim burden",
            money(avg_claim),
            "Average PMPM claim pressure for the selected segment view.",
            "blue",
        ),
    ]
    st.markdown("<div class='metric-grid'>" + "".join(cards) + "</div>", unsafe_allow_html=True)


def decision_quadrant(filtered: pd.DataFrame) -> go.Figure:
    plot_df = filtered.copy()
    plot_df["policy_size"] = plot_df["policy_years"].clip(lower=5000)
    fig = px.scatter(
        plot_df,
        x="expected_value",
        y="retention_urgency",
        size="policy_size",
        color="recommended_action",
        color_discrete_map=ACTION_COLORS,
        hover_name="segment",
        hover_data={
            "policy_years": ":,",
            "mid_year_lapse_rate": ":.1%",
            "any_lapse_rate": ":.1%",
            "claim_pm": ":$,.0f",
            "premium_pm": ":$,.0f",
            "policy_size": False,
            "expected_value": ":.2f",
            "retention_urgency": ":.2f",
        },
    )
    fig.add_hline(y=0.64, line_width=1, line_dash="dash", line_color="#9aa7a2")
    fig.add_vline(x=0.62, line_width=1, line_dash="dash", line_color="#9aa7a2")
    fig.add_annotation(
        x=0.86,
        y=0.9,
        text="Protect value",
        showarrow=False,
        font={"size": 12, "color": "#1f7a5c"},
    )
    fig.add_annotation(
        x=0.36,
        y=0.9,
        text="Price review",
        showarrow=False,
        font={"size": 12, "color": "#a15c22"},
    )
    fig.add_annotation(
        x=0.84,
        y=0.36,
        text="Watch list",
        showarrow=False,
        font={"size": 12, "color": "#37658f"},
    )
    fig.add_annotation(
        x=0.38,
        y=0.36,
        text="Business review",
        showarrow=False,
        font={"size": 12, "color": "#b83f48"},
    )
    fig.update_traces(
        marker={"line": {"width": 1.5, "color": "#ffffff"}, "opacity": 0.9},
        selector={"mode": "markers"},
    )
    fig.update_layout(
        height=430,
        margin={"l": 12, "r": 12, "t": 10, "b": 8},
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        legend={"orientation": "h", "y": -0.18, "x": 0, "title": None},
        xaxis={
            "title": "Expected value index",
            "range": [0.24, 0.92],
            "gridcolor": "#edf2ef",
            "zeroline": False,
        },
        yaxis={
            "title": "Retention urgency",
            "range": [0.30, 0.94],
            "gridcolor": "#edf2ef",
            "zeroline": False,
        },
        font={"family": "Inter, Arial, sans-serif", "color": "#15211e"},
    )
    return fig


def render_action_cards(filtered: pd.DataFrame) -> None:
    action_defs = {
        "Retain": (
            "High value with elevated lapse pressure.",
            "Use retention outreach where expected value justifies action.",
        ),
        "Reprice": (
            "Claim burden or premium adequacy pressure.",
            "Review pricing before adding more retention spend.",
        ),
        "Review": (
            "Mixed signal segment that needs diagnosis.",
            "Separate behavior, channel, and product drivers before choosing a lever.",
        ),
        "Monitor": (
            "Stable or lower urgency segment.",
            "Keep in the governance view and intervene only if indicators move.",
        ),
    }
    pieces = []
    totals = filtered.groupby("recommended_action")["policy_years"].sum().to_dict()
    for action, (title, body) in action_defs.items():
        value = totals.get(action, 0)
        pieces.append(
            "<section class='action-card'>"
            f"<span style='color:{ACTION_COLORS[action]};'>{escape(action)}</span>"
            f"<strong>{escape(title)}</strong>"
            f"<p>{escape(body)} Current view: {value:,} policy-years.</p>"
            "</section>"
        )
    st.markdown("<div class='action-grid'>" + "".join(pieces) + "</div>", unsafe_allow_html=True)


def render_table(filtered: pd.DataFrame) -> None:
    table_df = (
        filtered.sort_values("priority_score", ascending=False)
        .loc[
            :,
            [
                "segment",
                "year",
                "recommended_action",
                "policy_years",
                "mid_year_lapse_rate",
                "any_lapse_rate",
                "claim_pm",
                "premium_pm",
                "premium_adequacy",
                "priority_score",
                "owner",
            ],
        ]
        .rename(
            columns={
                "segment": "Segment",
                "year": "Year",
                "recommended_action": "Action",
                "policy_years": "Policy-years",
                "mid_year_lapse_rate": "Mid-year lapse",
                "any_lapse_rate": "Any lapse",
                "claim_pm": "Claim PMPM",
                "premium_pm": "Premium PMPM",
                "premium_adequacy": "Premium adequacy",
                "priority_score": "Priority",
                "owner": "Owner",
            }
        )
    )
    table_df["Mid-year lapse"] = table_df["Mid-year lapse"] * 100
    table_df["Any lapse"] = table_df["Any lapse"] * 100
    st.dataframe(
        table_df,
        width="stretch",
        hide_index=True,
        column_config={
            "Policy-years": st.column_config.NumberColumn(format="%d"),
            "Mid-year lapse": st.column_config.ProgressColumn(
                format="%.1f%%",
                min_value=0,
                max_value=14,
            ),
            "Any lapse": st.column_config.ProgressColumn(
                format="%.1f%%",
                min_value=0,
                max_value=28,
            ),
            "Claim PMPM": st.column_config.NumberColumn(format="$%d"),
            "Premium PMPM": st.column_config.NumberColumn(format="$%d"),
            "Premium adequacy": st.column_config.NumberColumn(format="%.2f"),
            "Priority": st.column_config.NumberColumn(format="%.1f"),
        },
    )


def main() -> None:
    add_css()
    df = load_segment_data()

    header_slot = st.empty()

    with st.container():
        col_year, col_product, col_channel, col_action = st.columns([1.05, 1.35, 1.35, 1.25])
        with col_year:
            year_options = ["All"] + [str(year) for year in sorted(df["year"].unique())]
            selected_year = st.selectbox("Year", year_options, index=0)
        with col_product:
            product_options = sorted(df["product"].unique())
            selected_products = st.multiselect("Products", product_options, default=product_options)
        with col_channel:
            channel_options = sorted(df["channel"].unique())
            selected_channels = st.multiselect("Channels", channel_options, default=channel_options)
        with col_action:
            action_options = ["Retain", "Reprice", "Review", "Monitor"]
            selected_actions = st.multiselect("Action lanes", action_options, default=action_options)

    filtered = df.copy()
    if selected_year != "All":
        filtered = filtered[filtered["year"] == int(selected_year)]
    filtered = filtered[
        filtered["product"].isin(selected_products)
        & filtered["channel"].isin(selected_channels)
        & filtered["recommended_action"].isin(selected_actions)
    ]

    if filtered.empty:
        st.warning("No segments match the current filters.")
        return

    with header_slot.container():
        render_header(filtered)
    render_metric_grid(filtered)

    tab_console, tab_detail, tab_method = st.tabs(["Action console", "Segment detail", "Evidence and method"])

    with tab_console:
        left, right = st.columns([1.55, 1], gap="large")
        with left:
            st.markdown(
                """
                <div class="section-title">
                    <h2>Decision quadrant</h2>
                    <p>Value and urgency determine the first management lane.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.plotly_chart(decision_quadrant(filtered), width="stretch", config={"displayModeBar": False})

        with right:
            st.markdown(
                """
                <div class="section-title">
                    <h2>Highest priority segments</h2>
                    <p>Ranked by urgency, lapse, value, and utilization pressure.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            top_segments = filtered.sort_values("priority_score", ascending=False).head(4)
            st.markdown(
                "<div class='segment-list'>" + "".join(segment_card(row) for _, row in top_segments.iterrows()) + "</div>",
                unsafe_allow_html=True,
            )

        st.markdown(
            """
            <div class="section-title">
                <h2>Action plan</h2>
                <p>Portfolio work is separated by decision type instead of one broad retention list.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_action_cards(filtered)

    with tab_detail:
        st.markdown(
            """
            <div class="section-title">
                <h2>Ranked segment view</h2>
                <p>Business-facing table for the executive brief and supporting analysis.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_table(filtered)

        selected_segment = st.selectbox(
            "Segment drill-down",
            filtered.sort_values("priority_score", ascending=False)["segment"].tolist(),
        )
        row = filtered[filtered["segment"] == selected_segment].iloc[0]
        st.markdown(
            f"""
            <div class="panel">
                <div class="section-title">
                    <h2>{escape(selected_segment)}</h2>
                    <p>{escape(str(row["recommended_action"]))} lane assigned to {escape(str(row["owner"]))}.</p>
                </div>
                <div class="action-grid">
                    {metric_card("Mid-year lapse", pct(float(row["mid_year_lapse_rate"])), "Early lapse pressure for this segment.", "gold")}
                    {metric_card("Premium adequacy", f"{float(row["premium_adequacy"]):+.2f}", "Positive means premium exceeds claim burden.", "green" if float(row["premium_adequacy"]) >= 0 else "coral")}
                    {metric_card("Utilization index", f"{float(row["utilization_index"]):.2f}", "Relative service use signal.", "blue")}
                    {metric_card("Next action", str(row["next_action"]), "Owner-facing action statement.", "coral")}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with tab_method:
        st.markdown(
            """
            <div class="section-title">
                <h2>Evidence and method</h2>
                <p>Built for a public demo without exposing the raw internal workbook.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class="action-grid">
                <section class="method-card">
                    <span>Evidence base</span>
                    <strong>{SCOPE.records:,} policy-year records</strong>
                    <p>The project scope references {SCOPE.variables} variables across {SCOPE.years}, combining premium, claims, lapse, utilization, product, channel, and demographic fields.</p>
                </section>
                <section class="method-card">
                    <span>Target definitions</span>
                    <strong>Lapse states are separated</strong>
                    <p>Mid-year lapse is treated as an early-retention signal. Any-lapse combines early and expiration-related lapse exposure.</p>
                </section>
                <section class="method-card">
                    <span>Decision logic</span>
                    <strong>Rank, classify, act</strong>
                    <p>Segments are compared on lapse risk, expected claim burden, premium adequacy, and expected value, then assigned to retain, reprice, monitor, or review.</p>
                </section>
                <section class="method-card">
                    <span>Publish posture</span>
                    <strong>Segment-level demo data</strong>
                    <p>The app ships with a non-sensitive segment summary. A private CSV can replace it later at <code>data/segment_summary.csv</code> using the same columns.</p>
                </section>
            </div>
            <p class="source-note">
                Public Streamlit deployment path: repository <code>zzddddzz/MSDS498</code>, branch <code>main</code>,
                entrypoint <code>streamlit_app.py</code>.
            </p>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
