## Imports

from supabase import create_client, Client
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta


## API
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


### Connecting the Data ### 

# Defining a function to retrieve data from Supabase
def fetch_items_data(table):
    response = supabase.table(table).select("*").execute()
    data = response.data
    df = pd.DataFrame(data)
    return df


# Establishing two variables for each table
items = fetch_items_data("items")
batches = fetch_items_data("batches")


### Web App ###

# Title for the Web App
st.title("Simple Pharma Analysis")

# Splitting the Web App into two tabs
tab1, tab2 = st.tabs(["Overview", "Product View"])


## Overview: This will show some charts with metrics for the whole data ##
with tab1:
    st.header("Overview")

    ## Item Expiry Dates Chart ##
    st.subheader("Item Expiry Dates")
    '''
    
    '''

    # Step 1: Joining
    # (Left) joining the DataFrames as I will use both tables for this.
    joined_df = pd.merge(batches, items, left_on='item_id', right_on='id', suffixes=('_batch', '_item'))

    # Step 2: Filtering
    # Convert expiry_date to datetime to allow for comparison
    joined_df['expiry_date'] = pd.to_datetime(joined_df['expiry_date'])
    
    # Calculate the date 6 months from now
    six_months_from_now = datetime.now() + timedelta(days=182)
    
    # Filter rows where expiry_date is within the next 6 months
    filtered_df = joined_df[joined_df['expiry_date'] <= six_months_from_now]

    # Step 3: Selecting Specific Columns
    # Only want to see product_id, label, batch_number and expiry_date for this chart
    selected_columns_df = filtered_df[['product_id', 'label', 'batch_number', 'expiry_date']]

    # Step 4: Ordering the Data
    # This will ensure the x-axis displays properly in date order
    final_df = selected_columns_df.sort_values(by='expiry_date')

    # Step 5: Plotting
    fig = px.scatter(final_df,
                    x='expiry_date',
                    y='label',
                    labels={'expiry_date': 'Expiry Date', 'label': 'Label'},
                    height=500,
                    color_discrete_sequence=['red']
                    )

    # Improving readability by adjusting the x-axis tick format and rotating them by -45 degrees
    fig.update_layout(xaxis_tickformat='%Y-%m-%d', xaxis_tickangle=-45)

    # Increasing size of the markers
    fig.update_traces(marker=dict(size=15))

    # Showing the plot in Web App 
    st.plotly_chart(fig, use_container_width=True)



    ## Time to Market ##

    st.subheader("Average Time to Market by Product")
    '''
    Ghryvelin and Testavan stand out with the fastest average times to market, signaling efficient processing, while Cefepime, Imipenem/Cilastatin, and Meropenem have the longest average times, potentially indicating a more involved process or different handling requirements.
    '''

    # Step 1: Converting date columns to datetime
    batches['date_receipt_warehouse'] = pd.to_datetime(batches['date_receipt_warehouse'])
    batches['date_in_market_release'] = pd.to_datetime(batches['date_in_market_release'])

    # Step 2: Calculating time to market for each row
    batches['time_to_market'] = (batches['date_in_market_release'] - batches['date_receipt_warehouse']).dt.days

    # Step 3: Grouping by product and calculating average
    average_time_to_market = batches.groupby('product')['time_to_market'].mean().reset_index()

    # Step 4: Ordering the Results
    average_time_to_market = average_time_to_market.sort_values(by='time_to_market', ascending=True)

    # Step 5: Renaming columns for clarity
    average_time_to_market.rename(columns={'time_to_market': 'average_time_to_market_days'}, inplace=True)

    # Step 6: Plotting
    fig2 = px.bar(average_time_to_market, 
                x='product', 
                y='average_time_to_market_days',
                labels={'average_time_to_market_days': 'Average Time to Market (days)', 'product': 'Product'},
                color='average_time_to_market_days')

    # Enhancing chart appearance
    fig2.update_layout(xaxis_title='Product',
                yaxis_title='Average Time to Market (days)',
                coloraxis_colorbar=dict(title='Days'))

    # Showing the plot in Web App 
    st.plotly_chart(fig2, use_container_width=True)

    

    ## Top 10 Products by Total Quantitiy ##

    st.subheader("Top 10 Products by Total Quantity")
    ''' 
    The chart ranks products based on the total quantity. The highest quantity is for the product labeled '000038_FG_CEFEPIME_1g_10x1g_FR,' with a quantity of 4239. The lowest among the top 10 is '000035_FG_Ghvrelvin_FR_NL_DK' with a quantity of 80.
    The top two products have significantly higher quantities compared to the others. There's a notable drop after the second product ('000040_FG_TESTAVAN_20mg/1.85x5g_CH'), which has a quantity of 4198, to the third product with a quantity of 2797.
    '''

    # Step 1: Making a copy of the joined_df from earlier
    joined_df_2 = joined_df.copy()

    # Step 2: Grouping and Aggregating the Data
    grouped_df_2 = joined_df_2.groupby(['product_id', 'label']).agg(total_quantity=pd.NamedAgg(column='quantity', aggfunc='sum'))

    # Step 3: Order the Results
    ordered_df = grouped_df_2.sort_values(by='total_quantity', ascending=True)

    # Step 4: Limiting the Results to 10
    top_10_df = ordered_df.head(10)

    # Reset index to make 'product_id' and 'label' regular columns
    top_10_df_reset = top_10_df.reset_index()

    # Step 5: Plotting
    fig3 = px.bar(top_10_df_reset,
                y='label', 
                x='total_quantity',
                text='total_quantity', 
                title='Top 10 Products by Total Quantity', 
                labels={'label': 'Product Label', 'total_quantity': 'Total Quantity'}, 
                color='total_quantity',  
                color_continuous_scale=px.colors.sequential.Viridis,  
                orientation='h')
    
    # Improving layout for better readability
    fig3.update_layout(xaxis_title='Product Label',
                    yaxis_title='Total Quantity',
                    xaxis_tickangle=-45)

    st.plotly_chart(fig3, use_container_width=True)

