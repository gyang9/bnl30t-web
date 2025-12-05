#!/usr/bin/env python3
import sys
import os

# Setup environment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DROP_DIR = os.path.join(BASE_DIR, 'drop')
sys.path.append(DROP_DIR)
sys.path.append(os.path.join(DROP_DIR, 'src'))
sys.path.append(os.path.join(DROP_DIR, 'tools'))
os.environ['SOURCE_DIR'] = DROP_DIR
os.environ['YAML_DIR'] = os.path.join(DROP_DIR, 'yaml')
os.environ['LIB_DIR'] = os.path.join(DROP_DIR, 'lib')

from event_display import EventDisplay

# Test file path - use the one from the web app
file_path = "/home/guang/work/bnl1t/drop/drop_jan26_24_pull/data_30ton/all_pmt_test_240624T1758_0.root"
yaml_path = os.path.join(DROP_DIR, 'yaml', 'config.yaml')

print(f"Testing peak time analysis on: {file_path}")
print("Initializing EventDisplay...")

try:
    ed = EventDisplay(file_path, yaml_path)
    print("EventDisplay initialized successfully")
    
    print("Starting peak time analysis...")
    peak_times = ed.get_all_peak_times()
    
    print(f"Analysis complete! Total channels: {len(peak_times)}")
    
    # Show first few results
    for ch in list(peak_times.keys())[:5]:
        print(f"  {ch}: {len(peak_times[ch])} events, first 5: {peak_times[ch][:5]}")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
