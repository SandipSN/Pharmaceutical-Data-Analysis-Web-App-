# Pharmaceutical Data Analysis

Simple data processesing and analyis of some sample pharmaceutical data. This data is dummy data and was obtained as an interview task. The data was imported to Supabase so I could use it's API to pull from for my web app.


File info:

- xl_to_csv.py
This python script converted the Excel file (items.xlsx) I recieved into CSV files. 

The output will be two CSV files:

    - items.csv
    - batches.csv

- simple_pharm_app.py
This python script pulls the uploaded data from Supabase via thier api.
Using Streamlit, I coded a simple Web App to represent some of the analyses. 
The Overview Tab shows the general overview of the data, whereas the Product Level tab allows you to select a specific product and see some charts associated with it.

The Web App can be accessed through this link:

[https://simplepharma-task.streamlit.app/](https://pharma-analysis.streamlit.app/)

The python file is not neccessarily run directly to view the above. Instead, it was uploaded to GitHub, where the Stramlit cloud service could pick it up and establish an accessible Web App online.