with tab2:

    st.header("Product View")

    ## Product Slicer
    product_list = batches['product'].unique().tolist()

    product_filter = st.selectbox(
    'Select a product:',
    (product_list))

    
    ## Expiry dates for each label

    # (Left) joining the DataFrames as I will use both tables for this.
    joined_df_3 = joined_df.copy()

    # Filtering joined DataFrame based on the selected product
    filtered_df_3 = joined_df_3[joined_df_3['product'] == product_filter]

    # Converterting expiry_date to datetime to allow for comparison
    filtered_df_3['expiry_date'] = pd.to_datetime(filtered_df_3['expiry_date'])

    # plotting
    fig4 = px.scatter(filtered_df_3, 
                    x='expiry_date', 
                    y='label', 
                    title=f"Expiry Dates for {product_filter}",
                    labels={"expiry_date": "Expiry Date", "label": "Label"},
                    hover_data=['batch_number', 'quantity'])

    # Improving readability by adjusting the x-axis tick format and rotating them by -45 degrees
    fig4.update_layout(xaxis_tickformat='%Y-%m-%d', xaxis_tickangle=-45)

    # Increasing size of the markers
    fig4.update_traces(marker=dict(size=15))

    # Showing the plot in Web App 
    st.plotly_chart(fig4, use_container_width=True)


    ## Top labels per product by quantity

    st.subheader("Top Labels by Quantity")

    # Making a copy of the joined_df from earlier
    joined_df_4 = joined_df.copy()

    # Filtering joined DataFrame based on the selected product
    filtered_df_4 = joined_df_4[joined_df_4['product'] == product_filter]

    # Aggregating data to get total quantity per label
    label_quantity_df_4 = filtered_df_4.groupby('label').agg({'quantity': 'sum'}).reset_index()

    # Ordering data for the plot
    ordered_df_4 = label_quantity_df_4.sort_values(by='quantity', ascending=True)

    # Plotting
    fig5 = px.bar(ordered_df_4, 
                x='quantity', 
                y='label', 
                title=f"{product_filter}",
                labels={"quantity": "Total Quantity", "label": "Label"},
                text='quantity',
                height=700,
                orientation='h')

    fig5.update_layout(xaxis_tickangle=-45)  

    st.plotly_chart(fig5, use_container_width=True)
