#!/usr/bin/env python
# coding: utf-8

# # VPM Reward 01/10/2024
# 
# 
# 
# 

# ## Basic Setup

# ### Folder Assignement

# In[118]:


import os

# Change the current working directory
os.chdir('C:/Users/srigd/Desktop/My Project/Dashboard/Reward/VPM_AVPM')

# Now, when you open a file without specifying a full path, Python looks in the current working directory
with open('another_file.txt', 'w') as f:
    f.write('This file is saved in the specified default directory.')


# ### Function Setup

# #### Object to Date Function

# In[119]:


import pandas as pd
import numpy as np

def convert_to_datetime_or_date(df, columns, format_type='datetime'):
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
            if format_type == 'datetime':
                df[column] = pd.to_datetime(df[column])
                # Remove timezone if present to ensure consistency
                df[column] = df[column].dt.tz_localize(None)
            elif format_type == 'date':
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




# #### Access table from Salesforce

# In[120]:


import requests
import pandas as pd
from simple_salesforce import Salesforce
import keyring

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
        'grant_type': 'password',
        'client_id': consumer_key,
        'client_secret': consumer_secret,
        'username': username,
        'password': password + security_token
    }
    response = requests.post(token_url, data=payload)
    response.raise_for_status()  # Check if the request was successful

    # Extract access token from the response
    access_token = response.json().get('access_token')
    instance_url = response.json().get('instance_url')

    # Step 2: Authenticate to Salesforce using the access token
    sf = Salesforce(instance_url=instance_url, session_id=access_token)

    # Step 3: Query data
    records = []
    query_result = sf.query_all(query)
    records.extend(query_result['records'])

    # Continue querying if there are more records
    while not query_result['done']:
        query_result = sf.query_more(query_result['nextRecordsUrl'], True)
        records.extend(query_result['records'])

    # Function to flatten nested dictionaries
    def flatten_record(record, parent_key='', sep='.'):
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
    if 'attributes.type' in df.columns:
        df = df.drop(columns=['attributes.type', 'attributes.url'])

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




# #### Check Duplicate

# In[121]:


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
data = {
    'A': [1, 2, 2, 4],
    'B': [5, 6, 6, 8],
    'C': ['X', 'Y', 'Y', 'Z']
}

df = pd.DataFrame(data)

# Check for duplicates in a single column
check_duplicates(df, 'A')

# Check for duplicates in multiple columns
check_duplicates(df, ['A', 'B'])




# #### Exporting the data to MYSQL80

# In[122]:


import pandas as pd
from sqlalchemy import create_engine
import urllib.parse
import win32cred
from sqlalchemy.orm import sessionmaker

def get_windows_credentials(target_name):
    """Retrieve credentials from Windows Credential Manager."""
    creds = win32cred.CredRead(target_name, win32cred.CRED_TYPE_GENERIC, 0)
    username = creds['UserName']
    password = creds['CredentialBlob'].decode('utf-16')
    return username, password

def load_dataframe_to_mysql(df, table_name):
    """Load a DataFrame into a MySQL table with the same structure as the DataFrame."""
    # Retrieve credentials
    target_name = 'SQLServerConnection'  # The name you used when storing the credentials
    username, password = get_windows_credentials(target_name)
    
    # MySQL connection details
    host = 'localhost'  # 'localhost' for local server
    database = 'edwardmellorsalesforce'  # Replace with your MySQL database name
    
    # URL-encode the password
    encoded_password = urllib.parse.quote_plus(password)
    
    # Create a connection string
    connection_string = f'mysql+mysqlconnector://{username}:{encoded_password}@{host}/{database}'
    
    # Create SQLAlchemy engine with increased timeout and autocommit
    engine = create_engine(connection_string, connect_args={"connect_timeout": 600, "autocommit": True})
    
    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Convert table name to lowercase to avoid case sensitivity issues
        table_name = table_name.lower()
        
        # Debug: Print status before loading the DataFrame
        print(f"Loading DataFrame into MySQL table '{table_name}'...")
        
        # Load DataFrame into MySQL with chunking
        df.to_sql(name=table_name, con=engine, if_exists='replace', index=False, chunksize=1000)
        
        # Commit the session
        session.commit()

        # Debug: Confirm table creation
        print(f"DataFrame successfully exported to MySQL database into table '{table_name}'")
        
    except Exception as e:
        # Rollback in case of error
        session.rollback()
        print(f"Error: {e}")
    finally:
        # Ensure the connection is properly closed
        session.close()
        engine.dispose()
        print("Database connection closed.")

