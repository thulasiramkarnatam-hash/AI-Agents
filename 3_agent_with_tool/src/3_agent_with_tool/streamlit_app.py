"""Streamlit UI for calculating the difference between two dates."""

from datetime import date

import streamlit as st

from .date_difference import calculate_date_difference


def main() -> None:
    """Render the date-difference calculator."""
    st.set_page_config(page_title="Date Difference Agent", page_icon="📅")
    st.title("📅 Date Difference Agent")
    st.write("Choose two dates to calculate complete years, remaining days, and total days.")

    date1 = st.date_input("Date 1", value=date(2020, 1, 1))
    date2 = st.date_input("Date 2", value=date.today())

    if st.button("Calculate difference", type="primary"):
        result = calculate_date_difference(date1, date2)
        st.subheader("Difference")
        first, second, third = st.columns(3)
        first.metric("Complete years", result.years)
        second.metric("Remaining days", result.days)
        third.metric("Total days", result.total_days)
        st.caption(
            f"Normalized interval: {result.start_date.isoformat()} "
            f"to {result.end_date.isoformat()}"
        )
        if result.total_days == 0:
            st.info("The two dates are the same.")


if __name__ == "__main__":
    main()
