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
        fieldnames = ['Timestamp', 'Garage Name', 'Occupancy', 'Last Updated Day', 'Last Updated Month', 'Last Updated Date', 'Last Updated Time']
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
        
        pattern = r"((?:South|West|North|South Campus) Garage) (.*?), San Jose, CA \d{5} (?:(\d+) %|full)"
        matches = re.finditer(pattern, content, re.IGNORECASE)
        
        print("\nSJSU Parking Garage Status:")
        print("=" * 70)
        
        current_time = datetime.now()
        timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
        day_of_week = current_time.strftime("%A")
        month_name = current_time.strftime("%B")
        print(f"{day_of_week}, {month_name}")
        
        last_updated_match = re.search(r"Last updated (.*?)\s*Refresh", content, re.IGNORECASE)
        last_updated_day = day_of_week
        last_updated_full = last_updated_match.group(1) if last_updated_match else "Unknown"
        
        try:
            if last_updated_full != "Unknown":
                last_updated_parts = last_updated_full.strip().split()
                
                if len(last_updated_parts) >= 2 and (last_updated_parts[-1] in ['AM', 'PM']):
                    time_part = last_updated_parts[-2] + ' ' + last_updated_parts[-1]  
                    date_part = ' '.join(last_updated_parts[:-2])  
                else:
                    date_part = last_updated_full
                    time_part = "Unknown"
                
                last_updated_date = date_part
                last_updated_time = time_part
                
                try:
                    parsed_date = datetime.strptime(date_part, "%B %d, %Y")
                    last_updated_month = parsed_date.strftime("%B")
                except ValueError:
                    last_updated_month = month_name  
            else:
                last_updated_date = "Unknown"
                last_updated_time = "Unknown"
                last_updated_month = "Unknown"
        except Exception as e:
            print(f"Error parsing last updated timestamp: {e}")
            last_updated_date = "Unknown"
            last_updated_time = "Unknown"
            last_updated_month = "Unknown"
        
        saved_files = []
        
        for match in matches:
            name = match.group(1)
            
            percentage = "100" if match.group(3) is None else match.group(3)
            
            garage_data = {
                'Timestamp': timestamp,
                'Garage Name': name,
                'Occupancy': percentage,
                'Last Updated Day': last_updated_day,
                'Last Updated Month': last_updated_month,
                'Last Updated Date': last_updated_date,
                'Last Updated Time': last_updated_time
            }
            
            filename = save_to_csv(garage_data, name)
            saved_files.append(filename)
            
            print(f"Garage: {name}")
            print(f"Occupancy: {percentage}%")
            print("-" * 70)
        
        print(f"\nLast Updated: {last_updated_day}, {last_updated_month} - {last_updated_date} at {last_updated_time}")
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