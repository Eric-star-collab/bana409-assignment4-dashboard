"""A compact weekly sales review for a regional supermarket manager."""
from pathlib import Path
import pandas as pd
import streamlit as st
import altair as alt

st.set_page_config(page_title="Northstar | Weekly Sales", page_icon="🛒", layout="wide")

@st.cache_data
def load_data():
    data = pd.read_csv(Path(__file__).parent / "data" / "supermarket_sales.csv")
    data["Date"] = pd.to_datetime(data["Date"], format="%m/%d/%Y")
    data["Week"] = data["Date"].dt.to_period("W-SUN").dt.start_time
    return data

df = load_data()
st.title("Northstar Team | Weekly Sales Review")
st.caption("For the regional sales manager: identify a branch or product line that needs a sales follow-up this week.")
st.caption("Data: Jan 1–Mar 30, 2019 · frozen Kaggle snapshot · intended production refresh: nightly; manager review: Monday morning.")

with st.sidebar:
    st.header("Review scope")
    city = st.selectbox("Store / city", ["All stores"] + sorted(df["City"].unique().tolist()))
    complete_weeks = sorted(w for w in df.Week.unique()
        if w >= df.Date.min() and w + pd.Timedelta(days=6) <= df.Date.max())
    week = st.selectbox("Complete week starting Monday", complete_weeks,
        index=len(complete_weeks)-1, format_func=lambda d: pd.Timestamp(d).strftime("%b %d, %Y"))
    st.caption("Partial boundary weeks are excluded from the week selector. Store labels use City because the source's Branch labels conflict with its location description.")

scope = df if city == "All stores" else df[df.City == city]
current = scope[scope.Week == week]
previous = scope[(scope.Week == week - pd.Timedelta(days=7)) & scope.Week.isin(complete_weeks)]
revenue = float(current.Sales.sum())
previous_revenue = float(previous.Sales.sum())
change = (revenue / previous_revenue - 1) if previous_revenue > 0 else None
cols = st.columns(3)
cols[0].metric("Sales including tax", f"${revenue:,.2f}", f"{change:+.1%} vs prior week" if change is not None else None)
cols[1].metric("Transactions", f"{current['Invoice ID'].nunique():,}")
cols[2].metric("Average transaction", f"${revenue / len(current):,.2f}" if len(current) else "No transactions")

if change is None:
    st.info("No complete prior-week comparison is available at this snapshot boundary.")
elif change < -0.15:
    st.warning(f"Review needed: sales are down {abs(change):.1%} from the previous complete week. Check transaction counts, the product-line breakdown, and stock availability before changing promotions.")
else:
    st.success(f"Weekly sales change: {change:+.1%}. Review the product-line breakdown before choosing a follow-up.")

left, right = st.columns([1.2, 1])
with left:
    st.subheader("1 · Is the decline persistent?")
    history = (scope[scope.Week.isin(complete_weeks) & (scope.Week <= week)]
        .groupby("Week", as_index=False).Sales.sum().tail(8))
    chart = alt.Chart(history).mark_line(point=True, color="#166e71").encode(
        x=alt.X("Week:T", title="Complete week starting Monday"),
        y=alt.Y("Sales:Q", title="Sales including tax (USD)", scale=alt.Scale(zero=True)),
        tooltip=[alt.Tooltip("Week:T", format="%Y-%m-%d"), alt.Tooltip("Sales:Q", format="$,.2f")])
    st.altair_chart(chart, width="stretch")
with right:
    st.subheader("2 · Which product lines changed?")
    categories = sorted(df["Product line"].unique())
    now = current.groupby("Product line").Sales.sum().reindex(categories, fill_value=0)
    before = previous.groupby("Product line").Sales.sum().reindex(categories, fill_value=0)
    comparison = pd.DataFrame({"Product line": categories, "Change": (now-before).to_numpy()})
    bars = alt.Chart(comparison).mark_bar().encode(
        x=alt.X("Change:Q", title="Sales change vs prior week (USD)"),
        y=alt.Y("Product line:N", sort="x", title=None),
        color=alt.condition(alt.datum.Change < 0, alt.value("#ba624f"), alt.value("#166e71")),
        tooltip=["Product line", alt.Tooltip("Change:Q", format="$,.2f")])
    if len(previous):
        st.altair_chart(bars, width="stretch")
    else:
        st.info("Select a later week to compare product lines against a complete previous week.")

st.caption("Sales are the source's tax-inclusive USD amounts; sales do not measure profit. The CSV's 'gross income' equals its 5% tax field, so it is excluded. No inventory or stock-out data is available: a sales decline triggers investigation, not an automatic reorder.")
with st.expander("Audit selected transactions"):
    st.dataframe(current[["Invoice ID", "Date", "City", "Product line", "Quantity", "Sales"]], hide_index=True)
    st.download_button("Download selected transactions", current.to_csv(index=False),
                       "selected_transactions.csv", "text/csv")
with st.expander("Source and interpretation"):
    st.markdown("[Kaggle: Supermarket Sales Dataset, Fares Ashraf](https://www.kaggle.com/datasets/faresashraf1001/supermarket-sales)")
    st.write("1,000 transaction rows; January–March 2019; three city locations. The uploader describes historical supermarket transactions in Myanmar, but independent collection provenance and whether the data is simulated are not established. Treat this as a retrospective demonstration.")
