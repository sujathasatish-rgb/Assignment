import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
import altair as alt

# MySQL connection details
user = "root"
password = ""
host = "localhost"
database = "sports_tennis"

# Create a SQLAlchemy engine
engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}")

# Function to fetch data from MySQL database into a DataFrame
def fetch_data(query):
    return pd.read_sql(query, engine)



# Sidebar for tab selection
tab_selection = st.sidebar.radio("Select a Tab", ("Summary Statistics and Leaderboard", "Competitors details"))

# Top 10 Ranked Competitors Query
top_ranked_query = """
    SELECT c.Name AS Competitor, cr.Rank
    FROM Competitors c
    JOIN CompetitorRanking cr ON c.competitor_id = cr.competitor_id
    ORDER BY cr.Rank ASC
    LIMIT 10
"""
top_ranked_df = fetch_data(top_ranked_query)

# Top 10 Competitors with High Points Query
top_points_query = """
    SELECT c.Name AS Competitor, cr.Points
    FROM Competitors c
    JOIN CompetitorRanking cr ON c.competitor_id = cr.competitor_id
    ORDER BY cr.Points DESC
    LIMIT 10
"""
top_points_df = fetch_data(top_points_query)

# Apply custom CSS for styling
st.markdown("""
    <style>
        .summary-table th, .competitors-table th, .matches-table th {
            background-color: #4CAF50; 
            color: white;
            font-size: 16px;
            text-align: center;
        }
        .summary-table td, .competitors-table td, .matches-table td {
            font-size: 14px;
            text-align: center;
            padding: 8px;
        }
        .summary-table, .competitors-table, .matches-table {
            border-collapse: collapse;
            width: 100%;
        }
        .summary-table, .competitors-table, .matches-table, .summary-table th, .competitors-table th, .matches-table th, .summary-table td, .competitors-table td, .matches-table td {
            border: 1px solid #ddd;
        }
        .summary-table tr:nth-child(even), .competitors-table tr:nth-child(even), .matches-table tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        .summary-table tr:hover, .competitors-table tr:hover, .matches-table tr:hover {
            background-color: #ddd;
        }
        /* Add scrolling to the competitors and matches tables */
        .competitors-table-wrapper, .matches-table-wrapper {
            max-height: 400px;
            overflow-y: auto;
        }
    </style>
""", unsafe_allow_html=True)

# Summary Statistics Tab
if tab_selection == "Summary Statistics and Leaderboard":
    # Title
    st.title("Tennis Sports Homepage Dashboard")
    st.header("Summary Statistics")
    
    # Example summary statistics queries
    total_competitors_query = "SELECT COUNT(DISTINCT c.competitor_id) AS total_competitors FROM Competitors c JOIN CompetitorRanking cr ON c.competitor_id = cr.competitor_id"
    total_competitors = fetch_data(total_competitors_query)['total_competitors'][0]

    countries_represented_query = "SELECT COUNT(DISTINCT c.country) AS countries_represented FROM Competitors c JOIN CompetitorRanking cr ON c.competitor_id = cr.competitor_id"
    countries_represented = fetch_data(countries_represented_query)['countries_represented'][0]

    highest_points_query = "SELECT MAX(cr.points) AS highest_points FROM Competitors c JOIN CompetitorRanking cr ON c.competitor_id = cr.competitor_id"
    highest_points = fetch_data(highest_points_query)['highest_points'][0]
    
    insights_data = {
        "Insights": ["Total Competitors", "Countries Represented", "Highest Points Scored"],
        "Value": [total_competitors, countries_represented, highest_points]
    }
    insights_df = pd.DataFrame(insights_data)
    st.markdown("""
        <table class="summary-table">
            <tr><th>Insights</th><th>Value</th></tr>
            <tr><td>Total Competitors</td><td>{}</td></tr>
            <tr><td>Countries Represented</td><td>{}</td></tr>
            <tr><td>Highest Points Scored</td><td>{}</td></tr>
        </table>
    """.format(total_competitors, countries_represented, highest_points), unsafe_allow_html=True)
    import altair as alt

if tab_selection == "Summary Statistics and Leaderboard":
    st.header("Leaderboard")
    st.subheader("Top 10 Ranked Competitors")
    if not top_ranked_df.empty:
        # Sorting the DataFrame by rank for better chart alignment
        top_ranked_df = top_ranked_df.sort_values(by="Rank")

        # Creating the bar chart
        chart_ranked = alt.Chart(top_ranked_df).mark_bar().encode(
            x=alt.X("Rank:O", sort=None, title="Rank"),
            y=alt.Y("Competitor:N", sort=None, title="Competitor"),
            color=alt.Color("Rank:O", scale=alt.Scale(scheme="blues"), legend=None),
            tooltip=["Competitor", "Rank"]
        ).properties(
            width=700,  # Adjust width for better fit
            height=400,  # Adjust height for better visibility
            title=""
        ).configure_title(
            fontSize=18,
            anchor="start",
            color="gray"
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14
        ).configure_view(
            strokeWidth=0  # Remove border around the chart
        )
        st.altair_chart(chart_ranked, use_container_width=True)
    else:
        st.write("No data available for top-ranked competitors.")

    # Top 10 Competitors with High Points Bar Chart
    st.subheader("Top 10 Competitors with High Points")
    if not top_points_df.empty:
        chart_points = alt.Chart(top_points_df).mark_bar().encode(
            x=alt.X("Points:Q", title="Points"),
            y=alt.Y("Competitor:N", sort="-x", title="Competitor"),
            color=alt.Color("Competitor:N", legend=None),
            tooltip=["Competitor", "Points"]
        )
        #.properties(width=600, height=400, title="Top 10 Competitors with High Points")
        st.altair_chart(chart_points, use_container_width=True)
    else:
        st.write("No data available for competitors with high points.")

