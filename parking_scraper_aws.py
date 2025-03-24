import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import urllib3
import re
import csv
import os
import boto3
from io import StringIO
from datetime import timezone
from zoneinfo import ZoneInfo


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def save_to_s3(garage_data, garage_name, s3_bucket):
    """
    Save garage data to CSV files in S3
    """
    s3 = boto3.client('s3')
    filename = f"{garage_name.replace(' ', '_').lower()}.csv"
    
    try:
        try:
            response = s3.get_object(Bucket=s3_bucket, Key=filename)
            existing_content = response['Body'].read().decode('utf-8')
            output = StringIO()
            output.write(existing_content)
        except s3.exceptions.NoSuchKey:
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=garage_data.keys())
            writer.writeheader()
        
        writer = csv.DictWriter(output, fieldnames=garage_data.keys())
        writer.writerow(garage_data)
        
        s3.put_object(
            Bucket=s3_bucket,
            Key=filename,
            Body=output.getvalue().encode('utf-8'),
            ContentType='text/csv'
        )
        
        return filename
    except Exception as e:
        print(f"Error saving to S3: {e}")
        return None

def get_parking_status(s3_bucket):
    url = "https://sjsuparkingstatus.sjsu.edu/"
    saved_files = []
    
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.get_text()
        
        pattern = r"((?:South|West|North|South Campus) Garage) (.*?), San Jose, CA \d{5} (\d+) %"
        matches = re.finditer(pattern, content)
        
        current_time = datetime.now(ZoneInfo("America/Los_Angeles"))
        timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
        day_of_week = current_time.strftime("%A")
        
        print(f"Current time in Pacific Time: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')} - Day: {day_of_week}")
        
        last_updated_match = re.search(r"Last updated (.*?)\s*Refresh", content)
        last_updated = f"{day_of_week}, {last_updated_match.group(1)}" if last_updated_match else "Unknown"
        
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
            
            filename = save_to_s3(garage_data, name, s3_bucket)
            if filename:
                saved_files.append(filename)
        print("Data collection successful") 
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Data collection successful',
                'files_updated': saved_files
            })
        }
        
    except requests.RequestException as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f"Error fetching data: {str(e)}"
            })
        }

def lambda_handler(event, context):
    """
    AWS Lambda handler function
    """
    print("Starting parking data collection...") 
    S3_BUCKET = 'sjsu-parking-data'
    
    return get_parking_status(S3_BUCKET)