# Example of calling it

# if __name__ == "__main__":
#     # Load DataFrame into MySQL
#     load_dataframe_to_mysql(Master, 'Master')



# ### Data Extraction

# #### User

# In[123]:


# Example usage
query = """
SELECT
    id,
    User__c, 
    Name, 
    Primary__c,
    Primary__r.Name,
    Staff_Activated__c,
    Primary__r.POD__r.Name,
    Role_Title__r.Name  
FROM
    Staff__c
"""
export_file = 'test.csv'

# Get the DataFrame
df = export_salesforce_data(query)

# Display the DataFrame
df


# In[124]:


df[df['User__c']=='0058W00000EKrpxQAD']


# In[125]:


user=df[['Id','User__c','Name','Primary__c','Primary__r.Name','Staff_Activated__c','Primary__r.POD__r.Name','Role_Title__r.Name']].copy()

# Rename the columns
user.rename(columns={
    'User__c': 'Staff_UserID',
    'Id':'Staff_StaffId',
    'Name': 'Staff_UserName',
    'Staff_Activated__c':'Staff_ActiveStatus',
    'Primary__c':'Staff_OfficeID',
    'Primary__r.Name': 'Staff_Office',
    'Primary__r.POD__r.Name': 'Staff_PODName',
    'Role_Title__r.Name': 'Staff_Title'
}, inplace=True)
user
# user[user['Staff_UserID']=='0058W00000EKrpxQAD']


# In[126]:


# # Creating a new row as a DataFrame
# new_row = pd.DataFrame([['NA', 'NA', 'NA', 'NA', 'NA', True, 'NA', 'Vendor Performance Manager']], columns=user.columns)

# # Concatenating the new row with the existing DataFrame
# user = pd.concat([user, new_row], ignore_index=True)


# user


# In[127]:


# user[user['Staff_UserID']=='0058W00000EKrpxQAD']


# # ### Calendar


# #### Calendar

# In[128]:


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
        Fiscal_Year__c       
        
FROM
        Edward_Mellor_Calendar__c
"""
# export_file = 'test.csv'

# Get the DataFrame
df = export_salesforce_data(query)
df['Year-Q-P-W'] = df['Name'].apply(lambda x: re.search(r'\[.*?\]', x).group(0) if re.search(r'\[.*?\]', x) else None)
# df
Calendar=df[['Year-Q-P-W','Date__c','Fiscal_Week__c','Days_of_Week__c','Fiscal_Period__c','Week_in_Period__c','Fiscal_Quarter__c','Fiscal_Reward_Week__c','Fiscal_Year__c']]
Calendar['Year-Q-P']=Calendar['Fiscal_Year__c']+'-'+Calendar['Fiscal_Quarter__c']+'-'+Calendar['Fiscal_Period__c']
# Rename the columns
Calendar.rename(columns={
    'Date__c': 'Calendar_Date',
    'Fiscal_Week__c': 'Calendar_FiscalWeek',
    'Days_of_Week__c': 'Calendar_DaysOfWeek',
    'Fiscal_Period__c': 'Calendar_FiscalPeriod',
    'Week_in_Period__c': 'Calendar_WeekInPeriod',
    'Fiscal_Quarter__c': 'Calendar_FiscalQuarter',
    'Fiscal_Reward_Week__c':'Calendar_FiscalRewardWeek',
    'Fiscal_Year__c':'Calendar_FiscalYear'
    
}, inplace=True)


Calendar = convert_to_datetime_or_date(Calendar, ['Calendar_Date'], format_type='date')

# Display the DataFrame
Calendar

from datetime import datetime

# Ensure 'Calendar_Date' is a datetime column and extract only the date part
Calendar['Calendar_Date'] = Calendar['Calendar_Date'].dt.date

# Filter based on the current date
Calendar = Calendar[Calendar['Calendar_Date'] < datetime.now().date()]
Calendar



# #### Master

# In[129]:


user['key']=1
Calendar['key']=1
Reward_Master= pd.merge(user, Calendar, on='key').drop('key', axis=1)
Reward_Master


# In[130]:


Reward_Master = convert_to_datetime_or_date(Reward_Master, ['Calendar_Date'], format_type='date').copy()
Reward_Master.dtypes


# #### Office by PostCode

# In[131]:


# Example usage
query = """
SELECT 
    id,
    Name,
    Market_Area__r.Office__c,
    Market_Area__r.Office__r.Name,
    Market_Area__c,
    Market_Area__r.Name
