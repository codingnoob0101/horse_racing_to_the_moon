import pandas as pd
import xml.etree.ElementTree as ET
import os
import re
from datetime import datetime
import glob

def extract_temperature_from_xml(xml_file_path, location_name):
    """
    Extract temperature for a specific location from XML file.
    """
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        
        # Find the description element containing CDATA
        for item in root.findall(".//item"):
            description = item.find("description")
            if description is not None and description.text:
                cdata_content = description.text
                
                # Look for the temperature table and extract the specific location temperature
                pattern = rf'<tr><td><font size="-1">{location_name}</font></td><td width="100" align="right"><font size="-1">(\d+) degrees'
                match = re.search(pattern, cdata_content)
                if match:
                    return int(match.group(1))
                    
        return None
    except Exception as e:
        print(f"Error processing XML file {xml_file_path}: {e}")
        return None

def find_xml_file(date_str, venue, hourly_temp_dir):
    """
    Find appropriate XML file based on date and venue.
    ST (Sha Tin) -> afternoon time (14:00-15:00)
    HV (Happy Valley) -> night time (19:00-20:00)
    """
    try:
        # Parse the date
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        year = date_obj.strftime('%Y')
        month = date_obj.strftime('%m')
        day = date_obj.strftime('%d')
        
        # Construct the directory path
        xml_dir = os.path.join(hourly_temp_dir, year, month, day)
        
        if not os.path.exists(xml_dir):
            return None
            
        # Define time patterns based on venue
        if venue == 'ST':  # Sha Tin - afternoon (14:00-15:00)
            time_patterns = ['14*', '15*']
        elif venue == 'HV':  # Happy Valley - night (19:00-20:00)
            time_patterns = ['19*', '20*']
        else:
            return None
        
        # Look for XML files with appropriate time patterns
        date_prefix = date_obj.strftime('%Y%m%d')
        
        for time_pattern in time_patterns:
            pattern = f"{date_prefix}-{time_pattern}-*.xml"
            xml_files = glob.glob(os.path.join(xml_dir, pattern))
            if xml_files:
                return xml_files[0]  # Return the first matching file
                
        return None
        
    except Exception as e:
        print(f"Error finding XML file for {date_str}, {venue}: {e}")
        return None

def get_temperature_for_venue(date_str, venue, hourly_temp_dir):
    """
    Get temperature for a specific venue and date.
    """
    xml_file = find_xml_file(date_str, venue, hourly_temp_dir)
    if xml_file is None:
        return None
        
    # Map venue codes to location names in XML
    venue_mapping = {
        'ST': 'Sha Tin',
        'HV': 'Happy Valley'
    }
    
    location_name = venue_mapping.get(venue)
    if location_name is None:
        return None
        
    return extract_temperature_from_xml(xml_file, location_name)

def process_combined_performance_data():
    """
    Main function to process the combined_performance_data.csv file.
    """
    # Read the CSV file
    print("Reading combined_performance_data.csv...")
    df = pd.read_csv('combined_performance_data.csv')
    
    print(f"Original data shape: {df.shape}")
    print(f"Original columns: {df.columns.tolist()}")
    
    # Remove scrape_time, race_class, and weather columns
    columns_to_remove = ['scrape_time', 'race_class', 'weather']
    df = df.drop(columns=[col for col in columns_to_remove if col in df.columns])
    
    print(f"After removing columns: {df.shape}")
    print(f"Remaining columns: {df.columns.tolist()}")
    
    # Add temperature column
    df['temperature'] = None
    
    # Process each row to get temperature
    hourly_temp_dir = 'hourly_temperature'
    
    print("Processing temperature data...")
    for index, row in df.iterrows():
        if index % 100 == 0:
            print(f"Processing row {index}/{len(df)}")
            
        date_str = row['date']
        venue = row['venue']
        
        temperature = get_temperature_for_venue(date_str, venue, hourly_temp_dir)
        df.at[index, 'temperature'] = temperature
    
    # Sort by date from earliest to latest
    print("Sorting data by date...")
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')  # Convert back to string format
    
    # Save the processed data
    output_file = 'combined_weather.csv'
    df.to_csv(output_file, index=False)
    
    print(f"Processing complete! Output saved to {output_file}")
    print(f"Final data shape: {df.shape}")
    
    # Show some statistics
    temp_stats = df['temperature'].describe()
    print("\nTemperature statistics:")
    print(temp_stats)
    
    # Show missing temperature data
    missing_temp = df['temperature'].isna().sum()
    print(f"\nRows with missing temperature data: {missing_temp}")
    
    return df

if __name__ == "__main__":
    result_df = process_combined_performance_data() 