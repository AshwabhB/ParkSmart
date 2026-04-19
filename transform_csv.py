import pandas as pd
import os

EXPECTED_COLUMNS = [
    'Timestamp', 'Garage Name', 'Occupancy',
    'Last Updated Day', 'Last Updated Month', 'Last Updated Date', 'Last Updated Time'
]

def transform_csv(file_path):
    df = pd.read_csv(file_path)

    if 'Address' not in df.columns:
        print(f"{file_path}: already in current schema, skipping.")
        return

    df[['Last Updated Day', 'Last Updated Date', 'Last Updated Time']] = (
        df['Last Updated'].str.extract(
            r'(\w+),\s+(\d{4}-\d{1,2}-\d{1,2})\s+(\d{1,2}:\d{2}:\d{2}\s+[AP]M)'
        )
    )
    df['Last Updated Month'] = pd.to_datetime(
        df['Last Updated Date'], errors='coerce'
    ).dt.strftime('%B')

    df = df.drop(columns=['Address'])
    df = df[EXPECTED_COLUMNS]
    df.to_csv(file_path, index=False)
    print(f"Transformed: {file_path}")


if __name__ == '__main__':
    csv_files = ['west_garage.csv', 'south_garage.csv', 'north_garage.csv', 'south_campus_garage.csv']
    for csv_file in csv_files:
        if os.path.exists(csv_file):
            transform_csv(csv_file)
        else:
            print(f"Not found, skipping: {csv_file}") 