

import uproot
import numpy as np
import matplotlib.pyplot as plt
import glob
import os

# Ensure the output directory exists
os.makedirs("output_plots", exist_ok=True)

channel_map = {
    "b1ch2": 0, "b1ch3": 1, "b1ch4": 2, "b1ch5": 3, "b1ch6": 4, "b1ch7": 5, "b1ch8": 6, "b1ch9": 7, "b1ch10": 8, "b1ch11": 9,
    "b4ch9": 10, "b4ch10": 11, "b4ch11": 12, "b4ch12": 13, "b4ch18": 14, "b4ch19": 15, "b4ch20": 16, "b4ch21": 17
}

def process_files(file_list, trigger_channels, signal_channels, output_prefix):
    trigger_counts = {ch: 0 for ch in trigger_channels}
    
    for trigger_ch in trigger_channels:
        print(f"Processing trigger channel: {trigger_ch}")
        integrated_sums = []
        
        # Use uproot.iterate to process files in chunks for better memory management
        for basket in uproot.iterate(f"{file_list}:Events", ["wfs"], library="np"):
            wfs = basket["wfs"]
            
            for i in range(len(wfs)):
                # Process trigger waveform
                trigger_wf = wfs[i][channel_map[trigger_ch]]
                baseline = np.mean(trigger_wf[:200])
                trigger_wf_sub = trigger_wf - baseline
                trigger_wf_mV = trigger_wf_sub * 0.061
                trigger_wf_inv = -1 * trigger_wf_mV
                
                if np.min(trigger_wf_inv) < -1000:
                    trigger_counts[trigger_ch] += 1
                    
                    event_integrated_sum = 0
                    for signal_ch in signal_channels:
                        signal_wf = wfs[i][channel_map[signal_ch]]
                        baseline = np.mean(signal_wf[:200])
                        signal_wf_sub = signal_wf - baseline
                        signal_wf_mV = signal_wf_sub * 0.061
                        signal_wf_inv = -1 * signal_wf_mV
                        event_integrated_sum += np.sum(signal_wf_inv)
                        
                    integrated_sums.append(event_integrated_sum)

        plt.figure()
        plt.hist(integrated_sums, bins=100, histtype='step', label=f'Trigger Counts: {trigger_counts[trigger_ch]}')
        plt.title(f"Integrated Sum for trigger {trigger_ch}")
        plt.xlabel("Integrated ADC (mV)")
        plt.ylabel("Counts")
        plt.legend()
        plt.savefig(f"output_plots/{output_prefix}_{trigger_ch}_distribution.png")
        plt.close()

    return trigger_counts

if __name__ == "__main__":
    set1_files = "/home/guang/work/bnl1t/drop/drop_jan26_24_pull/data_30ton/majority_test_251027T0850_4*.root"
    set2_files = "/home/guang/work/bnl1t/drop/drop_jan26_24_pull/data_30ton/majority_test_251014T0854_4*.root"

    trigger_channels = ["b4ch9", "b4ch10", "b4ch11", "b4ch12", "b4ch18", "b4ch19", "b4ch20", "b4ch21"]
    signal_channels = [f"b1ch{i}" for i in range(2, 12)]

    print("Processing Set 1")
    set1_trigger_counts = process_files(set1_files, trigger_channels, signal_channels, "set1")
    print("Set 1 Trigger Counts:", set1_trigger_counts)

    print("\nProcessing Set 2")
    set2_trigger_counts = process_files(set2_files, trigger_channels, signal_channels, "set2")
    print("Set 2 Trigger Counts:", set2_trigger_counts)

