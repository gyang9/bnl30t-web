import argparse
import sys
import os
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
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



def plot_waveforms(waveforms, event_id, title_prefix, output_dir, ed, interactive_mode):
    """Helper function to generate and show/save a plot."""
    if interactive_mode:
        print(f"Displaying {title_prefix} plot for event {event_id}... (Close window to continue)")
    else:
        print(f"Plotting {title_prefix} event {event_id}...")

    num_channels = len(ed.run.ch_names)
    grid_size = int(np.ceil(np.sqrt(num_channels)))
    fig, axes = plt.subplots(grid_size, grid_size, figsize=(20, 20), sharex=True, sharey=True)
    fig.suptitle(f'{title_prefix} - File: {os.path.basename(ed.args.if_path)} - Event {event_id}')
    axes = axes.flatten()

    for i, ch in enumerate(ed.run.ch_names):
        ax = axes[i]
        if ch in waveforms:
            ax.plot(waveforms[ch])
            ax.set_title(ch, fontsize=8)
        else:
            ax.set_title(f'{ch} - No data', fontsize=8)
        ax.grid(True)

    for i in range(num_channels, len(axes)):
        axes[i].set_visible(False)
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    if interactive_mode:
        plt.show()
    else:
        plot_filename = f"{output_dir}/event_{event_id}.png"
        plt.savefig(plot_filename)
        plt.close(fig)
        print(f"Saved plot: {plot_filename}")

def process_file(filepath, n_unconditional, m_conditional, bottom_pmts, output_dir, interactive_mode=False):
    """
    Process a single ROOT file.
    """
    print(f"Processing file: {filepath}")

    # Prepare output directories
    unconditional_dir = os.path.join(output_dir, 'unconditional')
    conditional_dir = os.path.join(output_dir, 'conditional')
    if not interactive_mode:
        os.makedirs(unconditional_dir, exist_ok=True)
        os.makedirs(conditional_dir, exist_ok=True)

    # --- Data Collection ---
    unconditional_waveforms = []
    unconditional_ids = []
    conditional_waveforms = []
    conditional_ids = []

    try:
        with uproot.open(filepath) as f:
            if "daq" not in f:
                print(f"Error: 'daq' tree not found in {filepath}")
                return
            all_event_ids = f["daq"]["event_id"].array(library="np")
    except Exception as e:
        print(f"Error reading event IDs from {filepath}: {e}")
        return

    print(f"Found {len(all_event_ids)} events. Starting search...")

    try:
        ed = EventDisplay(filepath, "/home/guang/work/bnl1t/drop/drop_jan26_24_pull/drop/yaml/config_30t.yaml")
    except Exception as e:
        print(f"Error initializing EventDisplay for {filepath}: {e}")
        return

    dgtz_dynamic_range_mV = ed.run.cfg.dgtz_dynamic_range_mV
    adc_to_mV_b4 = dgtz_dynamic_range_mV / (2**12 - 1)

    for event_id in all_event_ids:
        if len(unconditional_ids) >= n_unconditional and len(conditional_ids) >= m_conditional:
            print("Found enough events of both types. Stopping search.")
            break

        print(f"Processing event {event_id}...")
        num_grabbed = ed.grab_events(int(event_id))
        if num_grabbed == 0:
            continue
        
        wfm = ed.get_all_waveform(int(event_id))
        if wfm is None:
            continue

        waveforms_mV = {}
        condition_met = False
        for ch in ed.run.ch_names:
            if ch in wfm.raw_data:
                raw_wfm = wfm.raw_data[ch]
                baseline, _ = get_flat_baseline(raw_wfm)
                subtracted_wfm = -(raw_wfm - baseline)
                if 'b4' in ch:
                    waveforms_mV[ch] = subtracted_wfm * adc_to_mV_b4
                else:
                    # Assuming 14-bit for other channels as in previous versions
                    adc_to_mV = dgtz_dynamic_range_mV / (2**14 - 1)
                    waveforms_mV[ch] = subtracted_wfm * adc_to_mV

                if ch in bottom_pmts and np.max(waveforms_mV[ch]) > 1000:
                    condition_met = True

        # Store unconditional events
        if len(unconditional_ids) < n_unconditional:
            unconditional_waveforms.append(waveforms_mV)
            unconditional_ids.append(event_id)
            print(f"Stored event {event_id} for unconditional plot.")

        # Store conditional events
        if condition_met and len(conditional_ids) < m_conditional:
            conditional_waveforms.append(waveforms_mV)
            conditional_ids.append(event_id)
            print(f"Stored event {event_id} for conditional plot (peak > 1V).")

    # --- Plotting at the end ---
    print(f"\nFinished processing. Now creating plots.")

    # Plot unconditional events
    print(f"--- Generating {len(unconditional_ids)} unconditional plots ---")
    for i, waveforms in enumerate(unconditional_waveforms):
        event_id = unconditional_ids[i]
        plot_waveforms(waveforms, event_id, "Unconditional", unconditional_dir, ed, interactive_mode)

    # Plot conditional events
    print(f"--- Generating {len(conditional_ids)} conditional plots ---")
    for i, waveforms in enumerate(conditional_waveforms):
        event_id = conditional_ids[i]
        plot_waveforms(waveforms, event_id, "Conditional", conditional_dir, ed, interactive_mode)

def main():
    print(f"Using Matplotlib backend: {matplotlib.get_backend()}")
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
