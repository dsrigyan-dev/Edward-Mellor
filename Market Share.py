#!/usr/bin/env python
# coding: utf-8

# # MARKET SEGMENT

# ## BASIC SETTING

# ### DEFAULT FOLDER SETTING

# In[9]:


import os

import pandas as pd

# Change the current working directory
os.chdir("C:/Users/srigd/Desktop/My Project/Dashboard/Calendar KPI/MARKET SEGMENT")

# # Now, when you open a file without specifying a full path, Python looks in the current working directory
# with open('another_file.txt', 'w') as f:
#     f.write('This file is saved in the specified default directory.')

# Row and column setting
pd.set_option("display.max_rows", 100)  # Show all rows
pd.set_option("display.max_columns", None)  # Show all columns


# ## FUNCTION

# ### SHOW DATAFRAME

# In[10]:


import dtale
import pandas as pd

# Create a DataFrame


# Function to display the DataFrame in a new tab using dtale
def show(df):
    d = dtale.show(df)
    d.open_browser()

# Call the function to display the DataFrame in a new tab


# ### FORMAT DATAFRAME

# In[11]:


import numpy as np
import pandas as pd
from IPython.display import display


def format_dataframe(
    df,
    precision=2,
    thousands_separator=True,
    date_format="%Y-%m-%d",
    max_rows=None,
    max_cols=None,
    column_width=None,
    style=True,
):
    """
    Format a pandas DataFrame with improved readability and styling.

    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame to format
    precision : int, default 2
        Number of decimal places for floating point numbers
    thousands_separator : bool, default True
        Whether to add thousand separators to numerical values
    date_format : str, default '%Y-%m-%d'
        Format for datetime columns
    max_rows : int, optional
        Maximum number of rows to display
    max_cols : int, optional
        Maximum number of columns to display
    column_width : int, optional
        Maximum width for columns
    style : bool, default True
        Whether to apply style formatting (background colors, etc.)

    Returns:
    --------
    pandas.DataFrame
        Formatted DataFrame
    """
    # Create a copy to avoid modifying the original
    formatted_df = df.copy()

    # Set display options
    pd.set_option("display.max_rows", max_rows if max_rows else 50)
    pd.set_option("display.max_columns", max_cols if max_cols else 20)
    pd.set_option("display.width", column_width if column_width else 1000)
    pd.set_option("display.precision", precision)

    # Format numeric columns
    numeric_columns = formatted_df.select_dtypes(include=[np.number]).columns
    for col in numeric_columns:
        if thousands_separator:
            formatted_df[col] = formatted_df[col].apply(
                lambda x: "{:,}".format(round(x, precision)) if pd.notnull(x) else x
            )

    # Format datetime columns
    date_columns = formatted_df.select_dtypes(include=["datetime64"]).columns
    for col in date_columns:
        formatted_df[col] = formatted_df[col].dt.strftime(date_format)

    if style:
        # Apply styling
        styled_df = (
            formatted_df.style.set_properties(
                **{
                    "background-color": "#f5f5f5",
                    "color": "black",
                    "border-color": "#888888",
                    "padding": "5px",
                }
            )
            .set_table_styles(
                [
                    {
                        "selector": "th",
                        "props": [
                            ("background-color", "#4CAF50"),
                            ("color", "white"),
                            ("font-weight", "bold"),
                            ("padding", "5px"),
                            ("border", "1px solid #888888"),
                        ],
                    },
                    {"selector": "td", "props": [("border", "1px solid #888888")]},
                    {
                        "selector": "",
                        "props": [
                            ("border-collapse", "collapse"),
                            ("border", "1px solid #888888"),
                        ],
                    },
                ]
            )
            .highlight_null(props={"background-color": "#ffcdd2"})
        )  # Updated syntax for highlighting null values

        return styled_df

    return formatted_df


# Example usage function
def display_formatted_df(df, **kwargs):
    """
    Wrapper function to quickly display a formatted DataFrame
    """
    formatted = format_dataframe(df, **kwargs)
    display(formatted)


