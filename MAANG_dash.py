#MAANG Share Dashboard Code
import pandas as pd 
import streamlit as st 
import plotly.express as px

#set page size
st.set_page_config(layout="wide")

#----------Import Data----------#
#import data
df = pd.read_csv('MAANG_DATA.csv')

#replace Nan, NULL, NA values with a blank
df = df.fillna('')

#drop the 'Adj Close' column
df = df.drop(columns=['Adj Close'])

#ensure 'Volume' is numeric and round to the nearest whole number
df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')  # Convert to numeric, coercing errors
df['Volume'] = df['Volume'].round(0).astype(int)  # Round and convert to integer

#rounding to make numbers readable
df = df.round(2)
#adding appropriate commas for readability
def format_with_commas(x, column_name):
    if isinstance(x, (int, float)):
        if column_name in ['Open', 'High', 'Low', 'Close']:
            return f"${x:,.2f}"  # Format with dollar sign and 2 decimal places
        elif column_name == 'Volume':
            return f"{x:,}"  # Format with commas, no decimal for Volume
        else:
            return f"{x:,.1f}"  # Format with 1 decimal for other numeric columns
    return x

#apply formatting to all numeric columns
for column in df.columns:
    df[column] = df[column].apply(lambda x: format_with_commas(x, column))

#create a title
st.title('Share Price Action Dashboard')
st.markdown("<hr style='border: 1px solid red;'>", unsafe_allow_html=True)

#display the filtered dataframe
st.dataframe(df, use_container_width=True)

st.header("") 

#-----Metrics-----#
#create subheader and columns
st.subheader("Average Share Price by Company")
st.markdown("<style>hr {margin: 0;}</style><hr style='border: 1px solid red;'>", unsafe_allow_html=True)

#get unique company names from the DataFrame
unique_companies = df['Company Name'].unique()

#initialize a dictionary to hold average prices
average_prices = {}

#define company logos
company_logos = {
    "Meta Platforms Inc.": "https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg",
    "Amazon Inc.": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg",
    "Apple Inc.": "https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg",
    "Netflix Inc.": "https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg",
    "Alphabet Inc.": "https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg",
}

#calculate and display average prices for each company
for company in unique_companies:
    #filter the DataFrame for the current company
    company_data = df[df['Company Name'] == company]
    
    #calculate the average price across the relevant columns
    if not company_data.empty:
        average_price = company_data[['Open', 'High', 'Low', 'Close']].replace({'\$': '', ',': ''}, regex=True).astype(float).mean().mean()
        average_prices[company] = average_price  # Store the average price

        #display the average price with a border and logo
        st.markdown(
            f"<div style='border: 2px solid grey; padding: 10px; margin: 10px; border-radius: 5px; display: flex; align-items: center;'>"
            f"<img src='{company_logos[company]}' width='50' height='50' style='margin-right: 20px;'/>"
            f"<strong>{company}</strong> <span style='font-size: 1.5em; margin-left: 20px;'>${average_price:,.2f}</span>"
            f"</div>",
            unsafe_allow_html=True
        )
    else:
        st.metric(label=company, value="No data available")
#create space
st.header("")  # for spacing

# ----- Graphs ----- #
#create subheader and tabs
st.subheader("Graphs")
st.markdown("<style>hr {margin: 0;}</style><hr style='border: 1px solid red;'>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Average Share Price by Company", "Price Action", "Volume High/Low"])

#filling tabs
with tab1:
    if average_prices:  # Check if there are average prices calculated
        average_prices_df = pd.DataFrame(list(average_prices.items()), columns=['Company', 'Average Price'])

        # Plotting the average prices
        fig = px.bar(average_prices_df, x='Company', y='Average Price',
                     labels={'Average Price': 'Average Price ($)', 'Company': 'Company'},
                     color='Average Price',
                     color_continuous_scale=px.colors.sequential.Viridis)

        #display the plot
        st.plotly_chart(fig)
    else:
        st.write("No average prices to display.")

with tab2:
    #Create a dropdown to select a company
    selected_company = st.selectbox("Select a Company", options=unique_companies)

    #filter the DataFrame for the selected company
    company_data = df[df['Company Name'] == selected_company]

    #melt the DataFrame for easier plotting
    price_columns = ['Open', 'High', 'Low', 'Close']
    company_data_melted = company_data.melt(id_vars=['Date'], value_vars=price_columns,
                                             var_name='Price Type', value_name='Price')

    #plotting the price action with shades of the same color
    fig_line = px.line(company_data_melted, x='Date', y='Price', color='Price Type',
                        line_group='Price Type', hover_name='Price Type',
                        title='Click specific Price Types in legend to remove from graph',
                        labels={'Price': 'Price ($)', 'Price Type': 'Price Type'},
                        markers=True)

    #display the plot
    st.plotly_chart(fig_line)

with tab3:
    #create a line chart for volume over time for each company
    volume_data = df.groupby(['Date', 'Company Name'])['Volume'].sum().reset_index()

    #check if the volume_data DataFrame is empty
    if not volume_data.empty:
        fig_volume_time = px.line(volume_data, 
                                   x='Date', 
                                   y='Volume', 
                                   color='Company Name',
                                   title='Click company in legend to remove it from graph',
                                   labels={'Volume': 'Volume', 'Company Name': 'Company'},
                                   markers=True)  # Adding markers for clarity

        #display the plot
        st.plotly_chart(fig_volume_time)
    else:
        st.write("No data available for volume over time.")