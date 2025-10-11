# HKJC Horse Racing Data Scraper with Weather Integration

This project scrapes horse racing data from the Hong Kong Jockey Club (HKJC) website and integrates it with weather data from the Hong Kong Observatory (HKO) to create a comprehensive dataset for analysis.

## 🏇 Project Overview

The system consists of three main components:
1. **HKJC Racing Data Scraper** - Scrapes horse performance and race results
2. **Weather Data Integration** - Downloads and processes HKO weather data  
3. **Data Processing Pipeline** - Combines racing and weather data into analysis-ready format

## 📋 Prerequisites

### Software Requirements
- Python 3.7+
- Google Chrome browser
- Jupyter Notebook/Lab
- Internet connection

### Python Packages
The scraper will automatically install required packages:
```bash
pip install selenium requests pandas beautifulsoup4 webdriver-manager python-dateutil
```

## 🚀 Step-by-Step Workflow

### Step 1: Scrape HKJC Racing Data

1. **Open the Jupyter Notebook**
   ```bash
   jupyter notebook hkjc_scraper.ipynb
   ```

2. **Configure Scraping Parameters**
   
   In the notebook, modify the `Config` class settings:
   ```python
   class Config:
       START_DATE = "2023-01-01"  # Your desired start date
       END_DATE = "2025-07-14"    # Your desired end date
       RATE_LIMIT = 2             # Seconds between requests
       HEADLESS = True            # Set to False to see browser
   ```

3. **Run All Cells**
   
   Execute all cells in the notebook sequentially. The scraper will:
   - Set up Chrome WebDriver automatically
   - Scrape race results from both Sha Tin (ST) and Happy Valley (HV) venues
   - Extract horse performance data including:
     - Horse names, IDs, and numbers
     - Jockeys and trainers
     - Race positions, times, and odds
     - Race dates and venues
   - Export data to CSV files in the `output/` directory

4. **Output Files**
   
   The scraper generates several files:
   - `combined_performance_data.csv` - Main dataset with all horse performances
   - `hkjc_data_race_info_TIMESTAMP.csv` - Race information
   - `hkjc_data_performance_TIMESTAMP.csv` - Individual performance records
   - `hkjc_data_errors_TIMESTAMP.txt` - Error log (if any)

### Step 2: Download Weather Data

1. **Visit HKO Data Portal**
   
   Go to: https://data.gov.hk/en-data/dataset/hk-hko-rss-current-weather-report

2. **Download Historical Weather Data**
   
   - Scroll down to "Download Historical Data"
   - Set your date range to match your scraping period (e.g., 2023-01-01 to 2025-07-14)
   - Click "Next" and select all available data files
   - Download the ZIP file containing all weather XML files

3. **Extract Weather Data**
   
   - Unzip the downloaded file
   - You'll get XML files named like: `20230101-0001-CurrentWeather.xml`
   - Place all XML files in a folder called `weather_info/` in your project directory

### Step 3: Reorganize Weather Files

1. **Run the Weather Reorganizer**
   ```bash
   python weather_reorganizer.py
   ```

2. **Follow the Interactive Prompts**
   - Choose to run in dry-run mode first (recommended)
   - Review the proposed file movements
   - Confirm to proceed with actual reorganization

3. **Result**
   - Files will be organized into `hourly_temperature/yyyy/mm/dd/` structure
   - Example: `20230101-1400-CurrentWeather.xml` → `hourly_temperature/2023/01/01/20230101-1400-CurrentWeather.xml`

### Step 4: Integrate Weather with Racing Data

1. **Run the Weather Processing Script**
   ```bash
   python process_weather_data.py
   ```

2. **Processing Logic**
   
   The script will:
   - Read `combined_performance_data.csv`
   - For each race, find the appropriate weather data:
     - **Sha Tin (ST)** races: Use afternoon temperature (14:00-15:00)
     - **Happy Valley (HV)** races: Use evening temperature (19:00-20:00)
   - Extract temperature from XML files using location-specific parsing
   - Add temperature column to the dataset
   - Sort data chronologically