# ### SUM OF COLUMNS

# In[12]:


import pandas as pd


# Define the function
def print_column_sums(df, *columns):
    for column in columns:
        if column in df.columns:
            column_sum = df[column].sum()
            print(f"Column '{column}' number = {column_sum}")
        else:
            print(f"Column '{column}' does not exist in the DataFrame")


# Example usage
# Assuming df is your DataFrame
# Call the function with the DataFrame and column names as arguments
# print_column_sums(df, 'column1', 'column2', 'column3')


# ### Access data from salesforce via SOQL

# In[13]:


import keyring
import pandas as pd
import requests
from simple_salesforce import Salesforce


def export_salesforce_data(query, export_file=None):
    # Retrieve your credentials
    username = keyring.get_password("salesforce", "username")
    password = keyring.get_password("salesforce", "password")
    security_token = keyring.get_password("salesforce", "security_token")
    consumer_key = keyring.get_password("salesforce", "consumer_key")
    consumer_secret = keyring.get_password("salesforce", "consumer_secret")

    # Step 1: Obtain OAuth 2.0 token
    token_url = "https://login.salesforce.com/services/oauth2/token"
    payload = {
        "grant_type": "password",
        "client_id": consumer_key,
        "client_secret": consumer_secret,
        "username": username,
        "password": password + security_token,
    }
    response = requests.post(token_url, data=payload)
    response.raise_for_status()  # Check if the request was successful

    # Extract access token from the response
    access_token = response.json().get("access_token")
    instance_url = response.json().get("instance_url")

    # Step 2: Authenticate to Salesforce using the access token
    sf = Salesforce(instance_url=instance_url, session_id=access_token)

    # Step 3: Query data
    records = []
    query_result = sf.query_all(query)
    records.extend(query_result["records"])

    # Continue querying if there are more records
    while not query_result["done"]:
        query_result = sf.query_more(query_result["nextRecordsUrl"], True)
        records.extend(query_result["records"])

    # Function to flatten nested dictionaries
    def flatten_record(record, parent_key="", sep="."):
        items = []
        for k, v in record.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_record(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    # Flatten all records
    flattened_records = [flatten_record(record) for record in records]

    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(flattened_records)

    # Clean up the DataFrame (remove Salesforce metadata)
    if "attributes.type" in df.columns:
        df = df.drop(columns=["attributes.type", "attributes.url"])

    # Optionally, export the DataFrame to a CSV file if export_file is provided
    if export_file:
        df.to_csv(export_file, index=False)
        print(f"Data exported to {export_file}")

    # Return the DataFrame
    return df


# example of calling the function


# # Example usage
# query = """
# SELECT
#     id,
#     User__c,
#     Name,
#     Primary__r.Name,
#     Staff_Activated__c,
#     Primary__r.POD__r.Name,
#     Role_Title__r.Name
# FROM
#     Staff__c
# """
# export_file = 'test.csv'

# # Get the DataFrame
# df = export_salesforce_data(query)

# # Display the DataFrame
# df


# ### Exporting the data to MYSQL80

# In[14]:


import urllib.parse

import pandas as pd
import win32cred
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import Date


def get_windows_credentials(target_name):
    """Retrieve credentials from Windows Credential Manager."""
    creds = win32cred.CredRead(target_name, win32cred.CRED_TYPE_GENERIC, 0)
    username = creds["UserName"]
    password = creds["CredentialBlob"].decode("utf-16")
    return username, password


def load_dataframe_to_mysql(df, table_name):
    """Load a DataFrame into a MySQL table with the same structure as the DataFrame."""
    # Retrieve credentials
    target_name = "SQLServerConnection"
    username, password = get_windows_credentials(target_name)

    # MySQL connection details
    host = "localhost"
    database = "edwardmellorsalesforce"

    # URL-encode the password
    encoded_password = urllib.parse.quote_plus(password)

    # Create a connection string
    connection_string = (
        f"mysql+mysqlconnector://{username}:{encoded_password}@{host}/{database}"
    )

    # Create SQLAlchemy engine with increased timeout and autocommit
    engine = create_engine(
        connection_string, connect_args={"connect_timeout": 600, "autocommit": True}
    )

    # Detect and convert date columns
    dtype = {}
    for column in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[column]):
            # Convert to DATE format in DataFrame

            
            # df[column] = pd.to_datetime(df[column]).dt.date

            df = df.copy()  # Make an explicit copy to avoid warnings
    for column in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[column]):
            df.loc[:, column] = pd.to_datetime(df[column]).dt.date
            dtype[column] = Date
            # Add to dtype dictionary as DATE type for MySQL
            dtype[column] = Date

    try:
        # Load DataFrame into MySQL with the specified dtypes
        df.to_sql(
            name=table_name.lower(),
            con=engine,
            if_exists="replace",
            index=False,
            dtype=dtype,
            chunksize=1000,
        )
        print(
            f"DataFrame successfully exported to MySQL database into table '{table_name}'"
        )

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Ensure the connection is properly closed
        engine.dispose()
        print("Database connection closed.")


