#!/usr/bin/env python3
"""
Weather XML File Reorganizer

This script reorganizes weather XML files from the current structure 
into a yyyy/mm/dd directory structure.

Expected file format: yyyymmdd-hhmm-CurrentWeather.xml
Target structure: /yyyy/mm/dd/yyyymmdd-hhmm-CurrentWeather.xml
"""

import os
import shutil
import re
from pathlib import Path

def extract_date_from_filename(filename):
    """
    Extract date components from filename like '20230101-0001-CurrentWeather.xml'
    Returns: (year, month, day) or None if format doesn't match
    """
    # Pattern to match: yyyymmdd-hhmm-*.xml
    pattern = r'^(\d{4})(\d{2})(\d{2})-\d{4}-.*\.xml$'
    match = re.match(pattern, filename)
    
    if match:
        year, month, day = match.groups()
        return year, month, day
    return None

def find_xml_files(base_path):
    """
    Find all XML files in the current directory structure
    Returns: list of (full_path, filename) tuples
    """
    xml_files = []
    base_path = Path(base_path)
    
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.xml'):
                full_path = Path(root) / file
                xml_files.append((full_path, file))
    
    return xml_files

def reorganize_files(source_dir, target_dir, dry_run=False):
    """
    Reorganize XML files from source_dir to target_dir in yyyy/mm/dd structure
    
    Args:
        source_dir: Path to the weather_info directory
        target_dir: Path to the new organized directory
        dry_run: If True, only print what would be done without actually moving files
    """
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    # Find all XML files
    xml_files = find_xml_files(source_path)
    
    if not xml_files:
        print("No XML files found in the source directory.")
        return
    
    print(f"Found {len(xml_files)} XML files to reorganize.")
    
    # Statistics
    moved_count = 0
    failed_count = 0
    
    for file_path, filename in xml_files:
        # Extract date from filename
        date_parts = extract_date_from_filename(filename)
        
        if not date_parts:
            print(f"Warning: Could not parse date from filename: {filename}")
            failed_count += 1
            continue
        
        year, month, day = date_parts
        
        # Create target directory structure
        target_file_dir = target_path / year / month / day
        target_file_path = target_file_dir / filename
        
        if dry_run:
            print(f"Would move: {file_path} -> {target_file_path}")
        else:
            # Create directory if it doesn't exist
            target_file_dir.mkdir(parents=True, exist_ok=True)
            
            try:
                # Move the file
                shutil.move(str(file_path), str(target_file_path))
                moved_count += 1
                print(f"Moved: {filename} -> {year}/{month}/{day}/")
            except Exception as e:
                print(f"Error moving {filename}: {e}")
                failed_count += 1
    
    print(f"\nSummary:")
    print(f"Successfully moved: {moved_count} files")
    print(f"Failed to move: {failed_count} files")
    print(f"Total processed: {len(xml_files)} files")

def main():
    """Main function"""
    print("Weather XML File Reorganizer")
    print("=" * 40)
    
    # Current directory setup
    current_dir = Path.cwd()
    weather_info_dir = current_dir / "weather_info"
    organized_dir = current_dir / "weather_organized"
    
    if not weather_info_dir.exists():
        print(f"Error: weather_info directory not found at {weather_info_dir}")
        return
    
    print(f"Source directory: {weather_info_dir}")
    print(f"Target directory: {organized_dir}")
    print()
    
    # Ask user for confirmation
    while True:
        choice = input("Run in dry-run mode first? (y/n): ").lower().strip()
        if choice in ['y', 'yes']:
            print("\n--- DRY RUN MODE ---")
            reorganize_files(weather_info_dir, organized_dir, dry_run=True)
            
            print("\n" + "=" * 40)
            proceed = input("Proceed with actual file movement? (y/n): ").lower().strip()
            if proceed in ['y', 'yes']:
                print("\n--- ACTUAL FILE MOVEMENT ---")
                reorganize_files(weather_info_dir, organized_dir, dry_run=False)
            else:
                print("Operation cancelled.")
            break
        elif choice in ['n', 'no']:
            print("\n--- ACTUAL FILE MOVEMENT ---")
            reorganize_files(weather_info_dir, organized_dir, dry_run=False)
            break
        else:
            print("Please enter 'y' or 'n'")

if __name__ == "__main__":
    main() 