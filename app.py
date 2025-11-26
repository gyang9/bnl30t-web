import sys
import os
import io
import base64
import numpy as np
import matplotlib
matplotlib.use('Agg') # Use non-interactive backend
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, jsonify, send_file

# Setup paths and environment variables (copied from gui.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DROP_DIR = os.path.join(BASE_DIR, 'drop')
sys.path.append(DROP_DIR)
sys.path.append(os.path.join(DROP_DIR, 'src'))
os.environ['SOURCE_DIR'] = DROP_DIR
os.environ['YAML_DIR'] = os.path.join(DROP_DIR, 'yaml')
os.environ['LIB_DIR'] = os.path.join(DROP_DIR, 'lib')

# Import analysis modules
# We need to wrap imports in try-except to handle potential missing dependencies during dev
try:
    from analysis import process_file, format_channel_name, get_persistence_data
    from tools.event_display import EventDisplay
    from display_event_gui import display_charge, display_3d_grid
except ImportError as e:
    print(f"Warning: Could not import analysis modules: {e}")
    import traceback
    traceback.print_exc()
    import_error_msg = str(e)
    process_file = None
    EventDisplay = None
    display_charge = None
    display_3d_grid = None
else:
    import_error_msg = None

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max upload
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Global state to hold the loaded file and event display object
# In a production multi-user app, this should be session-based or database-backed.
# For a local single-user tool, global state is acceptable.
current_state = {
    'file_path': None,
    'event_display': None,
    'min_id': 0,
    'max_id': 0
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        print("Upload request received")
        if 'file' not in request.files:
            print("No file part in request")
            return jsonify({'success': False, 'error': 'No file part'})
        file = request.files['file']
        if file.filename == '':
            print("No file selected")
            return jsonify({'success': False, 'error': 'No selected file'})
        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(f"Saving file to: {filepath}")
            file.save(filepath)
            print(f"File saved successfully: {filepath}")
            return jsonify({'success': True, 'filepath': filepath})
    except Exception as e:
        print(f"Upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/load_file', methods=['POST'])
def load_file():
    data = request.json
    file_path = data.get('file_path')
    
    # Check if backend modules are available
    if not EventDisplay:
        return jsonify({'success': False, 'error': f'Backend analysis modules not available. Error: {import_error_msg}'})
    
    if not file_path or not os.path.exists(file_path):
        return jsonify({'success': False, 'error': 'File not found'})

    try:
        current_state['file_path'] = file_path
        config_path = os.path.join(os.environ['YAML_DIR'], 'config_30t.yaml')
        
        # Initialize EventDisplay
        current_state['event_display'] = EventDisplay(file_path, config_path)
        min_id, max_id = current_state['event_display'].get_bound_id()
        current_state['min_id'] = int(min_id)
        current_state['max_id'] = int(max_id)
        return jsonify({
            'success': True, 
            'filename': os.path.basename(file_path),
            'min_id': int(min_id),
            'max_id': int(max_id)
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/histogram', methods=['POST'])
def generate_histogram():
    if not current_state['file_path']:
        return jsonify({'success': False, 'error': 'No file loaded'})

    data = request.json
    channel_string = data.get('channels', 'b1ch0')
    trigger_string = data.get('trigger', 'b4ch9')
    title = data.get('title', 'Histogram')

    try:
        # Parse channels (simple implementation, can be improved to match gui.py regex)
        # For now, let's assume the user inputs comma-separated list or we reuse the regex logic
        # We'll duplicate the regex logic here for simplicity or import it if we refactor
        signal_channels = parse_channel_string(channel_string)
        trigger_channels = parse_channel_string(trigger_string)

        if process_file:
            integrated_sums = process_file(
                current_state['file_path'], 
                trigger_channels=trigger_channels, 
                signal_channels=signal_channels
            )
            
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.hist(integrated_sums, bins=100, range=(-100000, 100000))
            ax.set_title(title)
            ax.set_xlabel("Integrated Sum (mV * samples)")
            ax.set_ylabel("Frequency")
            
            # Save to base64 image
            img = io.BytesIO()
            fig.savefig(img, format='png')
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()
            plt.close(fig)
            
            return jsonify({'success': True, 'image': plot_url})
        else:
            return jsonify({'success': False, 'error': 'Analysis module not loaded'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/event_grid', methods=['POST'])
def generate_event_grid():
    if not current_state['file_path']:
        return jsonify({'success': False, 'error': 'No file loaded'})

    data = request.json
    # Channels field is unused for this visualization as we show all PMTs in 3D
    trigger_string = data.get('trigger', 'b4ch9')
    title = data.get('title', '3D Event Grid')

    try:
        trigger_channels = parse_channel_string(trigger_string)
        
        # We need to find triggered events using the EventDisplay class or similar logic
        # Since EventDisplay is already initialized, let's use it if possible, 
        # but EventDisplay is designed for single event access.
        # We can iterate through events using the same logic as process_file but returning event IDs.
        
        # Let's use a helper to get triggered event IDs and data
        # We need to read the file again or use the existing EventDisplay
        
        ed = current_state['event_display']
        if not ed:
             return jsonify({'success': False, 'error': 'Event Display not initialized'})

        # Limit to first 9 triggered events for grid (3x3)
        max_events = 9
        events_data = []
        
        # We need to scan the file for triggers. 
        # Re-using the logic from analysis.py but inside here for simplicity or we could add a function to analysis.py
        # Let's add a function to analysis.py to get triggered event IDs? 
        # Or just iterate using ed.grab_events() which might be slow if we have to check every event.
        # Faster to use uproot directly like in analysis.py.
        
        # Let's use the process_file logic but adapted.
        # Actually, let's just use uproot here to find IDs, then use ed to get data.
        
        import uproot
        from analysis import format_channel_name, get_baseline
        
        ADC_TO_MV_B4 = 2000.0 / 4095.0
        trigger_threshold = 100.0
        
        with uproot.open(current_state['file_path']) as file:
            tree = file["daq"]
            trigger_branch_names = ["adc_" + format_channel_name(ch) for ch in trigger_channels]
            
            # Iterate to find triggered events
            events_found = 0
            events_scanned = 0
            max_scan_events = 10000 # Safety limit to prevent timeout
            
            # Fetch event_id and trigger channels
            # RunDROP needs ALL adc channels plus event info
            all_branches = tree.keys()
            branches_to_read = [b for b in all_branches if b.startswith('adc_')] + ['event_id', 'event_ttt_1', 'event_sanity']
            
            # Use default library (awkward) to be compatible with RunDROP
            for batch in tree.iterate(expressions=branches_to_read):
                if events_found >= max_events or events_scanned >= max_scan_events:
                    break
                
                n_batch_events = len(batch)
                
                for i in range(n_batch_events):
                    if events_found >= max_events or events_scanned >= max_scan_events:
                        break
                    
                    events_scanned += 1
                    is_triggered = False
                    for trigger_ch_name in trigger_branch_names:
                        # Convert to numpy for calculation
                        trigger_wf = batch[trigger_ch_name][i].to_numpy()
                        baseline = get_baseline(trigger_wf)
                        if np.any((-(trigger_wf - baseline) * ADC_TO_MV_B4) > trigger_threshold):
                            is_triggered = True
                            break
                    
                    if is_triggered:
                        # Get global event ID
                        global_evt_id = int(batch['event_id'][i])
                        
                        # OPTIMIZATION: Process the event directly from the current batch
                        # instead of calling grab_events() which re-reads the file from the start.
                        
                        # Create a mini-batch with just this event
                        # We need to slice all arrays in the batch
                        mini_batch = batch[i:i+1]
                        
                        # Use the existing EventDisplay's RunDROP instance to process this mini-batch
                        ed.run.process_batch(mini_batch, None)
                        
                        # The processed waveform is now in ed.run.wfm_list
                        if ed.run.wfm_list:
                            wfm = ed.run.wfm_list[0] # There should be only one
                            
                            if wfm and wfm.amp_pe:
                                evt_chg = []
                                atime = []
                                # Extract data for 3D plot
                                for ch in ed.run.ch_names:
                                    if 'b4' in ch: continue
                                    charge = 0
                                    peak_time = 0
                                    if ch in wfm.amp_pe:
                                        charge = np.sum(wfm.amp_pe[ch])
                                        peak_time = np.argmax(wfm.amp_pe[ch]) * 2
                                    evt_chg.append(charge)
                                    atime.append(peak_time)
                                
                                events_data.append({
                                    'event_id': global_evt_id,
                                    'chg': evt_chg,
                                    'atime': atime
                                })
                                events_found += 1
                            
                            # Clear the list to free memory/reset for next iteration
                            ed.run.wfm_list = []
                            ed.run.pf_list = []
                        else:
                            print(f"Debug: Failed to process event {global_evt_id}")

        if not events_data:
             return jsonify({
                 'success': False, 
                 'error': f'No events found matching trigger. Scanned {events_found} triggered events out of {max_events} requested. (Check trigger channels and threshold). Debug: Last checked ID {global_evt_id if "global_evt_id" in locals() else "None"}'
             })

        # Plotting
        if display_3d_grid:
            fig = plt.figure(figsize=(12, 12))
            display_3d_grid(events_data, fig)
            
            img = io.BytesIO()
            fig.savefig(img, format='png')
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()
            plt.close(fig)
            
            return jsonify({'success': True, 'image': plot_url})
        else:
            return jsonify({'success': False, 'error': 'Display module not loaded'})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/event_display', methods=['POST'])
def generate_event_display():
    if not current_state['event_display']:
        return jsonify({'success': False, 'error': 'Event Display not initialized'})

    data = request.json
    try:
        event_id = int(data.get('event_id', 0))
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid Event ID'})

    try:
        ed = current_state['event_display']
        ed.grab_events(event_id)
        wfm = ed.get_all_waveform(event_id)

        if not wfm:
             return jsonify({'success': False, 'error': f'Event {event_id} not found'})

        evt_chg = []
        atime = []
        for ch in ed.run.ch_names:
            if 'b4' in ch:
                continue
            charge = 0
            peak_time = 0
            if ch in wfm.amp_pe:
                charge = np.sum(wfm.amp_pe[ch])
                peak_time = np.argmax(wfm.amp_pe[ch]) * 2
            
            evt_chg.append(charge)
            atime.append(peak_time)

        fig = plt.figure(figsize=(10, 10))
        ax1 = fig.add_subplot(2, 2, 1)
        ax2 = fig.add_subplot(2, 2, 2)
        ax3d = fig.add_subplot(2, 1, 2, projection='3d')

        if display_charge:
            display_charge(evt_chg, [], atime, event_id, False, fig, ax1, ax2, ax3d)
            
            img = io.BytesIO()
            fig.savefig(img, format='png')
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()
            plt.close(fig)
            
            return jsonify({'success': True, 'image': plot_url})
        else:
             return jsonify({'success': False, 'error': 'Display module not loaded'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/waveform', methods=['POST'])
def generate_waveform():
    if not current_state['event_display']:
        return jsonify({'success': False, 'error': 'Event Display not initialized'})

    data = request.json
    try:
        event_id = int(data.get('event_id', 0))
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid Event ID'})

    try:
        ed = current_state['event_display']
        wfm = ed.get_all_waveform(event_id)

        if wfm and wfm.amp_pe:
            channels_with_data = [ch for ch in ed.run.ch_names if ch in wfm.amp_pe]
            n_channels = len(channels_with_data)
            
            if n_channels > 0:
                n_cols = int(np.ceil(np.sqrt(n_channels)))
                n_rows = int(np.ceil(n_channels / n_cols))
                
                fig = plt.figure(figsize=(12, 8))
                for i, ch in enumerate(channels_with_data):
                    ax = fig.add_subplot(n_rows, n_cols, i + 1)
                    ax.plot(wfm.amp_pe[ch])
                    ax.set_title(ch, fontsize='small')
                    ax.set_xlabel("Sample", fontsize='small')
                    ax.set_ylabel("PE", fontsize='small')
                    ax.tick_params(axis='both', which='major', labelsize='small')

                fig.tight_layout()
                
                img = io.BytesIO()
                fig.savefig(img, format='png')
                img.seek(0)
                plot_url = base64.b64encode(img.getvalue()).decode()
                plt.close(fig)
                
                return jsonify({'success': True, 'image': plot_url})
            else:
                return jsonify({'success': False, 'error': 'No waveform data found'})
        else:
            return jsonify({'success': False, 'error': 'Waveforms not found'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def parse_channel_string(channel_string):
    import re
    channels = []
    parts = channel_string.split(',')
    for part in parts:
        part = part.strip()
        if '-' in part:
            match = re.match(r"(\w+)ch(\d+)-(\w+)ch(\d+)", part)
            if match:
                prefix1, start, prefix2, end = match.groups()
                if prefix1 == prefix2:
                    for i in range(int(start), int(end) + 1):
                        channels.append(f"{prefix1}ch{i}")
            else: # simplified range, like b1ch2-8
                match = re.match(r"(\w+)ch(\d+)-(\d+)", part)
                if match:
                    prefix, start, end = match.groups()
                    for i in range(int(start), int(end) + 1):
                        channels.append(f"{prefix}ch{i}")

        else:
            channels.append(part)
    return channels

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)
