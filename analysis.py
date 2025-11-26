import uproot
import numpy as np

def get_baseline(waveform):
    """Calculates the baseline of a waveform using the median of the first 100 samples."""
    n_baseline_samples = min(100, len(waveform))
    if n_baseline_samples == 0:
        return 0
    baseline_samples = np.sort(waveform[:n_baseline_samples])
    return np.median(baseline_samples)

def format_channel_name(original_name):
    """Converts 'bXchY' to 'bX_chY'."""
    import re
    match = re.match(r"b(\d)ch(\d+)", original_name)
    if match:
        return f"b{match.group(1)}_ch{match.group(2)}"
    return original_name

def process_file(file_path, trigger_channels=["b4ch9"], signal_channels=["b1ch2"], trigger_threshold=100.0):
    """
    Processes a ROOT file to extract integrated sums of waveforms based on a trigger.
    This version reads waveforms from individual channel branches and supports multiple trigger channels.
    """
    integrated_sums = []
    
    # ADC to mV conversion factors
    ADC_TO_MV_B4 = 2000.0 / 4095.0
    ADC_TO_MV_B1 = 2000.0 / 16383.0

    try:
        with uproot.open(file_path) as file:
            tree = file["daq"]
            
            trigger_branch_names = ["adc_" + format_channel_name(ch) for ch in trigger_channels]
            signal_branch_names = ["adc_" + format_channel_name(ch) for ch in signal_channels]
            
            all_branches = trigger_branch_names + signal_branch_names
            
            for batch in tree.iterate(expressions=all_branches, library="np"):
                for i in range(len(batch[trigger_branch_names[0]])): # Iterate over events in batch
                    is_triggered = False
                    for trigger_ch_name in trigger_branch_names:
                        trigger_wf = batch[trigger_ch_name][i]
                        baseline = get_baseline(trigger_wf)
                        
                        for sample in trigger_wf:
                            if (-(sample - baseline) * ADC_TO_MV_B4) > trigger_threshold:
                                is_triggered = True
                                break
                        if is_triggered:
                            break
                    
                    if is_triggered:
                        event_integrated_sum = 0
                        for ch_name in signal_branch_names:
                            signal_wf = batch[ch_name][i]
                            baseline_signal = get_baseline(signal_wf)
                            # Sum and convert to mV
                            event_integrated_sum += np.sum(-(signal_wf - baseline_signal) * ADC_TO_MV_B1)
                        
                        integrated_sums.append(event_integrated_sum)

    except Exception as e:
        print(f"Error processing file: {e}")
        # Reraise or handle as appropriate
        raise
    
    return integrated_sums

def get_persistence_data(file_path, trigger_channels=["b4ch9"], signal_channels=["b1ch2"], trigger_threshold=100.0):
    """
    Generates a 2D histogram (persistence plot) of waveforms.
    Returns: x_edges, y_edges, histogram_matrix
    """
    # ADC to mV conversion factors
    ADC_TO_MV_B4 = 2000.0 / 4095.0
    ADC_TO_MV_B1 = 2000.0 / 16383.0

    accumulated_waveforms = []
    
    try:
        with uproot.open(file_path) as file:
            tree = file["daq"]
            
            trigger_branch_names = ["adc_" + format_channel_name(ch) for ch in trigger_channels]
            signal_branch_names = ["adc_" + format_channel_name(ch) for ch in signal_channels]
            
            all_branches = trigger_branch_names + signal_branch_names
            
            # Limit to first 1000 triggered events to avoid OOM on free tier
            max_events = 1000
            events_found = 0

            for batch in tree.iterate(expressions=all_branches, library="np"):
                if events_found >= max_events:
                    break

                for i in range(len(batch[trigger_branch_names[0]])): # Iterate over events in batch
                    if events_found >= max_events:
                        break

                    is_triggered = False
                    for trigger_ch_name in trigger_branch_names:
                        trigger_wf = batch[trigger_ch_name][i]
                        baseline = get_baseline(trigger_wf)
                        
                        # Check trigger condition
                        if np.any((-(trigger_wf - baseline) * ADC_TO_MV_B4) > trigger_threshold):
                            is_triggered = True
                            break
                    
                    if is_triggered:
                        # For persistence, we usually overlay the signal channel(s)
                        # Let's take the first signal channel for now, or sum them?
                        # Usually persistence is per-channel. Let's sum them to match the histogram logic.
                        
                        combined_wf = None
                        for ch_name in signal_branch_names:
                            signal_wf = batch[ch_name][i]
                            baseline_signal = get_baseline(signal_wf)
                            wf_mv = -(signal_wf - baseline_signal) * ADC_TO_MV_B1
                            
                            if combined_wf is None:
                                combined_wf = wf_mv
                            else:
                                combined_wf += wf_mv
                        
                        if combined_wf is not None:
                            accumulated_waveforms.append(combined_wf)
                            events_found += 1

        if not accumulated_waveforms:
            return None, None, None

        # Create 2D Histogram
        waveforms = np.array(accumulated_waveforms)
        n_samples = waveforms.shape[1]
        time_axis = np.arange(n_samples) * 2 # 2ns per sample
        
        # Flatten for histogram2d: we need pairs of (t, amp)
        # This can be memory intensive. Let's do it efficiently.
        
        # Define bins
        t_bins = np.linspace(0, n_samples * 2, n_samples + 1)
        amp_min = np.min(waveforms)
        amp_max = np.max(waveforms)
        # Add some padding
        amp_range = amp_max - amp_min
        amp_bins = np.linspace(amp_min - 0.1*amp_range, amp_max + 0.1*amp_range, 100)
        
        H = np.zeros((len(amp_bins)-1, len(t_bins)-1))
        
        # Fill histogram
        for wf in waveforms:
            # For each waveform, we have (time_axis, wf) points
            # np.histogram2d is slow for many points.
            # Faster: iterate time slices?
            for t_idx in range(n_samples):
                amp_val = wf[t_idx]
                # Find amp bin
                amp_bin_idx = np.searchsorted(amp_bins, amp_val) - 1
                if 0 <= amp_bin_idx < len(amp_bins) - 1:
                    H[amp_bin_idx, t_idx] += 1
                    
        return t_bins, amp_bins, H

    except Exception as e:
        print(f"Error processing persistence: {e}")
        raise