FROM
    Edward_Mellor_Postcode_Bible__c
WHERE
    Market_Area__c != ''
        AND Market_Area__r.Office__c != ''
"""

df = export_salesforce_data(query)

# Display the DataFrame
df


# In[132]:


PostcodeOffice = df[['Name', 'Market_Area__r.Office__c']].copy()
PostcodeOffice.rename(columns={
    'Name':'Postcode',
    'Market_Area__r.Office__c': 'PostcodeOfficeId'
}, inplace=True)
PostcodeOffice

# Capitalize all letters in the 'Postcode' column
PostcodeOffice['Postcode'] = PostcodeOffice['Postcode'].str.upper()
PostcodeOffice


# In[133]:


check_duplicates(PostcodeOffice, ['Postcode','PostcodeOfficeId'])


# ### Listing


# #### Listing

# ##### Getting the data for listing

# In[134]:


# Example usage
query = """
SELECT 
    Id,
    OwnerId,
    RecordTypeId,
    RecordType.Name,
    Name,
    Postcode__c ,
    Office__c,
    Office__r.name,
    pba__ListingPrice_pb__c,
    pba__Status__c,
    Lister_Name__c,
    pba__ListedDate_pb__c,
    Valuation_Date__c,
    Withdrawn_Date__c,
    Calculated_Fee__c,
    Valuation_Cancelled__c,
    
    EA_Lister__c,
    EA_Lister__r.name,
    EA_Lister_Profile__c,
    Estate_Agency_Referral__c,
    Estate_Agency_Referral__r.name ,
    Property_Auto_Reference__c

    
FROM
    pba__Listing__c
where 
    pba__ListedDate_pb__c>2024-06-27 or Withdrawn_Date__c >2024-06-27 or Valuation_Date__c>2024-06-27 or Valuation_Cancelled__c>2024-06-27
