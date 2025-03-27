#made some changes to how trhe data is stored in the csv file. using this to transform the data to the new format in all existing csv files
#Change
import pandas as pd
import os

def transform_csv(file_path):
    df = pd.read_csv(file_path)
    
    if 'Address' in df.columns:
        df[['Last Updated Day', 'Last Updated Date', 'Last Updated Time']] = df['Last Updated'].str.extract(r'(\w+),\s+(\d{4}-\d{1,2}-\d{1,2})\s+(\d{1,2}:\d{2}:\d{2}\s+[AP]M)')
        
        df['Last Updated Month'] = 'March'  
        
        
        df = df.drop('Address', axis=1)
        
      
        df = df[['Timestamp', 'Garage Name', 'Occupancy', 'Last Updated Day', 'Last Updated Month', 'Last Updated Date', 'Last Updated Time']]
        
       
        df.to_csv(file_path, index=False)
        print(f"Transformed {file_path}")
    else:
        print(f"File {file_path} is already donee")


csv_files = ['west_garage.csv', 'south_garage.csv', 'north_garage.csv', 'south_campus_garage.csv']


for csv_file in csv_files:
    if os.path.exists(csv_file):
        print(f"working on  {csv_file}...")
        transform_csv(csv_file)
        print(f"yayy! done with {csv_file}") 