# Filtered Competitors Tab
elif tab_selection == "Competitors details":
    st.header("Competitors details")
    
    # Sidebar for filters (same as the existing code for filtering competitors)
    with st.sidebar:
        st.header("Filters")
        
        # Fetch unique competitor names
        unique_names_query = "SELECT DISTINCT name FROM Competitors ORDER BY name"
        unique_names_df = fetch_data(unique_names_query)
        unique_names = unique_names_df['name'].tolist()
        
        # Competitor name filter
        selected_name = st.selectbox("Select Competitor Name", options=["All"] + unique_names)
        
        # Fetch unique countries
        unique_countries_query = "SELECT DISTINCT country FROM Competitors ORDER BY country"
        unique_countries_df = fetch_data(unique_countries_query)
        unique_countries = unique_countries_df['country'].tolist()
        
        # Country filter
        selected_country = st.selectbox("Select Country", options=["All"] + unique_countries)
        
        # Fetch minimum and maximum rank dynamically
        rank_range_query = "SELECT MIN(rank) AS min_rank, MAX(rank) AS max_rank FROM CompetitorRanking"
        rank_range_df = fetch_data(rank_range_query)
        min_rank, max_rank = rank_range_df.loc[0, 'min_rank'], rank_range_df.loc[0, 'max_rank']
        
        # Rank range slider
        st.write("Select Rank Range")
        rank_min, rank_max = st.slider("Rank Range", min_value=min_rank, max_value=max_rank, value=(min_rank, max_rank))

    # Build dynamic filters (same as the existing code)
    filters = []
    if selected_name != "All":
        filters.append(f"c.name = '{selected_name}'")
    if selected_country != "All":
        filters.append(f"c.country = '{selected_country}'")
    filters.append(f"cr.rank BETWEEN {rank_min} AND {rank_max}")

    # Combine filters into a WHERE clause
    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

    
    # Add this query for Country-Wise Analysis
# Construct the country_analysis_query with a dynamically replaced where_clause
    country_analysis_query = f"""
        SELECT 
            c.Country AS Country, 
            COUNT(DISTINCT c.competitor_id) AS TotalCompetitors,
            AVG(cr.Points) AS AvgPoints
        FROM Competitors c
        JOIN CompetitorRanking cr ON c.competitor_id = cr.competitor_id
        {where_clause}  -- Inject the dynamically built where_clause here
        GROUP BY c.Country
        ORDER BY TotalCompetitors DESC
    """

    # Fetch competitors data based on the filters
    competitors_query = f"""
        SELECT c.Name, cr.Rank, c.Country, cr.Points
        FROM Competitors c
        JOIN CompetitorRanking cr ON c.competitor_id = cr.competitor_id
        {where_clause}
        ORDER BY cr.rank ASC
    """
    competitors_df = fetch_data(competitors_query)
    country_analysis_df = fetch_data(country_analysis_query)
    # Display filtered competitors with scrolling
    #st.header("competitors details")
    if not competitors_df.empty:
        competitors_table_html = competitors_df.to_html(classes="competitors-table", index=False)
        st.markdown(f'<div class="competitors-table-wrapper">{competitors_table_html}</div>', unsafe_allow_html=True)
    else:
        st.write("No competitors found matching the criteria.")

    # Display the country-wise analysis table
    if not country_analysis_df.empty:
        st.subheader("Total Competitors and Average Points by Country")
        st.dataframe(country_analysis_df)

        # Create a bar chart for visualization
        st.subheader("Country-Wise Total Competitors")
        competitors_chart = alt.Chart(country_analysis_df).mark_bar().encode(
            x=alt.X("TotalCompetitors:Q", title="Total Competitors"),
            y=alt.Y("Country:N", sort="-x", title="Country"),
            color=alt.Color("Country:N", legend=None),
            tooltip=["Country", "TotalCompetitors", "AvgPoints"]
        ).properties(
            width=700,
            height=400,
            title="Total Competitors by Country"
        )
        st.altair_chart(competitors_chart, use_container_width=True)

        st.subheader("Country-Wise Average Points")
        avg_points_chart = alt.Chart(country_analysis_df).mark_bar().encode(
            x=alt.X("AvgPoints:Q", title="Average Points"),
            y=alt.Y("Country:N", sort="-x", title="Country"),
            color=alt.Color("Country:N", legend=None),
            tooltip=["Country", "TotalCompetitors", "AvgPoints"]
        ).properties(
            width=700,
            height=400,
            title="Average Points by Country"
        )
        st.altair_chart(avg_points_chart, use_container_width=True)
    else:
        st.write("No data available for country-wise analysis.")

