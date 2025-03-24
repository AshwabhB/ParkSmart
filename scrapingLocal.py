import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import urllib3
import re
import csv
import os
import time


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def save_to_csv(garage_data, garage_name):
    filename = f"{garage_name.replace(' ', '_').lower()}.csv"
    file_exists = os.path.isfile(filename)
    
    with open(filename, 'a', newline='') as csvfile:
        fieldnames = ['Timestamp', 'Garage Name', 'Address', 'Occupancy', 'Last Updated']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        writer.writerow(garage_data)
    
    return filename

def get_parking_status():
    url = "https://sjsuparkingstatus.sjsu.edu/"
    
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()  
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        content = soup.get_text()
        
        pattern = r"((?:South|West|North|South Campus) Garage) (.*?), San Jose, CA \d{5} (\d+) %"
        matches = re.finditer(pattern, content)
        
        print("\nSJSU Parking Garage Status:")
        print("=" * 70)
        
        current_time = datetime.now()
        timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
        day_of_week = current_time.strftime("%A")
        print(day_of_week)
        
        last_updated_match = re.search(r"Last updated (.*?)\s*Refresh", content)
        if last_updated_match:
            date_str = last_updated_match.group(1)
            last_updated = f"{day_of_week}, {date_str}"
        else:
            last_updated = "Unknown"
        
        saved_files = []
        
        for match in matches:
            name = match.group(1)
            address = match.group(2) + ", San Jose, CA 95112"
            percentage = match.group(3)  
            
            garage_data = {
                'Timestamp': timestamp,
                'Garage Name': name,
                'Address': address,
                'Occupancy': percentage,
                'Last Updated': last_updated
            }
            
            filename = save_to_csv(garage_data, name)
            saved_files.append(filename)
            
            print(f"Garage: {name}")
            print(f"Address: {address}")
            print(f"Occupancy: {percentage}%")
            print("-" * 70)
        
        print(f"\nLast Updated: {last_updated}")
        print("\nData has been saved to:")
        for file in saved_files:
            print(f"- {file}")
        
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

if __name__ == "__main__":
    print("Starting SJSU Parking Garage monitoring (runs every 15 minutes)...")
    print("Press Ctrl+C to stop the program")
    
    while True:
        try:
            get_parking_status()
            print("\nWaiting 15 minutes until next update...")
            time.sleep(900)
        except KeyboardInterrupt:
            print("\nProgram stopped by user")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            print("Retrying in 15 minutes...")
            time.sleep(900)