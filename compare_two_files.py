#!/usr/bin/env python3
import argparse
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import re
import uproot

# Add necessary paths to sys.path
sys.path.append("/home/guang/work/bnl1t/drop/drop_jan26_24_pull/drop/tools")
sys.path.append("/home/guang/work/bnl1t/drop/drop_jan26_24_pull/drop/src")

from event_display import EventDisplay

def get_flat_baseline(val):
    """
    Calculate median and std for baseline.
    """
    # A simplified version from waveform.py
    if len(val) == 0:
        return 0, 0
    q = np.quantile(val, [0.15865, 0.5, 0.84135])
    return q[1], abs(q[2]-q[0])/2

def process_file(filepath, n_events, m_plots, bottom_pmts, output_dir):
    """
    Process a single ROOT file.
    """
    print(f"Processing file: {filepath}")

    # Use uproot to get event IDs
    try:
        with uproot.open(filepath) as f:
            if "daq" not in f:
                print(f"Error: 'daq' tree not found in {filepath}")
                return
            all_event_ids = f["daq"]["event_id"].array(library="np")
    except Exception as e:
        print(f"Error reading event IDs from {filepath}: {e}")
        return

    print(f"Found {len(all_event_ids)} events in {filepath}.")
    event_ids_to_process = all_event_ids[:n_events]
    print(f"First {n_events} event IDs to process: {event_ids_to_process}")
    
    # Use the 30-ton configuration file
    config_path = "/home/guang/work/bnl1t/drop/drop_jan26_24_pull/drop/yaml/config_30t.yaml"
    
    try:
        ed = EventDisplay(filepath, config_path)
    except Exception as e:
        print(f"Error initializing EventDisplay for {filepath}: {e}")
        return

    plots_made = 0
    
    # ADC to mV conversion factors from waveform.py
    dgtz_dynamic_range_mV = ed.run.cfg.dgtz_dynamic_range_mV
    adc_to_mV = dgtz_dynamic_range_mV / (2**14 - 1)
    adc_to_mV_b4 = dgtz_dynamic_range_mV / (2**12 - 1)

    for event_id in event_ids_to_process:
        if plots_made >= m_plots:
            break

        print(f"Grabbing event {event_id} from {os.path.basename(filepath)}...")
        
        try:
            num_grabbed = ed.grab_events(int(event_id))
            if num_grabbed == 0:
                print(f"Event {event_id} not found in {filepath}. Trying next event.")
                continue
        except Exception as e:
            print(f"Could not grab event {event_id}. Error: {e}")
            continue

        wfm = ed.get_all_waveform(int(event_id))
        if wfm is None:
            print(f"Waveform for event {event_id} not found.")
            continue

        waveforms_mV = {}
        condition_met = False
        
        for ch in ed.run.ch_names:
            if ch in wfm.raw_data:
                raw_wfm = wfm.raw_data[ch]
                
                # Baseline subtraction
                baseline, _ = get_flat_baseline(raw_wfm)
                subtracted_wfm = -(raw_wfm - baseline)
                
                # ADC to mV conversion
                if 'b4' in ch:
                    waveforms_mV[ch] = subtracted_wfm * adc_to_mV_b4
                else:
                    waveforms_mV[ch] = subtracted_wfm * adc_to_mV

                # Check threshold for bottom PMTs
                if ch in bottom_pmts:
                    if np.max(waveforms_mV[ch]) > 1000:
                        condition_met = True

        if condition_met:
            print(f"Event {event_id} meets the threshold condition. Plotting...")
            
            # Create plots
            num_channels = len(ed.run.ch_names)
            grid_size = int(np.ceil(np.sqrt(num_channels)))
            fig, axes = plt.subplots(grid_size, grid_size, figsize=(20, 20), sharex=True, sharey=True)
            fig.suptitle(f'File: {os.path.basename(filepath)} - Event {event_id}')
            axes = axes.flatten()

            for i, ch in enumerate(ed.run.ch_names):
                ax = axes[i]
                if ch in waveforms_mV:
                    ax.plot(waveforms_mV[ch])
                    ax.set_title(ch, fontsize=8)
                else:
                    ax.set_title(f'{ch} - No data', fontsize=8)
                ax.grid(True)

            for i in range(num_channels, len(axes)):
                axes[i].set_visible(False)
            
            plt.tight_layout(rect=[0, 0.03, 1, 0.95])
            
            # Save the figure
            plot_filename = f"{output_dir}/event_{event_id}_from_{os.path.basename(filepath)}.png"
            plt.savefig(plot_filename)
            plt.close(fig)
            print(f"Saved plot: {plot_filename}")
            
            plots_made += 1

def main():
    parser = argparse.ArgumentParser(description='Compare waveforms from two ROOT files.')
    parser.add_argument('file1', type=str, help='Path to the first ROOT file.')
    parser.add_argument('file2', type=str, help='Path to the second ROOT file.')
    parser.add_argument('--n', type=int, default=20, help='Number of events to process per file.')
    parser.add_argument('--m', type=int, default=20, help='Maximum number of events to plot per file.')
    parser.add_argument('--output_dir', type=str, default='waveform_comparison_plots', help='Directory to save plots.')
    parser.add_argument('--interactive', action='store_true', help='Display plots interactively instead of saving them to files.')
    args = parser.parse_args()

    bottom_pmts = [f'adc_b4_ch{i}' for i in range(9, 13)] + [f'adc_b4_ch{i}' for i in range(18, 22)]
    
    if not os.path.exists(args.output_dir) and not args.interactive:
        os.makedirs(args.output_dir)

    for filepath in [args.file1, args.file2]:
        process_file(filepath, args.n, args.m, bottom_pmts, args.output_dir, args.interactive)

if __name__ == '__main__':
    main()
