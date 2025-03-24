# SJSU Smart Parking Predictor 

*Note: This project is not officially affiliated with San Jose State University and the purpose of it is to help me find a good parking spot.* 


## Project Overview
This project aims to develop a web-based application that helps SJSU students and faculty make informed decisions about parking by predicting garage availability. The system will provide real-time parking status and predictive insights for all four SJSU parking garages.

## Current Progress 
- Successfully implemented a Python-based web scraper that:
  - Collects real-time parking occupancy data from SJSU's official parking status website
  - Runs automatically every 15 minutes as an AWS Lambda function
  - Stores historical data in CSV format on AWS S3
  - Tracks data for all four SJSU parking garages (South, West, North, and South Campus)
  - Records timestamps, garage names, addresses, and occupancy percentages

## Tech Stack (Current) 
- **Backend**: Python
- **Cloud Services**: 
  - AWS Lambda for automated scraping
  - AWS S3 for data storage
- **Libraries**:
  - BeautifulSoup4 for web scraping
  - Boto3 for AWS integration
  - Requests for HTTP requests
  - Additional utilities: urllib3, zoneinfo

## Future Development Plans 
1. **Data Collection Phase**
   - Continue gathering parking data to build a comprehensive dataset
   - Analyze patterns in parking behavior across different times and days

2. **Machine Learning Implementation**
   - Develop and train ML models using collected historical data
   - Create predictive algorithms for parking availability

3. **Web Application Development**
   - Build user-friendly interface for:
     - Real-time parking status
     - Predictive availability based on user's planned arrival time
     - Alternative parking recommendations
   - Implement user input features for preferred garage and arrival time

## Project Goals 
- Provide accurate predictions of parking availability
- Help users make informed decisions about parking choices
- Reduce time spent searching for parking
- Improve overall parking experience at SJSU

## Project Status: In Development 
This project is actively under development, currently in the data collection phase. Regular updates will be made as new features are implemented.

## Contributors
- Ashwabh Bhatnagar