"""

df = export_salesforce_data(query)

# Display the DataFrame
df


# In[135]:


Listing=df[['Id', 'OwnerId', 'Name','Postcode__c','RecordType.Name','Office__c','Office__r.Name', 'pba__ListingPrice_pb__c'\
            ,'EA_Lister__c','EA_Lister__r.Name','EA_Lister_Profile__c'\
            ,'Estate_Agency_Referral__c','Estate_Agency_Referral__r.Name'
            ,'Lister_Name__c','pba__Status__c','pba__ListedDate_pb__c', 'Valuation_Date__c','Withdrawn_Date__c',\
            'Calculated_Fee__c', 'Valuation_Cancelled__c','property_auto_reference__c'
           ]].copy()

# Rename the columns
# Correct the column renaming dictionary
Listing.rename(columns={
    'Name': 'Listing_Address',
    'Postcode__c':'Listing_Property_Postcode',
    'RecordType.Name': 'Listing_RecordType',
    'Office__c':'Listing_Office_Code',
    'Office__r.Name': 'Listing_Office',
    'EA_Lister__c': 'EA_Lister_Id',
    'EA_Lister__r.Name': 'EA_Lister',
    'Estate_Agency_Referral__c': 'Referral_Id',
    'Estate_Agency_Referral__r.Name': 'Referral_Name', 
    'pba__ListingPrice_pb__c': 'Listing_Price',
    'pba__Status__c': 'Listing_Status',
    'Lister_Name__c': 'Listing_ListerId',
    'pba__ListedDate_pb__c': 'Listing_ListingDate',
    'Valuation_Date__c': 'Listing_ValuationDate',
    'Withdrawn_Date__c': 'Listing_WithdrawnDate',
    'Calculated_Fee__c': 'Listing_Fee',
    'Valuation_Cancelled__c': 'Listing_ValuationCancellationDate',
    'property_auto_reference__c':'Property_Auto_Reference'
    
}, inplace=True)



Listing = convert_to_datetime_or_date(Listing, ['Listing_ListingDate'], format_type='date').copy()
Listing = convert_to_datetime_or_date(Listing, ['Listing_ValuationDate'], format_type='date').copy()
Listing = convert_to_datetime_or_date(Listing, ['Listing_WithdrawnDate'], format_type='date').copy()
Listing = convert_to_datetime_or_date(Listing, ['Listing_ValuationCancellationDate'], format_type='date').copy()
# print( Listing.dtypes)
Listing


# In[136]:


# # Get the office id from   postcode bible
# Listing=pd.merge(Listing,PostcodeOffice,left_on='Listing_Property_Postcode',right_on='Postcode',how='left')
# # Listing['PostcodeOfficeId'] = Listing['PostcodeOfficeId'].apply(lambda x: Listing['Listing_Property_Postcode'] if pd.isnull(x) else x)

# Listing


# In[137]:


conditions = [ Listing['EA_Lister_Id'].notnull(),    Listing['Referral_Id'].notnull()]

# Define the corresponding values for each condition
choices = [    Listing['EA_Lister_Id'],    Listing['Referral_Id']]

# Use np.select to apply the conditions and choices
Listing['Reward_Lister'] = np.select(conditions, choices, default=Listing['Listing_ListerId'])

Listing


# #### Marking Listing Files


# In[138]:


Listing['ListingFlag'] = np.where(
    ((Listing['Listing_RecordType'] == 'Sale') & 
     (Listing['Listing_Status'].isin(['Available', 'For Sale', 'Low Profile', 'Notice Given', 'On Hold', 'Referred (WD)', 'SSTC']))) |
    ((Listing['Listing_RecordType'] == 'Auction') & 
     # (BasicListing['EA_Lister'] != ''))
    (Listing['EA_Lister'].notna())),  # Use .notna() to check for non-null values,
    1,  # Set to 1 if conditions are met
    0   # Set to 0 otherwise
)
# Listing.loc[:,'Listing_Auction_Instruction'] = np.where(Listing['EA_Lister'].notna(), 1, 0)
# Listing.loc[:, 'Listing_Auction_Referral'] = np.where(Listing['Referral_Name'].notna(), 1, 0)

# Auction Instruction Flag
# Ensure EA_Lister_Id is not null or empty and Listing_RecordType is "Auction"
Listing.loc[:, 'Listing_Auction_Instruction'] = np.where(
    Listing['EA_Lister'].notna() & (Listing['EA_Lister'].str.strip() != "") & (Listing['Listing_RecordType'] == "Auction"), 
    1, 
    0
)

# Auction Referral Flag
# Ensure Referral_Id is not null or empty
Listing.loc[:, 'Listing_Auction_Referral'] = np.where(
    Listing['Referral_Id'].notna() & (Listing['Referral_Id'].str.strip() != "")  & (Listing['Listing_RecordType'] == "Auction"), 
    1, 
    0
)



Listing


# In[139]:


Listing=pd.merge(Listing,user[['Staff_UserID','Staff_OfficeID']],left_on='Reward_Lister',right_on='Staff_UserID',how='left')
Listing


# In[140]:


Listing['Mod_ListingOffice'] = np.where(Listing['Listing_RecordType'] == 'Auction', Listing[ 'Staff_OfficeID'],   Listing[ 'Listing_Office_Code']  )
Listing


# #### VPM Calculation

# In[141]:


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


# In[142]:


VPM = df[['Primary__c', 'User__c','Name']].copy()
VPM.rename(columns={
    'Primary__c':'OfficeId',
    'User__c': 'VPMId',
    'Name':'VPM_Name'
}, inplace=True)
VPM


# In[143]:


Listing=pd.merge(Listing,VPM,left_on='Mod_ListingOffice',right_on='OfficeId', how='left')
Listing


# #### Closing

# In[144]:


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
    CreatedById,
    CreatedDate,
    Completion_date__c,
    Sale_Fallen_Through__c,
    Closing_Status__c,
    Sale_Price__c,
    Percentage_Selling_Fee__c,
    Calculated_Fee__c,
    FLAG_6_Week_sale__c,
    pba__Listing__r.EA_Lister__c,
    pba__Listing__r.EA_Lister__r.Name,
    pba__Listing__r.Estate_Agency_Referral__c,
    pba__Listing__r.Estate_Agency_Referral__r.Name,
    Buying_Advisor__c,
    Property_Auto_Reference__c
FROM
    pba__Closing__c  
WHERE 
            (CreatedDate > 2024-06-27T00:00:00Z or Sale_Fallen_Through__c>2024-06-27 or Completion_date__c>2024-06-27 or   Fee_Received_Date__c>2024-06-27) and RecordType.Name!='DELETED' 
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
        "CreatedById",
        "CreatedDate",
        "Completion_date__c",
        "Sale_Fallen_Through__c",
        "Closing_Status__c",
        "Sale_Price__c",
        "Percentage_Selling_Fee__c",
        "Calculated_Fee__c",
        "FLAG_6_Week_sale__c",
        "pba__Listing__r.EA_Lister__c",
        "pba__Listing__r.EA_Lister__r.Name",
        "pba__Listing__r.Estate_Agency_Referral__c",
        "pba__Listing__r.Estate_Agency_Referral__r.Name" ,
        "Property_Auto_Reference__c",
        "Buying_Advisor__c"
  
    ]
].copy()


Closing.rename(
    columns={
        "Id": "Closing_Id",
        "OwnerId": "Closing_OwnerId",
        "pba__Listing__r.OwnerId":"Listing_OwnerID", 
        "Name": "Closing_ClosingId",
        "pba__Listing__r.Name":"Listing_Address",
        'pba__Listing__r.Postcode__c':"Listing_Postcode",
        "pba__Listing__r.Lister_Name__c":"Lister_Id",
        "pba__Offer__r.OwnerId":"Offer_Id",
        "RecordTypeId":"Closing_RecordTypeId",
        "RecordType.Name":"Closing_RecordName",
        "pba__Listing__r.Office__c":"Listing_Office_ID",
        "pba__Listing__r.Office__r.Name":"Listing_Office",
        "CreatedById":"Closing_Created_Id",
        "CreatedDate":"Closing_Date",
        "Completion_date__c":"Closing_Completion_Date",
        "Sale_Fallen_Through__c":"Sale_Fallen_Through_Date",
        "Closing_Status__c":"Closing_Status",
        "Sale_Price__c":"Sale_Price",
        "Percentage_Selling_Fee__c":"Percentage_Selling_Fee",
        "Calculated_Fee__c":"Calculated_Fee",
        "FLAG_6_Week_sale__c":"FLAG_6_Week_sale",
        
        "pba__Listing__r.EA_Lister__c":"EA_Lister_ID",
        "pba__Listing__r.EA_Lister__r.Name":"EA_Lister_Name",
        "pba__Listing__r.Estate_Agency_Referral__c":"Referral_ID",
        "pba__Listing__r.Estate_Agency_Referral__r.Name":"Referral_Name",
        "Property_Auto_Reference__c":"Property_Auto_Reference",
        "Buying_Advisor__c":"Buying_AdvisorID"
    },
    inplace=True,
)



Closing = convert_to_datetime_or_date(Closing, ["Closing_Date"], format_type="date")
Closing = convert_to_datetime_or_date(Closing, ["Closing_Completion_Date"], format_type="date")
Closing = convert_to_datetime_or_date(Closing, ["Sale_Fallen_Through_Date"], format_type="date")


# Display the DataFrame
Closing


# In[145]:


Closing['SalesFlag'] = np.where((Closing['Closing_RecordName'] == "Sale") & (Closing['Listing_Office'] != "Auction"),1, 0)
Closing['AuctionFlag'] = np.where((Closing['Closing_RecordName'] == "Auction") ,1, 0)

Closing.loc[:, 'Closing_Auction_Instruction'] = np.where(    (Closing['EA_Lister_Name'].notna()) & 
    (Closing['EA_Lister_Name'].str.strip() != "") & 
    (Closing['Closing_RecordName'] == "Auction"), 1, 0)


# Closing.loc[:, 'Closing_Auction_Instruction'] = np.where(Closing['EA_Lister_Name'].notna() & Closing['Closing_RecordName']=="Auction", 1, 0)
Closing.loc[:, 'Closing_Auction_Referral'] = np.where(Closing['Referral_Name'].notna(), 1, 0)


# Closing.loc[:, 'FLAG_6_Week_sale'] = np.where((Closing['FLAG_6_Week_sale'] == 1) & (Closing['SalesFlag'] == 0), 0, 1)
Closing.loc[:, 'FLAG_6_Week_sale'] = np.where(
    (Closing['FLAG_6_Week_sale'] == 1) & (Closing['SalesFlag'] == 0), 
    0, 
    Closing['FLAG_6_Week_sale']
)

# Closing.loc[:, 'NewOfficeID'] = np.where((Closing['Closing_Auction_Referral'] == 1) & (Closing['SalesFlag'] == 1), , 0)

# (Closing['Closing_Auction_Referral'] == 1)

# Listing_Office_ID


Closing


# In[146]:


conditions = [ Closing['EA_Lister_ID'].notnull(),    Closing['Referral_ID'].notnull()]

# Define the corresponding values for each condition
choices = [    Closing['EA_Lister_ID'],    Closing['Referral_ID']]

# Use np.select to apply the conditions and choices
Closing['Reward_Lister'] = np.select(conditions, choices, default=Closing['Lister_Id'])

Closing


# In[147]:


Closing=pd.merge(Closing,user[['Staff_UserID','Staff_OfficeID']],left_on='Reward_Lister',right_on='Staff_UserID',how='left')
Closing


# In[148]:


Closing['Mod_ListingOffice'] = np.where(Closing['Closing_RecordName'] == 'Auction', Closing[ 'Staff_OfficeID'],   Closing[ 'Listing_Office_ID']  )
Closing


# In[149]:


Closing=pd.merge(Closing,VPM,left_on='Mod_ListingOffice',right_on='OfficeId', how='left')
Closing


# #### FS_Signup

# In[150]:


query = """
SELECT 
    Id,
    RecordTypeId,
    Record_Type_Name__c,
    CreatedDate,
    Date_of_Sign_Up__c,
    Appointment_MakerLOOKUP__c,
    Appointment_MakerLOOKUP__r.Name,
    Appointment_MakerLOOKUP__r.Title,
    Listing__r.Name,
    Closing__c,
    Closing__r.Name,
    Closing__r.Office__c,
    Listing__r.Office__c,
    Listing__r.Office__r.Name,
    Closing__r.Vendor_Manager__c
