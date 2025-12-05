import sys
import os
import time

# Setup environment
src_path = "/home/guang/.gemini/antigravity/scratch/bnl1t_web/drop/src"
yaml_path = "/home/guang/.gemini/antigravity/scratch/bnl1t_web/drop/yaml/config.yaml"
os.environ['SOURCE_DIR'] = src_path
os.environ['YAML_DIR'] = "/home/guang/.gemini/antigravity/scratch/bnl1t_web/drop/yaml"
os.environ['LIB_DIR'] = "/home/guang/.gemini/antigravity/scratch/bnl1t_web/drop/lib"
sys.path.append(src_path)
sys.path.append("/home/guang/.gemini/antigravity/scratch/bnl1t_web/drop/tools")

from event_display import EventDisplay

def test_analysis():
    file_path = "/home/guang/work/bnl1t/drop/drop_jan26_24_pull/data_30ton/all_pmt_test_240624T1758_0.root" # Small file
    # file_path = "/home/guang/work/bnl1t/drop/drop_jan26_24_pull/data_30ton/majority_test_251031T0706_0.root" # Large file
    
    print(f"Loading file: {file_path}")
    ed = EventDisplay(file_path, yaml_path)
    
    print("Starting analysis...")
    start_time = time.time()
    try:
        peak_times = ed.get_all_peak_times()
        end_time = time.time()
        print(f"Analysis complete in {end_time - start_time:.2f} seconds")
        print(f"Total channels: {len(peak_times)}")
        for ch, times in list(peak_times.items())[:5]:
            print(f"Channel {ch}: {len(times)} events, first 5: {times[:5]}")
            
    except Exception as e:
        print(f"Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_analysis()