3. **Output**
   - `combined_weather.csv` - Final dataset with racing data + temperature

## 📊 Data Schema

### Final Output (`combined_weather.csv`)

| Column | Description | Example |
|--------|-------------|---------|
| `date` | Race date | `2023-01-04` |
| `venue` | Racing venue | `ST`, `HV` |
| `race_no` | Race number | `1`, `2`, ..., `11` |
| `position` | Finishing position | `1`, `2`, `3`, etc. |
| `horse_no` | Horse number | `1`, `2`, ..., `14` |
| `horse_name` | Horse name | `WINNING DREAMER` |
| `horse_id` | HKJC horse ID | `HK_2019_V123` |
| `jockey` | Jockey name | `Z. Purton` |
| `trainer` | Trainer name | `C. S. Shum` |
| `weight` | Carried weight | `133`, `125` |
| `horse_weight` | Hourse weight | `1234`, `1332`, ..., `1445` |
| `temperature` | Race day temperature | `22`, `25` |

## 🔧 Script Details

### `hkjc_scraper.ipynb`
- **Purpose**: Web scraping of HKJC racing data
- **Technology**: Selenium WebDriver with Chrome
- **Features**:
  - CORS bypass using browser automation
  - Rate limiting for respectful scraping
  - Error handling and retry logic
  - Batch processing with periodic saves
  - Support for both racing venues
  - Date range configuration

### `weather_reorganizer.py`
- **Purpose**: Reorganize flat weather XML files into date hierarchy
- **Input**: XML files like `yyyymmdd-hhmm-CurrentWeather.xml`
- **Output**: Directory structure `hourly_temperature/yyyy/mm/dd/`
- **Features**:
  - Dry-run mode for safety
  - Automatic directory creation
  - File validation and error reporting

### `process_weather_data.py`
- **Purpose**: Integrate weather data with racing performances
- **Logic**:
  - Maps racing venues to weather locations
  - Uses time-of-day logic for venue-specific weather
  - Handles missing weather data gracefully
- **Features**:
  - Progress tracking for large datasets
  - Statistical summary of temperature data
  - Data validation and cleaning

## 📈 Usage Examples

### Small Test Run
```python
# In the Jupyter notebook
test_result = run_hkjc_scraper(
    start_date='2024-01-03',
    end_date='2024-01-07', 
    venues=['ST'],
    max_races=5
)
```

### Full Season Scrape
```python
# For complete 2024 season
result = run_hkjc_scraper(
    start_date='2024-01-01',
    end_date='2024-12-31',
    venues=['ST', 'HV'],
    max_races=None  # No limit
)
```

## 🛠️ Troubleshooting

### Common Issues

**WebDriver Problems**
- Ensure Chrome browser is installed
- Check internet connection
- Try running with `HEADLESS = False` to see browser actions

**Weather Data Missing**
- Verify XML files are in correct directory structure
- Check file naming convention matches expected format
- Ensure date ranges align between racing and weather data

**Memory Issues**
- Process data in smaller date ranges
- Use batch processing with periodic saves
- Close browser between large scraping sessions

**Rate Limiting**
- Increase `RATE_LIMIT` value in Config
- Respect HKJC server limitations
- Run during off-peak hours

### Data Quality Checks

```python
# Check for missing temperatures
df = pd.read_csv('combined_weather.csv')
missing_temp = df['temperature'].isna().sum()
print(f"Missing temperature data: {missing_temp} records")

# Verify venue distribution
venue_counts = df['venue'].value_counts()
print(venue_counts)

# Check date range
date_range = df['date'].agg(['min', 'max'])
print(f"Date range: {date_range['min']} to {date_range['max']}")
```

## 📚 Data Sources

- **Racing Data**: [HKJC Official Results](https://racing.hkjc.com/)
- **Weather Data**: [HKO Open Data via DATA.GOV.HK](https://data.gov.hk/en-data/dataset/hk-hko-rss-current-weather-report)

