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