FROM
    Opportunity
WHERE
    Record_Type_Name__c = 'Mortgage'
        AND Date_of_Sign_Up__c != NULL
        AND Appointment_MakerLOOKUP__c != NULL
        AND Date_of_Sign_Up__c > 2024-06-27
        AND Closing__c != NULL
"""
# # # export_file = 'test.csv'

# Get the DataFrame
df = export_salesforce_data(query)


# df
Opportunity = df[
    [
    "Id",
    "RecordTypeId",
    "Record_Type_Name__c",
    "CreatedDate",
    "Date_of_Sign_Up__c",
    "Appointment_MakerLOOKUP__c",
    "Appointment_MakerLOOKUP__r.Name",
    "Appointment_MakerLOOKUP__r.Title",
    "Listing__r.Name",
    "Closing__c",
    "Closing__r.Name",
    "Closing__r.Office__c",
    "Listing__r.Office__c",
    "Listing__r.Office__r.Name",
      "Closing__r.Vendor_Manager__c"  
  
    ]
].copy()

# Opportunity
Opportunity.rename(
    columns={
    "Id":"Opportunity_ID",
     "Date_of_Sign_Up__c":"Opportunity_SignupDate",
    "Appointment_MakerLOOKUP__c":"Opportunity_AppointmentmakerID",
    "Appointment_MakerLOOKUP__r.Name":"Opportunity_AppointmentmakerName",
    "Appointment_MakerLOOKUP__r.Title":"Opportunity_AppointmentmakerTitle",
    "Listing__r.Name":"Opportunity_ListingAddress",
    "Closing__c":"Opportunity_ClosingID",
    "Closing__r.Name":"Opportunity_ClosingIDName",
    "Closing__r.Office__c":"Opportunity_ClosingOffice",
    "Listing__r.Office__c":"Opportunity_ListingOfficeID",
    "Listing__r.Office__r.Name":"Opportunity_ListingOfficeName",
    "Closing__r.Vendor_Manager__c":"VPMId"
    },
    inplace=True,
)



Opportunity = convert_to_datetime_or_date(Opportunity, ["CreatedDate"], format_type="date")
Opportunity = convert_to_datetime_or_date(Opportunity, ["Opportunity_SignupDate"], format_type="date")


Opportunity = Opportunity[~Opportunity['Opportunity_AppointmentmakerTitle'].str.contains('Vendor Performance Manager|Assistant Vendor Performance Manager', na=False)].reset_index(drop=True)
Opportunity = Opportunity[~Opportunity['Opportunity_ClosingOffice'].str.contains('Auction', na=False)].reset_index(drop=True)
# .reset_index(True)

# # Display the filtered dataframe
# Opportunity=filtered_df.copy()

Opportunity


# ## Export to MY SQL


# ### Load data in sql

# In[151]:


if __name__ == "__main__":
#     # Load DataFrame into MySQL
    load_dataframe_to_mysql(Listing, 'Reward_Listing')
    load_dataframe_to_mysql(Reward_Master, 'Reward_Master')
    load_dataframe_to_mysql(Closing, 'Reward_Closing')
    load_dataframe_to_mysql(VPM, 'Reward_VPM')
    load_dataframe_to_mysql(Opportunity, 'Reward_Opportunity')    
    load_dataframe_to_mysql(user, 'Reward_Staff')    
#     load_dataframe_to_mysql(PostcodeOffice, 'PostcodeOffice')   


# ## Create a local file for that date


# In[152]:


import datetime
import os

# Get the current date and time
current_datetime = datetime.datetime.now()

# Format the date and time as a string
datetime_string = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

# Create a filename with the date and time
filename = f"note_{datetime_string}.txt"

# Create and open the file
with open(filename, "w") as file:
    # Write the current date and time to the file
    file.write(f"File created on: {current_datetime}\n\n")
    file.write("Your notes here:\n")

# Print confirmation message
print(f"Notepad file '{filename}' has been created.")

# # Optionally, open the file (works on Windows)
# os.system(f"notepad.exe {filename}")