# Example usage
# load_dataframe_to_mysql(df, 'your_table_name')


# ### OBJECT TO DATE FUNCTION

# In[15]:


import numpy as np
import pandas as pd


def convert_to_datetime_or_date(df, columns, format_type="datetime"):
    """
    Convert specified columns in a DataFrame to datetime or date format.

    Parameters:
    df (pd.DataFrame): The DataFrame containing the columns to be converted.
    columns (list): List of column names to be converted.
    format_type (str): The target format ('datetime' or 'date'). Default is 'datetime'.

    Returns:
    pd.DataFrame: The DataFrame with specified columns converted.
    """
    for column in columns:
        if column in df.columns:
            if format_type == "datetime":
                df[column] = pd.to_datetime(df[column])
                # Remove timezone if present to ensure consistency
                df[column] = df[column].dt.tz_localize(None)
            elif format_type == "date":
                df[column] = pd.to_datetime(df[column]).dt.normalize()
                # Remove timezone if present to ensure consistency
                df[column] = df[column].dt.tz_localize(None)
            else:
                raise ValueError("Invalid format_type. Use 'datetime' or 'date'.")
        else:
            print(f"Warning: '{column}' not found in DataFrame columns.")
    return df


# # example of calling the function
# df = convert_to_datetime_or_date(df, ['SalesforceDateTime', 'AnotherDateTime'], format_type='date')


# ## DATA MANIPULATION

# ### RAW DATA

# In[16]:


# COALESCE(        DATE_SUB(LEAD(CreatedDate) OVER (ORDER BY CreatedDate), INTERVAL 1 DAY),        CURDATE()    ) AS EndDate,
# Example usage
query = """
SELECT
 id,
 UPRN__c,
 Name,
 CreatedDate,
  Brand_Name__c,
 Longitude__c,
 Latitude__c,
 Property_Type__c,
 Status__c,
 Branch_Name__c,
 Postcode__c,
 Address_1__c,
 Address_2__c,
 Address_3__c,
 Inclusion_Reason__c,
 Company_Name__c,
 Auction_Flag__c,
 Website_URL__c,
 New_Build_Flag__c,
 Listing_Price__c,
 Bedrooms__c,
 Bathrooms__c,
 First_Listing_Date__c
FROM EMv2_MCDR__c
Where Trans_Type__c !='Rent'

"""

# Get the DataFrame
raw_data = export_salesforce_data(query)

convert_to_datetime_or_date(raw_data, ['CreatedDate'], format_type='date')

# Display the DataFrame
raw_data


# In[17]:


raw_data[raw_data['UPRN__c']=='10012207397'].head(10)


# ### FLAGGING THE TABLE

# In[18]:


raw_data.dtypes


# ### NEW LISTING FLAG

# In[19]:


import pandas as pd
import numpy as np

# Ensure df is not a view/slice of another DataFrame
df = raw_data.copy()

# Initialize all flags and UPRN columns
df["Flag_AllNewListing"] = 0
df["Flag_EMNewListing"] = 0
# df["Flag_AllNewListingUPRN"] = None
# df["Flag_EMNewListingUPRN"] = None

# Define valid property types
valid_property_types = [
    'Flat / Apartment',
    'House - Terraced',
    'Bungalow',
    'House - Detached',
    'House - Semi-Detached',
    'House - Unspecified'
]

# Create boolean masks for qualifying records
all_qualifying_mask = (
    (df["Inclusion_Reason__c"] == "Listing First Visible") &
    (df["New_Build_Flag__c"] == "F") &
    (df["Property_Type__c"].isin(valid_property_types))
)

em_qualifying_mask = all_qualifying_mask & (df["Brand_Name__c"] == "Edward Mellor Ltd")

# Set flags using masks
df["Flag_AllNewListing"] = all_qualifying_mask.astype(int)
df["Flag_EMNewListing"] = em_qualifying_mask.astype(int)

# Set UPRN values using masks (only where flags are 1)
# df["Flag_AllNewListingUPRN"] = np.where(all_qualifying_mask, df["UPRN__c"], None)
# df["Flag_EMNewListingUPRN"] = np.where(em_qualifying_mask, df["UPRN__c"], None)

# # Display relevant columns to verify the logic
# df[["Inclusion_Reason__c", "New_Build_Flag__c", "Property_Type__c", "Flag_AllNewListing", "Flag_AllNewListingUPRN"]]
raw_data_listing=df.copy()
raw_data_listing


# In[20]:


raw_data_listing[raw_data_listing['UPRN__c']=='10012207397'].head(10)


# ### SALES FLAG

# In[21]:


df=raw_data_listing.copy()

# 1. Initialize all flags and UPRN columns
df["Flag_AllSales"] = 0
df["Flag_EMSales"] = 0
# df["Flag_AllSalesUPRN"] = None  # Initialize as empty
# df["Flag_EMSalesUPRN"] = None   # Initialize as empty

# 2. Define common conditions
valid_statuses = ['SSTC', 'Under Offer']
base_condition = (
    (df["Inclusion_Reason__c"].str.contains('Status Change')) & 
    (df["Status__c"].isin(valid_statuses)) &
    (df["New_Build_Flag__c"] == 'F') &
    (df['Property_Type__c'].isin(valid_property_types))
)

# 3. Create masks
Allmask = base_condition
EMmask = base_condition & (df["Brand_Name__c"] == "Edward Mellor Ltd")

# 4. Process All Sales
df.loc[Allmask, "Flag_AllSales"] = 1

# Ensure UPRN is updated only where Flag_AllSales is set to 1
# df.loc[df["Flag_AllSales"] == 1, "Flag_AllSalesUPRN"] = df.loc[df["Flag_AllSales"] == 1, "UPRN__c"]

# 5. Process Edward Mellor Sales
df.loc[EMmask, "Flag_EMSales"] = 1

# Ensure UPRN is updated only where Flag_EMSales is set to 1
# df.loc[df["Flag_EMSales"] == 1, "Flag_EMSalesUPRN"] = df.loc[df["Flag_EMSales"] == 1, "UPRN__c"]

# Final dataframe ready for use
raw_post_flagging=df.copy()
raw_post_flagging


# In[22]:


raw_post_flagging[raw_post_flagging['UPRN__c']=='10012207397'].head(10)


# In[23]:


convert_to_datetime_or_date(raw_post_flagging, ['CreatedDate', 'First_Listing_Date__c'], format_type='date')


# In[24]:


raw_post_flagging.dtypes


# ### POST CODE

# In[25]:


# Example usage
query = """
select Name,Area_Type__c,Postcode_District__c,Office__c,Office__r.Name,Previous_Office__c,Previous_Office__r.Name from Market_Area__c 
"""

# Get the DataFrame
postcode= export_salesforce_data(query)

# Display the DataFrame
postcode


# In[26]:


postcode[postcode['Postcode_District__c']=='M1']


# In[27]:


postcode = postcode[
    [
        "Name",
        "Area_Type__c",
        "Postcode_District__c",
        "Office__c",
        "Office__r.Name",
        "Previous_Office__c",
        "Previous_Office__r.Name"
    ]
].copy()

# Rename the columns
postcode.rename(
    columns={
        "Name": "Market_Area",
        "Area_Type__c":"Area_Type",
        "Postcode_District__c":"Postcode_District",
        "Office__c": "PostCodeofficeId",
        "Office__r.Name": "PostCodeofficeName",
        "Previous_Office__c": "PostCodePreviousOfficeId",
        "Previous_Office__r.Name": "PostCodePreviousOfficeName"
    },
    inplace=True,
)
# Replace None or NaN values in PostCodePreviousOfficeId with values from PostCodeofficeId
postcode["PostCodePreviousOfficeId"] = postcode["PostCodePreviousOfficeId"].fillna(postcode["PostCodeofficeId"])
postcode["PostCodePreviousOfficeName"] = postcode["PostCodePreviousOfficeName"].fillna(postcode["PostCodeofficeName"])

postcode["PostCodePreviousOfficeId"] = postcode["PostCodePreviousOfficeId"].fillna("Auction")
postcode["PostCodePreviousOfficeName"] = postcode["PostCodePreviousOfficeName"].fillna("Auction")

postcode["PostCodeofficeId"] = postcode["PostCodeofficeId"].fillna("Auction")
postcode["PostCodeofficeName"] = postcode["PostCodeofficeName"].fillna("Auction")
# postcode["PostCodePreviousOfficeName"].fillna("PostCodeofficeName")

postcode


# In[28]:


postcode[postcode['Market_Area']=='SK16']
# Print(postcode[postcode['Market_Area']=='M1']


# In[29]:


def apply_excel_like_formulas(df, column1, column2, postcode_column):
    # Function to extract postal area including the first space plus one character
    def extract_market_area(postcode):
        if pd.isna(postcode):
            return None
        space_index = postcode.find(" ")
        if space_index == -1 or len(postcode) <= space_index + 1:
            return postcode  # Return the full postcode if no space or no additional characters
        return postcode[:space_index + 2]  # Include space and one additional character

    # Function to extract postal area up to but not including the first space
    def extract_district(postcode):
        if pd.isna(postcode):
            return None
        space_index = postcode.find(" ")
        if space_index == -1:
            return postcode  # Return the full postcode if no space
        return postcode[:space_index]  # Exclude the space

    # Apply functions to extract data
    df[column1] = df[postcode_column].apply(extract_market_area)
    df[column2] = df[postcode_column].apply(extract_district)

    # Merge operations
    merged_data_market_area = pd.merge(df, postcode, left_on=column1, right_on='Market_Area', how='left')
    merged_data_district = pd.merge(df, postcode, left_on=column2, right_on='Market_Area', how='left')

    # Combine results and handle missing values
    df = merged_data_market_area.fillna(merged_data_district)
    
    return df

# Applying the function to process postal codes
df=raw_post_flagging.copy()
df= apply_excel_like_formulas(df, 'MCDR_MarketArea', 'MCDR_District', 'Postcode__c')
MCDR=df.copy()
MCDR


# In[30]:


MCDR[MCDR['UPRN__c']=='10012207397'].head(10)


# In[31]:


MCDR.dtypes


# ### EXPORT THE DATA IN SQL

# In[32]:


if __name__ == "__main__":
    # Load DataFrame into MySQL
    load_dataframe_to_mysql(MCDR, "MCDR")


# In[ ]:




