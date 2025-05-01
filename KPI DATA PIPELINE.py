#!/usr/bin/env python
# coding: utf-8

# # All KPI 23/10/2024

# ## This project is taking data from salesforce and transferring the data in my SQL so that can be used for creating performance & Reward Dashboard

# ## Basic Setting

# ### Dafault Folders

# In[2]:


import os

import pandas as pd

# Change the current working directory
os.chdir("C:/Users/srigd/Desktop/My Project/Dashboard/Calendar KPI")

# # Now, when you open a file without specifying a full path, Python looks in the current working directory
# with open('another_file.txt', 'w') as f:
#     f.write('This file is saved in the specified default directory.')

# Row and column setting
pd.set_option("display.max_rows", 100)  # Show all rows
pd.set_option("display.max_columns", None)  # Show all columns


# ## Function 

# #### Show Dataframe

# In[3]:


import dtale
import pandas as pd

# Create a DataFrame


# Function to display the DataFrame in a new tab using dtale
def show(df):
    d = dtale.show(df)
    d.open_browser()

# Call the function to display the DataFrame in a new tab


# ### Format Dataframe

# In[4]:


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


# In[ ]:





# ### Sum of columns

# In[5]:


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


# ### Object to date function

# In[6]:


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


# ### Access data from salesforce via SOQL

# In[7]:


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


# ### Duplicacy Check

# In[8]:


import pandas as pd


def check_duplicates(df, columns):
    """
    This function checks for duplicate records based on one or more columns in a Pandas DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame to check for duplicates.
    columns (str or list): The column name (or a list of column names) to check for duplicates.

    Returns:
    bool: Returns True if duplicates are found, otherwise False.
    Displays the duplicated rows if any are found.
    """
    # Check if a single column or a list of columns is passed
    if isinstance(columns, str):
        columns = [columns]

    # Check for duplicates based on the specified column(s)
    duplicates = df[df.duplicated(subset=columns, keep=False)]

    if not duplicates.empty:
        print("Duplicates found:")
        print(duplicates)
        return True
    else:
        print("No duplicates found.")
        return False


# Example usage:
# Creating a sample DataFrame
data = {"A": [1, 2, 2, 4], "B": [5, 6, 6, 8], "C": ["X", "Y", "Y", "Z"]}

df = pd.DataFrame(data)

# Check for duplicates in a single column
check_duplicates(df, "A")

# Check for duplicates in multiple columns
check_duplicates(df, ["A", "B"])


# ### Exporting the data to MYSQL80

# In[9]:


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


# ## Source File

# ### PostCode

# In[17]:


# Example usage
query = """
select Name,Postcode_District__c,Office__c,Office__r.Name,Previous_Office__c,Previous_Office__r.Name from Market_Area__c 
"""

# Get the DataFrame
df = export_salesforce_data(query)

# Display the DataFrame
df


# In[18]:


postcode = df[
    [
        "Name",
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


# ### Staff

# In[19]:


# Example usage
query = """
select id,Market_Area__c,Market_Area__r.Postcode_Sector__c, 
Postcode__c,Market_Area__r.Office__c,Market_Area__r.Office__r.Name,Market_Area__r.Previous_Office__c,Market_Area__r.Previous_Office__r.Name from pba__Property__c 
"""

# Get the DataFrame
df = export_salesforce_data(query)

# Display the DataFrame
df


# In[20]:


# df.to_excel('postcode_mapping.xlsx')


# In[21]:


# Example usage
query = """
SELECT 
    id,
    User__c,
    Name,
    Primary__c,
    Primary__r.Name,
    Staff_Activated__c,
    Primary__r.POD__c,
    Primary__r.POD__r.Name,
    Role_Title__c,
    Role_Title__r.Name
FROM
    Staff__c
WHERE
    User__c != NULL
"""

# Get the DataFrame
df = export_salesforce_data(query)

# Display the DataFrame
df


# In[22]:


df.dtypes


# In[23]:


Staff = df[
    [
        "Id",
        "User__c",
        "Name",
        "Primary__c",
        "Primary__r.Name",
        "Staff_Activated__c",
        "Primary__r.POD__c",
        "Primary__r.POD__r.Name",
        "Role_Title__c",
        "Role_Title__r.Name",
    ]
].copy()

# Rename the columns
Staff.rename(
    columns={
        "User__c": "Staff_UserId",
        "Id": "Staff_StaffId",
        "Name": "Staff_UserName",
        "Staff_Activated__c": "Staff_ActiveStatus",
        "Primary__c": "Staff_OfficeId",
        "Primary__r.Name": "Staff_Office",
        "Primary__r.POD__c": "PODId",
        "Primary__r.POD__r.Name": "Staff_PODName",
        "Role_Title__c": "Staff_RoleTitleId",
        "Role_Title__r.Name": "Staff_Title",
    },
    inplace=True,
)

# user[user['Staff_UserID']=='0058W00000EKrpxQAD']

Staff["Staff_Status"] = np.where(
    Staff["Staff_ActiveStatus"] == 1, "Active", "Not Active"
)
Staff


# In[24]:


Staff_Limited = Staff[["Staff_UserId", "Staff_UserName", "Staff_Title"]]
Staff_Limited


# In[25]:


Staff


# In[26]:


Staff[['Staff_UserName']]


# In[27]:


import os
import pandas as pd
from fuzzywuzzy import process

# Define the root directory where employee images are stored
root_folder = "//MELLORVFILE/Users/Marketing/Employee Photos"

# Load your DataFrame (assuming it's already loaded)
# Staff = pd.read_csv("staff_data.csv")  # If loading from a CSV
# Staff = pd.read_excel("staff_data.xlsx")  # If loading from Excel

# Get the list of employee names from the DataFrame
employee_names = Staff["Staff_UserName"].astype(str).tolist()

# Step 1: Recursively get all image file paths
image_files = []
for root, _, files in os.walk(root_folder):
    for file in files:
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):  # Add more formats if needed
            image_files.append(os.path.join(root, file))

# Step 2: Match each employee name with the best image file
matched_image_paths = []
for emp in employee_names:
    file_names = [os.path.basename(img) for img in image_files]  # Extract just file names
    best_match, score = process.extractOne(emp, file_names)  # Find best match
    if score > 70:  # Adjust threshold as needed
        matched_file = next(img for img in image_files if best_match in img)
        matched_image_paths.append(matched_file)
    else:
        matched_image_paths.append("No match found")

# Step 3: Add the matched image path to the DataFrame
Staff["Image_Path"] = matched_image_paths
Staff["Score"] = score

# # Step 1: Define old and new path patterns
# old_prefix = r"//MELLORVFILE/Users/Marketing/Employee Photos\\"  # Local path
# onedrive_base_link = "https://1drv.ms/f/s!AuU5ko4KvAOYbc772VmcveJb0qA?e=Dn6aV7"

# #  Step 2: Load Employee Data
# # Staff = pd.read_csv("staff_data.csv")  # Uncomment if loading from a CSV
# # Staff = pd.read_excel("staff_data.xlsx")  # Uncomment if loading from Excel

# #  Step 3: Convert Local Paths to OneDrive Links
# Staff["onedrive_imagepath"] = Staff["Image_Path"].str.replace(old_prefix, onedrive_base_link, regex=False).str.replace("\\", "/", regex=False)




# Step 4: Save the updated DataFrame (optional)
Staff.to_excel('link.xlsx')

print("Image links added successfully!")
Staff



# In[28]:


import os
import shutil
import pandas as pd

# Load Employee Data (Ensure Staff DataFrame is already loaded)
# Example: Load from a CSV or Excel file if needed
# Staff = pd.read_csv("staff_data.csv")  # Uncomment if loading from a CSV
# Staff = pd.read_excel("staff_data.xlsx")  # Uncomment if loading from Excel

# Define destination folder for copying images
destination_folder = r"C:\Users\srigd\Documents\My Tableau Repository\Shapes\Employee"

# Ensure destination folder exists
os.makedirs(destination_folder, exist_ok=True)

# Copy images based on Image_Path
for index, row in Staff.iterrows():
    source_path = row["Image_Path"]
    
    if os.path.exists(source_path):  # Check if the source file exists
        # Get file name from source path
        file_name = os.path.basename(source_path)
        
        # Define new file path
        new_file_path = os.path.join(destination_folder, file_name)
        
        # Copy file
        shutil.copy2(source_path, new_file_path)
        # print(f"✅ Copied: {source_path} → {new_file_path}")
    # else:
    #     print(f"⚠️ File not found: {source_path}")

print("✅ All staff images copied successfully!")


# In[29]:


# import pandas as pd

# # Ensure Staff DataFrame is defined
# # Example: Load Staff DataFrame if needed
# # Staff = pd.read_csv("staff_data.csv")

# # Function to convert OneDrive shared links to direct image links
# def convert_onedrive_to_direct(link):
#     if "onedrive.live.com" in link:
#         if "embed" in link:
#             # Convert OneDrive embed link to direct download link
#             return link.replace("embed?", "download?").split("&authkey=")[0]
#         elif "resid=" in link:
#             # Convert OneDrive share link to API direct link
#             base_id = link.split("resid=")[-1].split("&")[0]
#             return f"https://api.onedrive.com/v1.0/shares/u!{base_id}/root/content"
#     return link  # If link format is unknown, return as-is

# # Apply the conversion function to each row in the DataFrame
# Staff["Direct_Image_URL"] = Staff["onedrive_imagepath"].apply(convert_onedrive_to_direct)

# Staff


# In[30]:


Staff


# In[ ]:





# In[ ]:





# In[31]:


Staff.to_excel('link.xlsx')


# In[32]:


if __name__ == "__main__":
    # Load DataFrame into MySQL
    load_dataframe_to_mysql(Staff, "Staff")


# ### Calendar

# In[33]:


import re

query = """
SELECT
        Name,
        Date__c              ,
        Fiscal_Week__c       ,
        Days_of_Week__c      ,
        Fiscal_Period__c     ,
        Week_in_Period__c    ,
        Fiscal_Quarter__c    ,
        Fiscal_Reward_Week__c,
        Fiscal_Year__c,
         Period_Week_Token__c,
        Month__c,
        Month_Text__c    
        
FROM
        Edward_Mellor_Calendar__c
"""
# export_file = 'test.csv'

# Get the DataFrame
df = export_salesforce_data(query)
df["Year-Q-P-W"] = df["Name"].apply(
    lambda x: re.search(r"\[.*?\]", x).group(0) if re.search(r"\[.*?\]", x) else None
)
# df
Calendar = df[
    [
        "Year-Q-P-W",
        "Date__c",
        "Fiscal_Week__c",
        "Days_of_Week__c",
        "Fiscal_Period__c",
        "Week_in_Period__c",
        "Fiscal_Quarter__c",
        "Fiscal_Reward_Week__c",
        "Fiscal_Year__c",
        "Period_Week_Token__c",
        "Month__c",
        "Month_Text__c",
    ]
]
Calendar["Year-Q-P"] = (
    Calendar["Fiscal_Year__c"]
    + "-"
    + Calendar["Fiscal_Quarter__c"]
    + "-"
    + Calendar["Fiscal_Period__c"]
)
# Rename the columns
Calendar.rename(
    columns={
        "Date__c": "Calendar_Date",
        "Fiscal_Week__c": "Calendar_FiscalWeek",
        "Days_of_Week__c": "Calendar_DaysOfWeek",
        "Fiscal_Period__c": "Calendar_FiscalPeriod",
        "Week_in_Period__c": "Calendar_WeekInPeriod",
        "Fiscal_Quarter__c": "Calendar_FiscalQuarter",
        "Fiscal_Reward_Week__c": "Calendar_FiscalRewardWeek",
        "Fiscal_Year__c": "Calendar_FiscalYear",
        "Period_Week_Token__c": "Week_NumberInPeriod",
        "Month__c": "Calendar_Month",
        "Month_Text__c": "Calendar_Month_txt",
    },
    inplace=True,
)


# Calendar = convert_to_datetime_or_date(Calendar, ['Calendar_Date'], format_type='date')

Calendar = convert_to_datetime_or_date(
    Calendar, ["Calendar_Date"], format_type="datetime"
).copy()
Calendar


# In[34]:


Calendar.dtypes


# In[35]:


if __name__ == "__main__":
    # Load DataFrame into MySQL
    load_dataframe_to_mysql(Calendar, "Calendar")


# ### Office

# In[36]:


# import re
query = """
select POD__c,POD__r.Name,id,Name,Not_User_Selectable__c from pba__Office__c 
"""
# export_file = 'test.csv'
# df
# Get the DataFrame
df = export_salesforce_data(query)
# df
# Rename the columns
df.rename(
    columns={
        "POD__c": "Office_POD",
        "POD__r.Name": "Office_PODName",
        "Id": "Office_OfficeId",
        "Name": "Office_OfficeName",
        "Not_User_Selectable__c":"Office_UserSelectable"
    },
    inplace=True,
)

Office = df[
    ["Office_POD", "Office_PODName", "Office_OfficeId", "Office_OfficeName","Office_UserSelectable"]
].copy()
Office


# In[37]:


if __name__ == "__main__":
    # Load DataFrame into MySQL
    load_dataframe_to_mysql(Office, "Office")


# ## Manipulated File

# ### Office_Calendar

# In[279]:


# This will be useful while caculating Office Performance


# In[280]:


Office["key"] = 1
Calendar["key"] = 1
Office_Calendar = pd.merge(Office, Calendar, on="key").drop("key", axis=1)
Office_Calendar


# In[281]:


if __name__ == "__main__":
    # Load DataFrame into MySQL
    load_dataframe_to_mysql(Office_Calendar, "Office_Calendar")


# ### Staff_Calendar

# In[282]:


# This will be useful to calculate employee performance


# In[283]:


Staff["key"] = 1
Calendar["key"] = 1
Staff_Calendar = pd.merge(Staff, Calendar, on="key").drop("key", axis=1)
Staff_Calendar


# In[284]:


if __name__ == "__main__":
    # Load DataFrame into MySQL
    load_dataframe_to_mysql(Staff_Calendar, "Staff_Calendar")


# ### VPM by Office

# In[285]:


# Example usage
query = """
SELECT 
    User__c,
    Name,
    Primary_Office_ID__c,
    Primary__c ,
    Office_Name__c,
    Job_Title_Name__c,
    Role_Title__c,
    Staff_Activated__c
FROM
    Staff__c
WHERE
    Job_Title_Name__c IN ('Vendor Performance Manager' , 'Assistant Vendor Performance Manager')
ORDER BY Office_Name__c

"""

df = export_salesforce_data(query)

# Display the DataFrame
df


# In[286]:


# Identifying offices that have both "Vendor Performance Manager" and "Assistant Vendor Performance Manager"
office_counts = df.groupby(["Office_Name__c", "Job_Title_Name__c"]).size().unstack(fill_value=0)
offices_to_remove = office_counts[(office_counts.get("Vendor Performance Manager", 0) > 0) & 
                                  (office_counts.get("Assistant Vendor Performance Manager", 0) > 0)].index

# Filtering the dataframe to remove "Assistant Vendor Performance Manager" records for those offices
df_filtered = df[~((df["Office_Name__c"].isin(offices_to_remove)) & 
                   (df["Job_Title_Name__c"] == "Assistant Vendor Performance Manager"))]
df_filtered=df_filtered[df_filtered["Staff_Activated__c"] == 1]
# Displaying the cleaned dataframe
df_filtered=df_filtered.reset_index(drop=True)
df_filtered


# In[287]:


vpm = df_filtered[["Primary__c", "Office_Name__c", "User__c", "Name"]].copy()
vpm.rename(
    columns={
        "Primary__c": "VPM_OfficeId",
        "Office_Name__c": "VPM_Office",
        "User__c": "VPM_UserId",
        "Name": "VPM_Name",
    },
    inplace=True,
)
vpm


# In[288]:


Office.dtypes


# In[289]:


vpm


# In[290]:


office_renamed=Office[['Office_OfficeId','Office_OfficeName']].rename(columns={'Office_OfficeId': 'VPM_OfficeId', 'Office_OfficeName': 'VPM_Office'})
result = pd.concat([vpm, office_renamed]).drop_duplicates('VPM_Office').reset_index(drop=True)
result['VPM_UserId'] = result['VPM_UserId'].fillna('Unidentified')
result['VPM_Name'] = result['VPM_Name'].fillna('Unidentified')
result


# In[291]:


vpm=result.copy()
vpm


# In[292]:


vpm.dtypes


# In[293]:


vpm.to_excel("vpm.xlsx")


# In[294]:


if __name__ == "__main__":
    # Load DataFrame into MySQL
    load_dataframe_to_mysql(vpm, "vpm")


# ## KPI Calculation

# ### Viewing & Mortgage Appointment

# #### Raw Event Table

# In[10]:


# Example usage
query = """
SELECT ID
	,RecordTypeId
	,RecordType.Name
	,Subject
    ,Related_SF_Record_ID__c
	,CreatedById
	,CreatedBy.Name
	,Created_By_Staff__c
	,CreatedDate
	,StartDateTime
	,EndDateTime
	,Type
	,Created_By_Staff__r.Name
	,Listing__c
	,Listing__r.Name
	,Listing__r.Postcode__c
	,Listing__r.Lister__c
	,DurationInMinutes
        ,Office__c
    ,CALC_Office_ID__c
    ,Contact_Name_Text__c
FROM Event
 where CreatedDate > 2023-06-30T00:00:00Z 
"""

# Get the DataFrame
df = export_salesforce_data(query)

# Display the DataFrame
df


# In[11]:


# Rename the columns
event = df[
    [
        "Id",
        "RecordTypeId",
        "RecordType.Name",
        "Subject",
        "Related_SF_Record_ID__c",
        "CreatedById",
        "CreatedBy.Name",
        "Created_By_Staff__c",
        "CreatedDate",
        "Type",
        "Listing__c",
        "DurationInMinutes",
        "Listing__r.Name",
        "Listing__r.Postcode__c",
        "CALC_Office_ID__c",
        "Office__c",
        "Contact_Name_Text__c",
    ]
].copy()
event.rename(
    columns={
        "Id": "Event_Id",
        "Subject": "Event_Subject",
        "CreatedById": "Event_CreatedById",
        "RecordTypeId": "Event_RecordId",
        "RecordType.Name": "Event_RecordName",
        "Related_SF_Record_ID__c":"Opportunity_ID",
        "CreatedDate": "Event_CreatedDate",
        "CreatedBy.Name": "Event_CreatedByName",
        "Created_By_Staff__c": "Event_Created_By_Staff",
        "Type": "Event_EventType",
        "Listing__c": "Event_ListingId",
        "Listing__r.Name": "Event_ListingName",
        "Listing__r.Postcode__c": "Event_ListingPostCode",
        "CALC_Office_ID__c":"Event_OfficeId",
        "Office__c": "Event_Office",
        "DurationInMinutes": "Event_DurationInMinutes",
        "Contact_Name_Text__c": "Event_ContactName",
    },
    inplace=True,
)

event = convert_to_datetime_or_date(
    event, ["Event_CreatedDate"], format_type="date"
).copy()

event


# In[12]:


event.dtypes


# In[13]:


# Flag for 'Viewing' event type
event["Flag_Viewing"] = event.apply(
    lambda row: (
        1
        if row["Event_EventType"] == "Viewing" and (row["Event_Office"] != "Auction")
        else 0
    ),
    axis=1,
)

# Flag for 'Viewing Cancelled' event type
# event["Flag_ViewingCancellation"] = event.apply(lambda row: 1 if row["Event_EventType"] == "Viewing"  and (row["Event_Office"]!='Auction')  and ("CANCELLED" not in str(row['Event_Subject']) else 0, axis=1)
event["Flag_ViewingCancellation"] = event.apply(
    lambda row: (
        1
        if (
            row["Event_EventType"] == "Viewing"
            and row["Event_Office"] != "Auction"
            and "CANCELLED" not in str(row["Event_Subject"])
        )
        else 0
    ),
    axis=1,
)

# # Flag for 'Mortgage Appointment' event, but exclude ones with 'CANCELLED'
event["Flag_MortgageBooked"] = event.apply(
    lambda row: (
        1
        if ("Mortgage Appointment" in str(row["Event_Subject"]))
        and ("CANCELLED" not in str(row["Event_Subject"]))
        else 0
    ),
    axis=1,
)
# # Flag for 'Mortgage Appointment' event, including cancellation and review
event["Flag_MortgageBookedAll"] = event.apply(
    lambda row: 1
    if (
        "Mortgage Appointment" in str(row["Event_Subject"]) and
        not any(x in str(row["Event_Subject"]) for x in [
            "Client cancelled meeting",
            "Client didn't answer",
            "Mortgage Review Appointment"
        ])
    )
    else 0,
    axis=1
)


# # Flag for 'Mortgage Appointment' event, but exclude ones with 'CANCELLED'
event["Flag_CancelledMortgageBooking"] = event.apply(
    lambda row: (
        1
        if ("Mortgage Appointment" in str(row["Event_Subject"]))
        and ("CANCELLED" in str(row["Event_Subject"]))
        else 0
    ),
    axis=1,
)

event


# In[14]:


event.to_excel("event.xlsx")


# In[15]:


print_column_sums(
    event, "Flag_Viewing", "Flag_MortgageBooked", "Flag_CancelledMortgageBooking"
)


# In[38]:


event = pd.merge(
    event,
    Staff_Limited,
    left_on="Event_CreatedById",
    right_on="Staff_UserId",
    how="left",
)
event = event.drop(columns=["Staff_UserId", "Staff_UserName"])
event.rename(columns={"Staff_Title": "Event_CreatedByTitle"}, inplace=True)
event


# In[39]:


import itables.options as opt
from itables import init_notebook_mode

init_notebook_mode(all_interactive=True)
# To display
from itables import show

show(event)


# In[40]:


from ydata_profiling import ProfileReport

# Create and display profile report
profile = ProfileReport(event, title="Profiling Report")
profile.to_notebook_iframe()


# In[41]:


if __name__ == "__main__":
    # Load DataFrame into MySQL
    load_dataframe_to_mysql(event, "event")


# In[ ]:


event


# ### Listing

# #### Rawl Listing

# In[306]:


# Example usage
query = """
SELECT 
    Id,
    OwnerId,
    RecordTypeId,
    RecordType.Name,
    Name,
    Postcode__c,
    Office__c,
    Office__r.Name,
    EA_Referral_Office__c,
    pba__ListingPrice_pb__c,
    pba__Status__c,
    Lister_Name__c,
    pba__ListedDate_pb__c,
    Valuation_Date__c,
    Withdrawn_Date__c,
    Calculated_Fee__c,
    Valuation_Cancelled__c,
    EA_Lister__c,
    EA_Lister__r.Name,
    EA_Lister_Profile__c,
    Estate_Agency_Referral__c,
    Estate_Agency_Referral__r.Name,
    Property_Auto_Reference__c,
    Vendor_Contact_Number__c,
    Rewards_VPM_Id_c__c,
    Rewards_VPM__c

    
FROM
    pba__Listing__c
WHERE 
    (
        (pba__ListedDate_pb__c > 2023-06-30 OR 
         Withdrawn_Date__c > 2023-06-30 OR 
         Valuation_Date__c > 2023-06-30 OR 
         Valuation_Cancelled__c > 2023-06-30)
    ) 
    AND 
    (
        (RecordType.Name = 'Auction' AND 
         (EA_Lister__c != null OR Estate_Agency_Referral__c != null)
        ) 
        OR 
        (RecordType.Name = 'Sale')
    )

"""

df = export_salesforce_data(query)

# Display the DataFrame
df


# In[307]:


Listing = df[
    [
        "Id",
        "OwnerId",
        "Name",
        "Postcode__c",
        "RecordType.Name",
        "Office__c",
        "Office__r.Name",
        "pba__ListingPrice_pb__c",
        # "pba__Property__r.Market_Area__r.Office__c",
        # "pba__Property__r.Market_Area__r.Office__r.Name",
        # "pba__Property__r.Market_Area__r.Previous_Office__c",
        # "pba__Property__r.Market_Area__r.Previous_Office__r.Name",
        "EA_Lister__c",
        "EA_Lister__r.Name",
        "EA_Lister_Profile__c",
        "Estate_Agency_Referral__c",
        "Estate_Agency_Referral__r.Name",
        "Lister_Name__c",
        "pba__Status__c",
        "pba__ListedDate_pb__c",
        "Valuation_Date__c",
        "Withdrawn_Date__c",
        "Calculated_Fee__c",
        "Valuation_Cancelled__c",
        "property_auto_reference__c",
        "Vendor_Contact_Number__c",
        "Rewards_VPM_Id_c__c",
        "Rewards_VPM__c"

    ]
].copy()


# Rename the columns
# Correct the column renaming dictionary
Listing.rename(
    columns={
        "Id": "Listing_Id",
        "OwnerId": "Listing_OwnerId",
        "Name": "Listing_Address",
        "Postcode__c": "Listing_PropertyPostcode",
        "RecordType.Name": "Listing_RecordType",
        "Office__c": "Listing_OfficeCode",
        "Office__r.Name": "Listing_OfficeName",
        # "pba__Property__r.Market_Area__r.Office__c": "Listing_PostCodeofficeId",
        # "pba__Property__r.Market_Area__r.Office__r.Name": "Listing_PostCodeofficeName",

        # "pba__Property__r.Market_Area__r.Previous_Office__c":"Listing_PostCodePreviousOfficeId",
        # "pba__Property__r.Market_Area__r.Previous_Office__r.Name":"Listing_PostCodePreviousOfficeName",
        
        "EA_Lister__c": "Listing_EAListerId",
        "EA_Lister__r.Name": "Listing_EAListerName",
        "EA_Lister_Profile__c": "Listing_EAListerProfile",
        "Estate_Agency_Referral__c": "Listing_ReferralId",
        "Estate_Agency_Referral__r.Name": "Listing_ReferralName",
        "pba__ListingPrice_pb__c": "Listing_ListingPrice",
        "pba__Status__c": "Listing_ListingStatus",
        "Lister_Name__c": "Listing_ListerId",
        "pba__ListedDate_pb__c": "Listing_ListingDate",
        "Valuation_Date__c": "Listing_ValuationDate",
        "Withdrawn_Date__c": "Listing_WithdrawnDate",
        "Valuation_Cancelled__c": "Listing_ValuationCancellationDate",
        "Calculated_Fee__c": "Listing_Fee",
        "property_auto_reference__c": "Property_Auto_Reference",
        "Vendor_Contact_Number__c":"Vendor_Contact",
        "Rewards_VPM_Id_c__c":"Listing_VPMId",
        "Rewards_VPM__c":"Listing_VPMName"
    },
    inplace=True,
)


Listing = convert_to_datetime_or_date(
    Listing, ["Listing_ListingDate"], format_type="date"
).copy()
Listing = convert_to_datetime_or_date(
    Listing, ["Listing_ValuationDate"], format_type="date"
).copy()
Listing = convert_to_datetime_or_date(
    Listing, ["Listing_WithdrawnDate"], format_type="date"
).copy()
Listing = convert_to_datetime_or_date(
    Listing, ["Listing_ValuationCancellationDate"], format_type="date"
).copy()
# print( Listing.dtypes)
Listing


# #### Listing Table Flagging

# In[308]:


today = pd.Timestamp.today()


# Listing Flag
Listing["Flag_Listing"] = np.where(
    (Listing["Listing_RecordType"] == "Sale")
    & (
        Listing["Listing_ListingStatus"].isin(
            [
                "Available",
                "For Sale",
                "Low Profile",
                "Notice Given",
                "On Hold",
                "Referred (WD)",
                "SSTC",
                "Exchanged",
                "Completed",
            ]
        )
    ),
    1,
    0,
)

# Listing Fee
Listing["Flag_ListingFee"] = np.where(    Listing["Flag_Listing"] == 1, Listing["Listing_Fee"], 0)
Listing["Flag_ListingPrice"] = np.where(    Listing["Flag_Listing"] == 1, Listing["Listing_ListingPrice"], 0)


# Listing Withdrawn Flag

Listing.loc[:, "Flag_Withdrawn"] = np.where(
    Listing["Listing_WithdrawnDate"].notna()
    & (Listing["Listing_RecordType"] == "Sale"),
    1,
    0,
)

# Listing Withdrawn Fee

Listing.loc[:, "Flag_WithdrawnFee"] = np.where(
    Listing.loc[:, "Flag_Withdrawn"] == 1, Listing["Listing_Fee"], 0
)


# Auction Instruction Flag
# Ensure EA_Lister_Id is not null or empty and Listing_RecordType is "Auction"
Listing.loc[:, "Flag_ListingAuctionInstruction"] = np.where(
    Listing["Listing_EAListerId"].notna()
    & (Listing["Listing_EAListerId"].str.strip() != "")
    & (Listing["Listing_RecordType"] == "Auction"),
    1,
    0,
)
# Auction Instruction Fee
# Ensure EA_Lister_Id is not null or empty and Listing_RecordType is "Auction"
Listing["Flag_ListingAuctionInstructionFee"] = np.where(
    Listing["Flag_ListingAuctionInstruction"] == 1, Listing["Listing_Fee"], 0
)


# Auction Referral Flag
# Ensure Referral_Id is not null or empty
Listing.loc[:, "Flag_ListingAuctionReferral"] = np.where(
    Listing["Listing_ReferralId"].notna()
    & (Listing["Listing_ReferralId"].str.strip() != "")
    & (Listing["Listing_RecordType"] == "Auction"),
    1,
    0,
)


# Auction Referral Fee
# Ensure Referral_Id is not null or empty
Listing.loc[:, "Flag_ListingAuctionReferralFee"] = np.where(
    Listing["Flag_ListingAuctionReferral"] == 1, Listing["Listing_Fee"], 0
)

# Valuation & Cancellation Flag
Listing.loc[:, "Flag_Valuation"] = np.where(
    Listing["Listing_ValuationDate"].notna(), 1, 0
)
Listing.loc[:, "Flag_ValuationCancellation"] = np.where(
    Listing["Listing_ValuationCancellationDate"].notna(), 1, 0
)

Listing


# #### Mod Owner Id/VPM

# In[309]:


Listing["Mod_Listing_OwnerId"] = np.where(
    Listing["Listing_EAListerId"].notna()
    & (Listing["Listing_EAListerId"].str.strip() != "")
    & (Listing["Listing_RecordType"] == "Auction"),
    Listing["Listing_EAListerId"],
    np.where(
        Listing["Listing_ReferralId"].notna()
        & (Listing["Listing_ReferralId"].str.strip() != "")
        & (Listing["Listing_RecordType"] == "Auction"),
        Listing["Listing_ReferralId"],
        Listing["Listing_OwnerId"],
    ),
)
Listing


# #### Mod_Lister Id

# In[310]:


Listing["Mod_Listing_ListerId"] = np.where(
    Listing["Listing_EAListerId"].notna()
    & (Listing["Listing_EAListerId"].str.strip() != "")
    & (Listing["Listing_RecordType"] == "Auction"),
    Listing["Listing_EAListerId"],
    np.where(
        Listing["Listing_ReferralId"].notna()
        & (Listing["Listing_ReferralId"].str.strip() != "")
        & (Listing["Listing_RecordType"] == "Auction"),
        Listing["Listing_ReferralId"],
        Listing["Listing_ListerId"],
    ),
)
Listing


# #### Postcode office processing 

# In[311]:


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
    merged_data_market_area = pd.merge(
        df, postcode, left_on=column1, right_on='Market_Area', how='left'
    )
    merged_data_district = pd.merge(
        df, postcode, left_on=column2, right_on='Market_Area', how='left'
    )

    # Combine results and handle missing values
    df = merged_data_market_area.fillna(merged_data_district)
    
    return df

# Applying the function to process postal codes
Listing = apply_excel_like_formulas(
    Listing, 'Listing_MarketArea', 'Listing_District', 'Listing_PropertyPostcode'
)
Listing


# In[ ]:





# In[ ]:





# #### Mod_Office

# In[312]:


Listing["Listing_Mod_OfficeId"] = np.where(
    (Listing["Listing_EAListerId"].notna())
    & (Listing["Listing_EAListerId"].str.strip() != "")
    & (Listing["Listing_RecordType"] == "Auction"),
    Listing["PostCodeofficeId"],
    np.where(
        (Listing["Listing_ReferralId"].notna())
        & (Listing["Listing_ReferralId"].str.strip() != "")
        & (Listing["Listing_RecordType"] == "Auction"),
        Listing["PostCodeofficeId"],
        Listing["Listing_OfficeCode"],
    ),
)
Listing


# #### VPM Details

# In[313]:


Listing = pd.merge(
    Listing, vpm, left_on="Listing_Mod_OfficeId", right_on="VPM_OfficeId", how="left"
)
Listing = Listing.drop(columns=["VPM_OfficeId"])
Listing.rename(
    columns={
        "VPM_Office": "Listing_VPM_OfficeName",
        "VPM_UserId": "Listing_VPM_UserId",
        "VPM_Name": "Listing_VPM_Name",
    },
    inplace=True,
)
Listing


# In[314]:


Listing.to_excel("Listing.xlsx")


# #### Staff Details for OwnerID

# In[315]:


Listing = pd.merge(
    Listing,
    Staff_Limited,
    left_on="Mod_Listing_OwnerId",
    right_on="Staff_UserId",
    how="left",
)
Listing = Listing.drop(columns=["Staff_UserId"])
Listing.rename(
    columns={
        "Staff_UserName": "Listing_Mod_OwnerName",
        "Staff_Title": "Listing_Mod_OwnerTitle",
    },
    inplace=True,
)
Listing


# #### Lister ID User Details

# In[316]:


Listing = pd.merge(
    Listing,
    Staff_Limited,
    left_on="Mod_Listing_ListerId",
    right_on="Staff_UserId",
    how="left",
)
Listing = Listing.drop(columns=["Staff_UserId"])
Listing.rename(
    columns={
        "Staff_UserName": "Listing_Mod_ListerName",
        "Staff_Title": "Listing_Mod_ListerTitle",
    },
    inplace=True,
)
Listing


# In[317]:


Listing.dtypes


# In[ ]:





# In[318]:


# Correct the column renaming dictionary
Listing.rename(
    columns={
        "PostCodeofficeId": "Listing_PostCodeofficeId",
        "PostCodeofficeName": "Listing_PostCodeofficeName",
        "PostCodePreviousOfficeId": "Listing_PostCodePreviousOfficeId",
        "PostCodePreviousOfficeName": "Listing_PostCodePreviousOfficeName",
    },
    inplace=True,
)

Listing = Listing.drop(columns=["Listing_MarketArea", "Listing_District"])
Listing


# In[319]:


Listing_Reorder = [
    "Listing_Id",
    "Listing_ListingStatus",
    "Property_Auto_Reference",
    "Listing_Address",
    "Listing_PropertyPostcode",
    "Listing_RecordType",
    "Listing_ListingDate",
    "Listing_ValuationDate",
    "Listing_WithdrawnDate",
    "Listing_ValuationCancellationDate",
    "Listing_ListingPrice",
    "Listing_Fee",
    "Flag_Listing",
    "Flag_ListingFee",
    "Flag_ListingPrice",
    "Flag_Withdrawn",
    "Flag_WithdrawnFee",
    "Flag_ListingAuctionInstruction",
    "Flag_ListingAuctionInstructionFee",
    "Flag_ListingAuctionReferral",
    "Flag_ListingAuctionReferralFee",
    "Flag_Valuation",
    "Flag_ValuationCancellation",
    "Listing_OfficeCode",
    "Listing_OfficeName",


      "Listing_PostCodeofficeId",
      "Listing_PostCodeofficeName",
    
    "Listing_PostCodePreviousOfficeId",
    "Listing_PostCodePreviousOfficeName",
    
    "Listing_Mod_OfficeId",
    "Listing_VPM_OfficeName",
    "Listing_EAListerId",
    "Listing_EAListerName",
    "Listing_EAListerProfile",
    "Listing_ReferralId",
    "Listing_ReferralName",
    "Listing_OwnerId",
    "Mod_Listing_OwnerId",
    "Listing_Mod_OwnerName",
    "Listing_Mod_OwnerTitle",
    "Listing_ListerId",
    "Mod_Listing_ListerId",
    "Listing_Mod_ListerName",
    "Listing_Mod_ListerTitle",
    "Listing_VPM_UserId",
    "Listing_VPM_Name",
    "Listing_VPMId",	
    "Listing_VPMName",	
    "Vendor_Contact"
]
Listing = Listing[Listing_Reorder]
Listing


# In[320]:


Listing=Listing.copy()

# Fill missing values in 'Listing_PostCodePreviousOfficeId' using 'Listing_PostCodeOfficeId'
Listing['Listing_PostCodePreviousOfficeId'].fillna(Listing['Listing_PostCodeofficeId'], inplace=True)

# Fill missing values in 'Listing_PostCodePreviousOfficeName' using 'Listing_PostCodeOfficeName'
Listing['Listing_PostCodePreviousOfficeName'].fillna(Listing['Listing_PostCodeofficeName'], inplace=True)


Listing


# In[321]:


Listing.dtypes


# #### Summary

# In[322]:


print_column_sums(
    Listing,
    "Flag_Listing",
    "Flag_Withdrawn",
    "Flag_ListingAuctionInstruction",
    "Flag_ListingAuctionReferral",
    "Flag_Valuation",
    "Flag_ValuationCancellation",
)


# In[323]:


if __name__ == "__main__":
    # Load DataFrame into MySQL
    load_dataframe_to_mysql(Listing, "Listing")


# #### Exception Details

# ##### Duplicate Listing

# In[324]:


# Select the specified columns
selected_columns = Listing[['Listing_Id', 'Listing_Address', 'Listing_PropertyPostcode']]

# Find all duplicate rows and store them in a DataFrame
duplicates_Listing = selected_columns[selected_columns.duplicated(keep=False)]  # Show all duplicate occurrences

# Count the number of duplicate rows
duplicate_count = duplicates_Listing.shape[0]  # Use correct variable name

# Show duplicate rows
print(f'Number of duplicate values: {duplicate_count}')
duplicates_Listing


# In[325]:


if __name__ == "__main__":
    # Load DataFrame into MySQL
    load_dataframe_to_mysql(duplicates_Listing, "duplicates_Listing")


# In[326]:


# 1. Post Code office & Listing Office is not matching-Need to see
# .2.VPM is not matching for the office against the owner ID
# owner ID is not VPM
# Owner ID is not equal to VPM
# VPM Not Listed
# Post code not giving any office, even though there is an auction there should be some branch from where it is referred or instructed


# In[ ]:





# In[ ]:





# ### Closing

# #### Raw Closing

# In[327]:


# Exchange_Date__c,
#  Success_Fee_To_Be_Paid__c,
#  BP_Net_Of_VAT__c,

query = """
SELECT
 Id,
 pba__Listing__c, 
 OwnerId,
 pba__Listing__r.OwnerId, 
 pba__Offer__r.OwnerId,
 
 Name,
 pba__Listing__r.Name,
 pba__Listing__r.Postcode__c,
 
 pba__Listing__r.Lister_Name__c,
 RecordTypeId,
 RecordType.Name,
 
 pba__Listing__r.Office__c,
 pba__Listing__r.Office__r.Name,
 pba__Listing__r.CALC_Estate_Office_ID__c,

 pba__Listing__r.pba__Property__r.Market_Area__r.Office__c,
 pba__Listing__r.pba__Property__r.Market_Area__r.Office__r.Name,
 
 CreatedById,
 
CreatedDate,
pba__Listing__r.pba__ListedDate_pb__c, 
 Completion_date__c,
 Fee_Received_Date__c,
 Sale_Fallen_Through__c,
 Exchange_Date__c,


 
 Closing_Status__c,
 
 Sale_Price__c,
 Percentage_Selling_Fee__c,
 Calculated_Fee__c,
 Fee_Received_Amount__c, 
 Success_Fee_To_Be_Paid__c,
 BP_Net_Of_VAT__c,
 
 FLAG_6_Week_sale__c,
 
 pba__Listing__r.EA_Lister__c,
 pba__Listing__r.EA_Lister__r.Name,
 pba__Listing__r.Estate_Agency_Referral__c,
 pba__Listing__r.Estate_Agency_Referral__r.Name,
 Buying_Advisor__c,
 pba__Listing__r.Vendor_Contact_Number__c,
 
 Property_Auto_Reference__c


FROM
 pba__Closing__c  
WHERE 
 (CreatedDate > 2023-06-30T00:00:00Z or Sale_Fallen_Through__c>2023-06-30 or Completion_date__c>2023-06-30 or Fee_Received_Date__c>2023-06-30) and RecordType.Name!='DELETED' 
   and     (RecordType.Name = 'Sale' OR pba__Listing__r.EA_Lister__c != null OR  pba__Listing__r.Estate_Agency_Referral__c != null)
"""
# # # export_file = 'test.csv'

# Get the DataFrame
df = export_salesforce_data(query)

# df
Closing = df[
 [
     "Id",
     "OwnerId",
     "pba__Listing__c",
     "pba__Listing__r.OwnerId",
     "Name",
     "pba__Listing__r.Name",
     "pba__Listing__r.Postcode__c",
     "pba__Listing__r.Lister_Name__c",
     "pba__Offer__r.OwnerId",
     "RecordTypeId",
     "RecordType.Name",
     "pba__Listing__r.Office__c",
     "pba__Listing__r.Office__r.Name",
     "pba__Listing__r.CALC_Estate_Office_ID__c",
     
     # "pba__Listing__r.pba__Property__r.Market_Area__r.Office__c",
     # "pba__Listing__r.pba__Property__r.Market_Area__r.Office__r.Name",
     
     "CreatedById",
     "CreatedDate",

     # Date
     "pba__Listing__r.pba__ListedDate_pb__c",
     "Completion_date__c",
     "Fee_Received_Date__c",
     "Sale_Fallen_Through__c",
     "Closing_Status__c",
     "Exchange_Date__c",

     # Fee
     "Sale_Price__c",
     "Percentage_Selling_Fee__c",
     "Calculated_Fee__c",
     "Fee_Received_Amount__c",
     "Success_Fee_To_Be_Paid__c",
     "BP_Net_Of_VAT__c",
     
     "FLAG_6_Week_sale__c",
     "pba__Listing__r.EA_Lister__c",
     "pba__Listing__r.EA_Lister__r.Name",
     "pba__Listing__r.Estate_Agency_Referral__c",
     "pba__Listing__r.Estate_Agency_Referral__r.Name",
     "Property_Auto_Reference__c",
     "Buying_Advisor__c",
     "pba__Listing__r.Vendor_Contact_Number__c"
 ]
].copy()


Closing.rename(
 columns={
     "Id": "Closing_Id",
     "pba__Listing__c": "Closing_Listing_ListingId",
     "OwnerId": "Closing_OwnerId",
     "pba__Listing__r.OwnerId": "Closing_Listing_OwnerId",
     "Name": "Closing_ClosingName",
     "pba__Listing__r.Name": "Closing_Listing_Address",
     
     "pba__Listing__r.Postcode__c": "Closing_Listing_Postcode",
     "pba__Listing__r.Lister_Name__c": "Closing_Listing_ListerId",

     
     "pba__Offer__r.OwnerId": "Closing_Offer_OwnerId",
     "RecordTypeId": "Closing_RecordTypeId",
     "RecordType.Name": "Closing_RecordName",
     "pba__Listing__r.Office__c": "Closing_Listing_OfficeId",
     "pba__Listing__r.Office__r.Name": "Closing_Listing_OfficeName",
     # "pba__Listing__r.CALC_Estate_Office_ID__c":"Closing_Listing_Mod_OfficeId",
     "pba__Listing__r.pba__Property__r.Market_Area__r.Office__c": "Listing_PostCodeOfficeId",
     "pba__Listing__r.pba__Property__r.Market_Area__r.Office__r.Name": "Listing_PostCodeOfficeName",
     "CreatedById": "Closing_CreatedById",
     
     # date
     "CreatedDate": "Closing_ClosingDate",
     "pba__Listing__r.pba__ListedDate_pb__c": "Closing_ListingDate",
     "Completion_date__c": "Closing_CompletionDate",
     "Fee_Received_Date__c": "Closing_FeeReceivedDate",
     "Sale_Fallen_Through__c": "Closing_SaleFallenThroughDate",
     "Exchange_Date__c":"Closing_Exchange_Date",
     "Closing_Status__c": "Closing_Status",
     
     # Fee & Price
     "Sale_Price__c": "Closing_SalesPrice",
     "Percentage_Selling_Fee__c": "Closing_PercentageSellingFee",
     "Calculated_Fee__c": "Closing_SalesFee",
     "Fee_Received_Amount__c": "Closing_FeeReceivedAmount",
     "Success_Fee_To_Be_Paid__c":"Closing_Success_Fee",
     "BP_Net_Of_VAT__c":"Closing_BP_Net_Of_VAT",

     # Flag & Owner
     "FLAG_6_Week_sale__c": "Closing_FLAG6Weeksales",
     "pba__Listing__r.EA_Lister__c": "Closing_Listing_EAListerId",
     "pba__Listing__r.EA_Lister__r.Name": "Closing_Listing_EAListerName",
     "pba__Listing__r.Estate_Agency_Referral__c": "Closing_Listing_ReferralId",
     "pba__Listing__r.Estate_Agency_Referral__r.Name": "Closing_Listing_ReferralName",
     "Property_Auto_Reference__c": "Property_Auto_Reference",
     "Buying_Advisor__c": "Closing_BuyingAdvisorId",
     "pba__Listing__r.Vendor_Contact_Number__c":"Vendor_Contact"
 },
 inplace=True,
)

Closing = convert_to_datetime_or_date(
 Closing, ["Closing_ClosingDate"], format_type="date"
)
Closing = convert_to_datetime_or_date(
 Closing, ["Closing_CompletionDate"], format_type="date"
)
Closing = convert_to_datetime_or_date(
 Closing, ["Closing_FeeReceivedDate"], format_type="date"
)
Closing = convert_to_datetime_or_date(
 Closing, ["Closing_SaleFallenThroughDate"], format_type="date"
)
Closing = convert_to_datetime_or_date(
 Closing, ["Closing_ListingDate"], format_type="date"
)
Closing = convert_to_datetime_or_date(
 Closing, ["Closing_Exchange_Date"], format_type="date"
)


# Display the DataFrame
Closing


# #### Creating Flags

# In[328]:


# Closing Flag
Closing["Flag_Sales"] = np.where(
    (Closing["Closing_RecordName"] == "Sale")
    & (Closing["Closing_Listing_OfficeName"] != "Auction"),
    1,
    0,
)
# Closing Flag Fee
Closing["Flag_SalesFee"] = np.where(    Closing["Flag_Sales"] == 1, Closing["Closing_SalesFee"], 0)
Closing["Flag_SalesPrice"] = np.where(    Closing["Flag_Sales"] == 1, Closing["Closing_SalesPrice"], 0)


# Auction Flag
Closing["Flag_Auction"] = np.where(
    (Closing["Closing_RecordName"] == "Auction")
    & (Closing["Closing_Listing_OfficeName"] == "Auction"),
    1,
    0,
)
# Auction FlagFee
Closing["Flag_AuctionFee"] = np.where(
    Closing["Flag_Auction"] == 1, Closing["Closing_SalesFee"], 0
)


# Completed sales Flag
Closing["Flag_CompletedSales"] = np.where(
    (Closing["Flag_Sales"] == 1) & (Closing["Closing_CompletionDate"].notna()), 1, 0
)
# Completed salesFee
Closing["Flag_CompletedSalesFee"] = np.where(
    Closing["Flag_CompletedSales"] == 1, Closing["Closing_SalesFee"], 0
)


# Check for non-null and non-blank values in EA_Lister_Id and Referral_Id
# Acution Instruction
Closing["Flag_AuctionInstruction"] = np.where(
    Closing["Closing_Listing_EAListerId"].notna()
    & (Closing["Closing_Listing_EAListerId"].str.strip() != "")
    & (Closing["Closing_RecordName"] == "Auction"),
    1,
    0,
)
Closing["Flag_AuctionInstructionFee"] = np.where(
    Closing["Flag_AuctionInstruction"] == 1, Closing["Closing_SalesFee"], 0
)


Closing["Flag_ClosingAuctionReferral"] = np.where(
    Closing["Closing_Listing_ReferralId"].notna()
    & (Closing["Closing_Listing_ReferralId"].str.strip() != "")
    & (Closing["Closing_RecordName"] == "Auction"),
    1,
    0,
)
Closing["Flag_ClosingAuctionReferralFee"] = np.where(
    Closing["Flag_ClosingAuctionReferral"] == 1, Closing["Closing_SalesFee"], 0
)

# np.where(,  Closing['Closing_SalesFee'], 0)
# Flag if sales is done in 6 weeks
# Converting 1 to 0 where sales conditions does not match
# Count
Closing["Flag_SaleIn6Week"] = np.where(
    (Closing["Closing_FLAG6Weeksales"] == 1) & (Closing["Flag_Sales"] == 0),
    0,
    Closing["Closing_FLAG6Weeksales"],
)
# Fee
Closing["Flag_SaleIn6WeekFee"] = np.where(
    Closing["Flag_SaleIn6Week"] == 1, Closing["Closing_SalesFee"], 0
)

# drop the earlier column
Closing = Closing.drop(columns=["Closing_FLAG6Weeksales"])

Closing.loc[:, "Flag_SalesFallen"] = np.where(
    (Closing["Closing_SaleFallenThroughDate"].notna()) & (Closing["Flag_Sales"] == 1),
    1,
    0,
)
Closing.loc[:, "Flag_SalesFallenFee"] = np.where(
    Closing.loc[:, "Flag_SalesFallen"] == 1, Closing["Closing_SalesFee"], 0
)

# Fee Received Flag/Cashbook Number
Closing["Flag_FeeReceived"] = np.where(Closing["Closing_FeeReceivedDate"].notna(), 1, 0)

# Fee Received Amount
Closing["Flag_FeeReceivedFee"] = np.where(
    Closing["Flag_FeeReceived"] == 1, Closing["Closing_FeeReceivedAmount"], 0
)


Closing


# In[329]:


Closing.to_excel("Closing.xlsx")


# #### Mod Listing Owner ID/VPM

# In[330]:


Closing["Closing_Mod_Listing_OwnerId"] = np.where(
    Closing["Closing_Listing_EAListerId"].notna()
    & (Closing["Closing_Listing_EAListerId"].str.strip() != "")
    & (Closing["Closing_RecordName"] == "Auction"),
    Closing["Closing_Listing_EAListerId"],
    np.where(
        Closing["Closing_Listing_ReferralId"].notna()
        & (Closing["Closing_Listing_ReferralId"].str.strip() != "")
        & (Closing["Closing_RecordName"] == "Auction"),
        Closing["Closing_Listing_ReferralId"],
        Closing["Closing_Listing_OwnerId"],
    ),
)
Closing


# #### Mod Closing Owner ID/Sales Progressor

# In[331]:


Closing["Closing_Mod_OwnerId"] = np.where(
    Closing["Closing_Listing_EAListerId"].notna()
    & (Closing["Closing_Listing_EAListerId"].str.strip() != "")
    & (Closing["Closing_RecordName"] == "Auction"),
    Closing["Closing_Listing_EAListerId"],
    np.where(
        Closing["Closing_Listing_ReferralId"].notna()
        & (Closing["Closing_Listing_ReferralId"].str.strip() != "")
        & (Closing["Closing_RecordName"] == "Auction"),
        Closing["Closing_Listing_ReferralId"],
        Closing["Closing_OwnerId"],
    ),
)
Closing


# #### Mod Lister

# In[332]:


Closing["Closing_Mod_Listing_ListerId"] = np.where(
    Closing["Closing_Listing_EAListerId"].notna()
    & (Closing["Closing_Listing_EAListerId"].str.strip() != "")
    & (Closing["Closing_RecordName"] == "Auction"),
    Closing["Closing_Listing_EAListerId"],
    np.where(
        Closing["Closing_Listing_ReferralId"].notna()
        & (Closing["Closing_Listing_ReferralId"].str.strip() != "")
        & (Closing["Closing_RecordName"] == "Auction"),
        Closing["Closing_Listing_ReferralId"],
        Closing["Closing_Listing_ListerId"],
    ),
)
Closing


# #### Mod Buying Advisor

# In[333]:


Closing["Closing_Mod_BuyingAdvisorId"] = np.where(
    Closing["Closing_Listing_EAListerId"].notna()
    & (Closing["Closing_Listing_EAListerId"].str.strip() != "")
    & (Closing["Closing_RecordName"] == "Auction"),
    Closing["Closing_Listing_EAListerId"],
    np.where(
        Closing["Closing_Listing_ReferralId"].notna()
        & (Closing["Closing_Listing_ReferralId"].str.strip() != "")
        & (Closing["Closing_RecordName"] == "Auction"),
        Closing["Closing_Listing_ReferralId"],
        Closing["Closing_BuyingAdvisorId"],
    ),
)
Closing


# #### Office operation based on postcode

# In[334]:


Closing = apply_excel_like_formulas(
    Closing, 'Closing_MarketArea', 'Closing_District', 'Closing_Listing_Postcode'
)
Closing


# In[ ]:





# In[335]:


# Correct the column renaming dictionary
Closing.rename(
    columns={
        "PostCodeofficeId": "Listing_PostCodeOfficeId",
        "PostCodeofficeName": "Listing_PostCodeOfficeName",
        "PostCodePreviousOfficeId": "Listing_PostCodePreviousOfficeId",
        "PostCodePreviousOfficeName": "Listing_PostCodePreviousOfficeName",
    },
    inplace=True,
)

# Closing = Listing.drop(columns=["Closing_MarketArea", "Closing_District"])
Closing


# #### Mod Office

# In[336]:


Closing["Closing_Listing_Mod_OfficeId"] = np.where(
    Closing["Closing_Listing_EAListerId"].notna()
    & (Closing["Closing_Listing_EAListerId"].str.strip() != "")
    & (Closing["Closing_RecordName"] == "Auction"),
    Closing["Listing_PostCodeOfficeId"],
    np.where(
        Closing["Closing_Listing_ReferralId"].notna()
        & (Closing["Closing_Listing_ReferralId"].str.strip() != "")
        & (Closing["Closing_RecordName"] == "Auction"),
        Closing["Listing_PostCodeOfficeId"],
        Closing["Closing_Listing_OfficeId"],
    ),
)
Closing


# #### Mod VPM

# In[337]:


Closing = pd.merge(
    Closing,
    vpm,
    left_on="Closing_Listing_Mod_OfficeId",
    right_on="VPM_OfficeId",
    how="left",
)
Closing = Closing.drop(columns=["VPM_OfficeId"])
Closing.rename(
    columns={
        "VPM_Office": "Closing_Mod_OfficeName",
        "VPM_UserId": "Closing_VPM_UserId",
        "VPM_Name": "Closing_VPM_Name",
    },
    inplace=True,
)
Closing


# #### Listing Owner ID details

# In[338]:


Closing = pd.merge(
    Closing,
    Staff_Limited,
    left_on="Closing_Mod_Listing_OwnerId",
    right_on="Staff_UserId",
    how="left",
)
Closing = Closing.drop(columns=["Staff_UserId"])
Closing.rename(
    columns={
        "Staff_UserName": "Closing_Listing_Mod_OwnerName",
        "Staff_Title": "Closing_Listing_Mod_OwnerTitle",
    },
    inplace=True,
)
Closing


# #### Closing  Owner ID details

# In[339]:


Closing = pd.merge(
    Closing,
    Staff_Limited,
    left_on="Closing_Mod_OwnerId",
    right_on="Staff_UserId",
    how="left",
)
Closing = Closing.drop(columns=["Staff_UserId"])
Closing.rename(
    columns={
        "Staff_UserName": "Closing_Mod_OwnerName",
        "Staff_Title": "Closing_Mod_OwnerTitle",
    },
    inplace=True,
)
Closing


# #### Listing_Lister  ID details

# In[340]:


Closing = pd.merge(
    Closing,
    Staff_Limited,
    left_on="Closing_Mod_Listing_ListerId",
    right_on="Staff_UserId",
    how="left",
)
Closing = Closing.drop(columns=["Staff_UserId"])
Closing.rename(
    columns={
        "Staff_UserName": "Closing_Listing_Mod_ListerName",
        "Staff_Title": "Closing_Listing_Mod_ListerTitle",
    },
    inplace=True,
)
Closing


# #### Buying Advisor details

# In[341]:


Closing = pd.merge(
    Closing,
    Staff_Limited,
    left_on="Closing_Mod_BuyingAdvisorId",
    right_on="Staff_UserId",
    how="left",
)
Closing = Closing.drop(columns=["Staff_UserId"])
Closing.rename(
    columns={
        "Staff_UserName": "Closing_Mod_BuyingAdvisorName",
        "Staff_Title": "Closing_Mod_BuyingAdvisorTitle",
    },
    inplace=True,
)
Closing


# #### Offer ID Details

# In[342]:


Closing = pd.merge(
    Closing,
    Staff_Limited,
    left_on="Closing_Offer_OwnerId",
    right_on="Staff_UserId",
    how="left",
)
Closing = Closing.drop(columns=["Staff_UserId"])
Closing.rename(
    columns={
        "Staff_UserName": "Closing_OfferOwnerName",
        "Staff_Title": "Closing_OfferOwnerTitle",
    },
    inplace=True,
)
Closing


# #### Reorder

# In[343]:


Closing.dtypes


# In[344]:


closing_reorder = [
    "Closing_Listing_ListingId",
    "Closing_Id",
    "Closing_ClosingName",
    "Property_Auto_Reference",
    "Closing_Listing_Address",
    "Closing_Listing_Postcode",
    "Closing_RecordTypeId",
    "Closing_RecordName",
    "Closing_Status",
    "Closing_CreatedById",

    # Date
    "Closing_ClosingDate",
    "Closing_ListingDate",
    "Closing_CompletionDate",
    "Closing_FeeReceivedDate",
    "Closing_SaleFallenThroughDate",
    "Closing_Exchange_Date",

    # Fee & Price
    "Closing_SalesPrice",
    "Closing_PercentageSellingFee",
    "Closing_SalesFee",
    "Closing_FeeReceivedAmount",
    "Closing_Success_Fee",
    "Closing_BP_Net_Of_VAT",

    # Relevent Owner
    "Closing_Listing_EAListerId",
    "Closing_Listing_EAListerName",
    "Closing_Listing_ReferralId",
    "Closing_Listing_ReferralName",

    # Flag
    "Flag_Sales",
    "Flag_SalesFee",
    "Flag_SalesPrice",
    "Flag_Auction",
    "Flag_AuctionFee",
    "Flag_FeeReceived",
    "Flag_FeeReceivedFee",
    "Flag_CompletedSales",
    "Flag_CompletedSalesFee",
    "Flag_AuctionInstruction",
    "Flag_AuctionInstructionFee",
    "Flag_ClosingAuctionReferral",
    "Flag_ClosingAuctionReferralFee",
    "Flag_SaleIn6Week",
    "Flag_SaleIn6WeekFee",
    "Flag_SalesFallen",
    "Flag_SalesFallenFee",
    
    "Closing_Listing_OfficeId",
    "Closing_Listing_OfficeName",
    "Closing_Listing_Mod_OfficeId",
    "Closing_Mod_OfficeName",
    "Listing_PostCodePreviousOfficeId",
    "Listing_PostCodePreviousOfficeName",
    
    "Closing_Listing_OwnerId",
    "Closing_Mod_Listing_OwnerId",
    "Closing_Listing_Mod_OwnerName",
    "Closing_Listing_Mod_OwnerTitle",
    "Closing_OwnerId",
    "Closing_Mod_OwnerId",
    "Closing_Mod_OwnerName",
    "Closing_Mod_OwnerTitle",
    "Closing_Listing_ListerId",
    "Closing_Mod_Listing_ListerId",
    "Closing_Listing_Mod_ListerName",
    "Closing_Listing_Mod_ListerTitle",
    "Closing_BuyingAdvisorId",
    "Closing_Mod_BuyingAdvisorId",
    "Closing_Mod_BuyingAdvisorName",
    "Closing_Mod_BuyingAdvisorTitle",
    "Closing_VPM_UserId",
    "Closing_VPM_Name",
    "Closing_Offer_OwnerId",
    "Closing_OfferOwnerName",
    "Closing_OfferOwnerTitle",
    "Vendor_Contact"
]

Closing = Closing[closing_reorder]
Closing


# #### Summary

# In[345]:


print_column_sums(
    Closing,
    "Flag_Sales",
    "Flag_Auction",
    "Flag_CompletedSales",
    "Flag_AuctionInstruction",
    "Flag_ClosingAuctionReferral",
    "Flag_SaleIn6Week",
    "Flag_SalesFallen",
)


# In[346]:


if __name__ == "__main__":
    # Load DataFrame into MySQL
    load_dataframe_to_mysql(Closing, "Closing")


# In[347]:


Closing.dtypes


# In[348]:


# Select the specified columns
selected_columns = Closing[['Closing_Id', 'Closing_Listing_Address', 'Closing_Listing_Postcode']]

# Find duplicate rows (keep=False ensures all duplicates are marked)
duplicates_closing = selected_columns[selected_columns.duplicated(keep=False)]

# Count the number of duplicate rows
duplicate_count = duplicates_closing.shape[0]

# Show duplicate rows
print(f'Number of duplicate values: {duplicate_count}')

duplicates_closing


# In[ ]:





# ### Contact

# #### Hot Buyers

# In[349]:


import numpy as np

# Define SOQL query to retrieve the necessary fields from the Contact object
query = """
SELECT 
    Id,
    AIP__c,
    pba__Stage_pb__c,
    Record_Type_Name__c,
    LeadSource,
    PhotoUrl,
    Mortgage_Date__c,
    Mortgage_Appointment__c,
    Mortgage_Signed_Up__c,
    Mortgage_Broker_Edward_Mellor__c,
    Mortgage_Referred_By_Who__c,
    pba__Office_pb__c,
    pba__Office_pb__r.Name
FROM
    contact
WHERE
    pba__Stage_pb__c = 'Hot Buyer'
    AND Record_Type_Name__c = 'Individual Client'
"""

# Fetch the data from Salesforce into a DataFrame
df = export_salesforce_data(query)

# Select the relevant columns and create a copy for further processing
Contact = df[
    [
        "Id",
        "AIP__c",
        "pba__Stage_pb__c",
        "Record_Type_Name__c",
        "LeadSource",
        "PhotoUrl",
        "Mortgage_Date__c",
        "Mortgage_Appointment__c",
        "Mortgage_Signed_Up__c",
        "Mortgage_Broker_Edward_Mellor__c",
        "Mortgage_Referred_By_Who__c",
        "pba__Office_pb__c",
        "pba__Office_pb__r.Name",
    ]
].copy()

# Rename columns to more meaningful names
Contact.rename(
    columns={
        "Id": "Contact_Id",
        "AIP__c": "Contact_AIPDate",
        "pba__Stage_pb__c": "Contact_Stage",
        "Record_Type_Name__c": "Contact_RecordTypeName",
        "Mortgage_Date__c": "Contact_MortgageDate",
        "Mortgage_Appointment__c": "Contact_MortgageAppointmentDate",
        "Mortgage_Signed_Up__c": "Contact_MortgageSignedUp",
        "Mortgage_Broker_Edward_Mellor__c": "Flag_Contact_MortgageBrokerEdwardMellor",
        "Mortgage_Referred_By_Who__c": "Contact_MortgageReferrer",
        "pba__Office_pb__c": "Contact_OfficeId",
        "pba__Office_pb__r.Name": "Contact_OfficeName",
    },
    inplace=True,
)

# Convert specific date fields to the proper datetime format
Contact = convert_to_datetime_or_date(Contact, ["Contact_AIPDate"], format_type="date")
Contact = convert_to_datetime_or_date(
    Contact, ["Contact_MortgageDate"], format_type="date"
)
Contact = convert_to_datetime_or_date(
    Contact, ["Contact_MortgageAppointmentDate"], format_type="date"
)
Contact = convert_to_datetime_or_date(
    Contact, ["Contact_MortgageSignedUp"], format_type="date"
)

# Return the processed DataFrame
Contact


# In[350]:


Contact = pd.merge(
    Contact,
    Staff_Limited,
    left_on="Contact_MortgageReferrer",
    right_on="Staff_UserId",
    how="left",
)
Contact["Contact_Flag_HotBuyers"] = 1
Contact


# In[351]:


Contact.dtypes


# In[352]:


Contact.rename(
    columns={
        "Staff_UserId": "Contact_MortgageReferrerId",
        "Staff_UserName": "Contact_MortgageReferrerName",
        "Staff_Title": "Contact_MortgageReferrerTitle",
    },
    inplace=True,
)
Contact


# In[353]:


if __name__ == "__main__":
    # Load DataFrame into MySQL
    load_dataframe_to_mysql(Contact, "Contact")


# ### Opportunity

# #### Raw Opportunity

# In[354]:


import numpy as np

# Define SOQL query to retrieve the necessary fields from the Opportunity object
query = """
SELECT 
    Id,
    OwnerId,
    RecordTypeId,
    Record_Type_Name__c,
    Name,
    CreatedDate,
    Date_of_Sign_Up__c,
    Appointment_MakerLOOKUP__c,
    Appointment_MakerLOOKUP__r.Name,
    Appointment_MakerLOOKUP__r.Title,
    Appointment_MakerLOOKUP__r.SYS_EM_Office_ID__c,
    Contact__c,
    Contact__r.Name,
    Applicant_Type__c,
    Listing__c,
    Listing__r.Name,
    Closing__c,
    Closing__r.Name,
    Closing__r.Office__c,
    Listing__r.Office__c,
    Listing__r.Office__r.Name,
    Closing__r.Vendor_Manager__c,
    LeadSource,
    Appointment_Type__c,
    Total_Commission__c
FROM
    Opportunity
WHERE
    Record_Type_Name__c = 'Mortgage'
    AND Date_of_Sign_Up__c != NULL
    AND Appointment_MakerLOOKUP__c != NULL
    AND Date_of_Sign_Up__c > 2024-06-27
"""

# Fetch the data from Salesforce into a DataFrame
df = export_salesforce_data(query)

# Select the relevant columns and create a copy for further processing
Opportunity = df[
    [
        "Id",
        "OwnerId",
        "RecordTypeId",
        "Record_Type_Name__c",
        "Name",
        "CreatedDate",
        "Date_of_Sign_Up__c",
        "Appointment_MakerLOOKUP__c",
        "Appointment_MakerLOOKUP__r.Name",
        "Appointment_MakerLOOKUP__r.Title",
        "Contact__c",
        "Contact__r.Name",
        "Applicant_Type__c",
        "Appointment_MakerLOOKUP__r.SYS_EM_Office_ID__c",
        "Listing__c",
        "Listing__r.Name",
        "Closing__c",
        "Closing__r.Name",
        "Closing__r.Office__c",
        "Listing__r.Office__c",
        "Listing__r.Office__r.Name",
        "Closing__r.Vendor_Manager__c",
        "LeadSource",
        "Appointment_Type__c",
        "Total_Commission__c",
    ]
].copy()

# Rename columns to more meaningful names
Opportunity.rename(
    columns={
        "Id": "Opportunity_Id",
        "OwnerId": "Opportunity_OwnerId",
        "RecordTypeId": "Opportunity_RecordTypeId",
        "Name": "Opportunity_Name",
        "Date_of_Sign_Up__c": "Opportunity_SignupDate",
        "Record_Type_Name__c": "Opportunity_RecordTypeName",
        "CreatedDate": "Opportunity_CreatedDate",
        "Appointment_MakerLOOKUP__c": "Opportunity_AppointmentmakerId",
        "Appointment_MakerLOOKUP__r.Name": "Opportunity_AppointmentmakerName",
        "Appointment_MakerLOOKUP__r.Title": "Opportunity_AppointmentmakerTitle",
        "Appointment_MakerLOOKUP__r.SYS_EM_Office_ID__c": "Opportunity_AppointmentMakerOfficeId",
        "Contact__c": "Contact_Id",
        "Contact__r.Name": "Contact_Name",
        "Applicant_Type__c": "Opportunity_ApplicantType",
        "Listing__c": "Opportunity_ListingId",
        "Listing__r.Name": "Opportunity_ListingAddress",
        "Closing__c": "Opportunity_ClosingId",
        "Closing__r.Name": "Opportunity_ClosingName",
        "Closing__r.Office__c": "Opportunity_ClosingOffice",
        "Listing__r.Office__c": "Opportunity_ListingOfficeId",
        "Listing__r.Office__r.Name": "Opportunity_ListingOfficeName",
        "Closing__r.Vendor_Manager__c": "Opportunity_VPMId",
        "Appointment_Type__c": "Opportunity_Classification",
        "LeadSource": "Opportunity_LeadSource",
        "Total_Commission__c": "Opportunity_MortgageCommission",
    },
    inplace=True,
)

# Convert specific date fields to the proper datetime format
Opportunity = convert_to_datetime_or_date(
    Opportunity, ["CreatedDate"], format_type="date"
)
Opportunity = convert_to_datetime_or_date(
    Opportunity, ["Opportunity_SignupDate"], format_type="date"
)


# Return the processed DataFrame
Opportunity


# #### Opportunity Flagging

# In[355]:


# Add flags based on certain conditions
Opportunity["Flag_Closing_FSSignup"] = 1  # Mark all as 1 for FSSignup
Opportunity["Flag_Closing_EMSignup"] = np.where(
    Opportunity["Opportunity_ClosingId"].notna(), 1, 0
)
Opportunity["Flag_SelfSignupByVPM"] = np.where(
    Opportunity["Opportunity_AppointmentmakerTitle"].str.contains("Vendor", na=False),
    1,
    0,
)
# Opportunity['Flag_SignupByVendor'] = np.where(Opportunity['Opportunity_ApplicantType'] contains ('Vendor'), 1, 0)
Opportunity["Flag_SignupByVendor"] = np.where(
    Opportunity["Opportunity_ApplicantType"].str.contains("Vendor", na=False), 1, 0
)
Opportunity["Flag_SignupByVPMwithVendor"] = np.where(
    (Opportunity["Opportunity_AppointmentmakerTitle"].str.contains("Vendor", na=False))
    & (Opportunity["Flag_SignupByVendor"] == 1),
    1,
    0,
)


# Flag EMSignup if ClosingId is not null
Opportunity


# In[356]:


Opportunity = pd.merge(
    Opportunity,
    Office,
    left_on="Opportunity_AppointmentMakerOfficeId",
    right_on="Office_OfficeId",
    how="left",
)
Opportunity = Opportunity.drop(columns=["Office_OfficeId", "key"])
Opportunity.rename(
    columns={
        "Staff_UserName": "Closing_OfferOwnerName",
        "Staff_Title": "Closing_OfferOwnerTitle",
    },
    inplace=True,
)
Opportunity


# #### VPM 

# In[357]:


Opportunity = pd.merge(
    Opportunity,
    vpm,
    left_on="Opportunity_AppointmentMakerOfficeId",
    right_on="VPM_OfficeId",
    how="left",
)
Opportunity = Opportunity.drop(columns=["VPM_OfficeId"])
Opportunity.rename(
    columns={
        "VPM_UserId": "Closing_VPM_UserId",
        "VPM_Name": "Closing_VPM_Name",
    },
    inplace=True,
)
Opportunity


# In[358]:


vpm


# #### Summary

# In[359]:


print_column_sums(Opportunity, "Flag_Closing_FSSignup", "Flag_Closing_EMSignup")


# In[360]:


Opportunity.dtypes


# In[361]:


if __name__ == "__main__":
    # Load DataFrame into MySQL
    load_dataframe_to_mysql(Opportunity, "Opportunity")


# In[ ]:




