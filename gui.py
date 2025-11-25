import sys
import os
import numpy as np
import re

# Add the 'drop' directory to the python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'drop'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'drop', 'src'))
os.environ['SOURCE_DIR'] = os.path.join(os.path.dirname(__file__), 'drop')
os.environ['YAML_DIR'] = os.path.join(os.path.dirname(__file__), 'drop', 'yaml')
os.environ['LIB_DIR'] = os.path.join(os.path.dirname(__file__), 'drop', 'lib')

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QPushButton, QLabel, QLineEdit, QFileDialog, QHBoxLayout, QStatusBar
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from analysis import process_file
from display_event_gui import display_charge
from tools.event_display import EventDisplay

class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100, figure=None):
        if figure is None:
            self.fig = Figure(figsize=(width, height), dpi=dpi)
            self.axes = self.fig.add_subplot(111)
        else:
            self.fig = figure
        super(MatplotlibCanvas, self).__init__(self.fig)
        self.setParent(parent)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analysis GUI")
        self.setGeometry(100, 100, 1200, 800)

        self.file_path = None
        self.event_display = None

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # File selection
        self.file_label = QLabel("No file loaded.")
        self.load_button = QPushButton("Load File")
        self.load_button.clicked.connect(self.load_file)
        
        file_layout = QHBoxLayout()
        file_layout.addWidget(self.load_button)
        file_layout.addWidget(self.file_label)
        file_layout.addStretch()
        self.layout.addLayout(file_layout)

        # Tab widget
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Histogram Tab
        self.hist_tab = QWidget()
        self.tabs.addTab(self.hist_tab, "Histogram")
        self.hist_layout = QVBoxLayout(self.hist_tab)
        
        hist1_layout = QHBoxLayout()
        self.hist1_channels_input = QLineEdit("b1ch0,b1ch2-b1ch8,b1ch10-b1ch11")
        self.show_hist1_button = QPushButton("Generate Histogram 1")
        self.show_hist1_button.clicked.connect(self.show_histogram1)
        self.show_hist1_button.setEnabled(False)
        hist1_layout.addWidget(self.hist1_channels_input)
        hist1_layout.addWidget(self.show_hist1_button)
        self.hist_layout.addLayout(hist1_layout)

        hist2_layout = QHBoxLayout()
        self.hist2_channels_input = QLineEdit("b1ch12-b1ch15,b2ch0-b2ch15,b3ch0-b3ch3")
        self.show_hist2_button = QPushButton("Generate Histogram 2")
        self.show_hist2_button.clicked.connect(self.show_histogram2)
        self.show_hist2_button.setEnabled(False)
        hist2_layout.addWidget(self.hist2_channels_input)
        hist2_layout.addWidget(self.show_hist2_button)
        self.hist_layout.addLayout(hist2_layout)

        trigger_layout = QHBoxLayout()
        trigger_layout.addWidget(QLabel("Trigger Channels:"))
        self.trigger_channels_input = QLineEdit("b4ch9-b4ch12,b4ch18-b4ch21")
        trigger_layout.addWidget(self.trigger_channels_input)
        self.hist_layout.addLayout(trigger_layout)

        self.hist_canvas = MatplotlibCanvas(self)
        self.hist_layout.addWidget(self.hist_canvas)

        # Event Display Tab
        self.event_tab = QWidget()
        self.tabs.addTab(self.event_tab, "Event Display")
        self.event_layout = QVBoxLayout(self.event_tab)

        event_controls_layout = QHBoxLayout()
        self.event_id_label = QLabel("Event ID:")
        self.event_id_input = QLineEdit()
        self.show_event_button = QPushButton("Show Event")
        self.show_event_button.clicked.connect(self.show_event_display)
        self.show_event_button.setEnabled(False)
        self.event_range_label = QLabel("Valid event range: [N/A]")
        event_controls_layout.addWidget(self.event_id_label)
        event_controls_layout.addWidget(self.event_id_input)
        event_controls_layout.addWidget(self.show_event_button)
        event_controls_layout.addWidget(self.event_range_label)
        event_controls_layout.addStretch()

        self.event_layout.addLayout(event_controls_layout)

        event_fig = Figure(figsize=(10, 10), dpi=100)
        self.event_ax1 = event_fig.add_subplot(2, 2, 1)
        self.event_ax2 = event_fig.add_subplot(2, 2, 2)
        self.event_ax3d = event_fig.add_subplot(2, 1, 2, projection='3d')
        self.event_canvas = MatplotlibCanvas(self, figure=event_fig)
        self.event_layout.addWidget(self.event_canvas)
        

        # Waveform Tab
        self.waveform_tab = QWidget()
        self.tabs.addTab(self.waveform_tab, "Waveform")
        self.waveform_layout = QVBoxLayout(self.waveform_tab)

        waveform_controls_layout = QHBoxLayout()
        self.wf_event_id_label = QLabel("Event ID:")
        self.wf_event_id_input = QLineEdit()
        self.show_waveform_button = QPushButton("Show All Waveforms")
        self.show_waveform_button.clicked.connect(self.show_waveform)
        self.show_waveform_button.setEnabled(False)
        self.wf_event_range_label = QLabel("Valid event range: [N/A]")
        waveform_controls_layout.addWidget(self.wf_event_id_label)
        waveform_controls_layout.addWidget(self.wf_event_id_input)
        waveform_controls_layout.addWidget(self.show_waveform_button)
        waveform_controls_layout.addWidget(self.wf_event_range_label)
        waveform_controls_layout.addStretch()
        self.waveform_layout.addLayout(waveform_controls_layout)

        self.waveform_canvas = MatplotlibCanvas(self)
        self.waveform_layout.addWidget(self.waveform_canvas)
        
        self.setStatusBar(QStatusBar(self))

    def parse_channel_string(self, channel_string):
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
    
    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open ROOT File", "", "ROOT Files (*.root)")
        if file_path:
            self.file_path = file_path
            self.file_label.setText(f"Loaded: {os.path.basename(self.file_path)}")
            self.statusBar().showMessage("File loaded successfully.", 2000)
            self.show_hist1_button.setEnabled(True)
            self.show_hist2_button.setEnabled(True)
            self.show_event_button.setEnabled(True)
            self.show_waveform_button.setEnabled(True)

            try:
                self.statusBar().showMessage("Getting event range...")
                QApplication.processEvents()
                config_path = os.path.join(os.environ['YAML_DIR'], 'config_30t.yaml')
                self.event_display = EventDisplay(self.file_path, config_path)
                min_id, max_id = self.event_display.get_bound_id()
                self.event_range_label.setText(f"Valid event range: [{min_id}, {max_id}]")
                self.wf_event_range_label.setText(f"Valid event range: [{min_id}, {max_id}]")
                self.statusBar().showMessage("Event range loaded.", 2000)
            except Exception as e:
                self.event_range_label.setText("Valid event range: [Error]")
                self.wf_event_range_label.setText("Valid event range: [Error]")
                self.statusBar().showMessage(f"Error getting event range: {e}", 5000)

    def show_histogram1(self):
        channel_string = self.hist1_channels_input.text()
        signal_channels = self.parse_channel_string(channel_string)
        self.generate_histogram(signal_channels, "Histogram 1")

    def show_histogram2(self):
        channel_string = self.hist2_channels_input.text()
        signal_channels = self.parse_channel_string(channel_string)
        self.generate_histogram(signal_channels, "Histogram 2")

    def generate_histogram(self, signal_channels, title):
        if self.file_path:
            try:
                self.statusBar().showMessage("Generating histogram...")
                print(f"Generating {title}...")
                QApplication.processEvents()

                trigger_channel_string = self.trigger_channels_input.text()
                trigger_channels = self.parse_channel_string(trigger_channel_string)
                
                integrated_sums = process_file(self.file_path, trigger_channels=trigger_channels, signal_channels=signal_channels)
                
                self.hist_canvas.axes.clear()
                self.hist_canvas.axes.hist(integrated_sums, bins=100, range=(-100000, 100000))
                self.hist_canvas.axes.set_title(title)
                self.hist_canvas.axes.set_xlabel("Integrated Sum (mV * samples)")
                self.hist_canvas.axes.set_ylabel("Frequency")
                self.hist_canvas.draw()
                
                self.statusBar().showMessage("Histogram displayed.", 2000)
                print(f"{title} generated.")
            except Exception as e:
                self.statusBar().showMessage(f"Error generating histogram: {e}", 5000)
                print(f"Error generating histogram: {e}")
        else:
            self.statusBar().showMessage("No file loaded.", 2000)
            print("No file loaded for histogram generation.")

    def show_waveform(self):
        if self.file_path and self.wf_event_id_input.text() and self.event_display:
            try:
                event_id = int(self.wf_event_id_input.text())
            except ValueError:
                self.statusBar().showMessage("Invalid Event ID.", 2000)
                return

            self.statusBar().showMessage(f"Getting waveforms for event {event_id}...")
            QApplication.processEvents()
            
            self.waveform_canvas.fig.clear()

            try:
                wfm = self.event_display.get_all_waveform(event_id)

                if wfm and wfm.amp_pe:
                    channels_with_data = [ch for ch in self.event_display.run.ch_names if ch in wfm.amp_pe]
                    n_channels = len(channels_with_data)
                    if n_channels > 0:
                        n_cols = int(np.ceil(np.sqrt(n_channels)))
                        n_rows = int(np.ceil(n_channels / n_cols))
                        
                        for i, ch in enumerate(channels_with_data):
                            ax = self.waveform_canvas.fig.add_subplot(n_rows, n_cols, i + 1)
                            ax.plot(wfm.amp_pe[ch])
                            ax.set_title(ch, fontsize='small')
                            ax.set_xlabel("Sample", fontsize='small')
                            ax.set_ylabel("PE", fontsize='small')
                            ax.tick_params(axis='both', which='major', labelsize='small')

                        self.waveform_canvas.fig.tight_layout()
                        self.waveform_canvas.draw()
                        self.statusBar().showMessage("Waveforms displayed.", 2000)
                    else:
                        self.statusBar().showMessage("No waveform data found for this event.", 2000)

                else:
                    self.statusBar().showMessage("Waveforms not found for this event.", 2000)
            except Exception as e:
                self.statusBar().showMessage(f"Error displaying waveforms: {e}", 5000)
        elif not self.file_path:
            self.statusBar().showMessage("No file loaded.", 2000)
        elif not self.event_display:
            self.statusBar().showMessage("Event display not initialized. Please re-load the file.", 5000)
        else:
            self.statusBar().showMessage("Please enter an Event ID.", 2000)

    def show_event_display(self):
        if self.file_path and self.event_id_input.text() and self.event_display:
            try:
                event_id = int(self.event_id_input.text())
            except ValueError:
                self.statusBar().showMessage("Invalid Event ID.", 2000)
                print("Invalid Event ID entered.")
                return

            self.statusBar().showMessage(f"Processing event {event_id}...")
            print(f"Generating event display for event {event_id}...")
            QApplication.processEvents()
            
            self.event_ax1.clear()
            self.event_ax2.clear()
            self.event_ax3d.clear()

            try:
                print(f"Grabbing event {event_id}...")
                self.event_display.grab_events(event_id)
                print(f"Getting waveform for event {event_id}...")
                wfm = self.event_display.get_all_waveform(event_id)

                if wfm:
                    print("Successfully grabbed event. Calculating charge and time...")
                    evt_chg = []
                    atime = []
                    for ch_i, ch in enumerate(self.event_display.run.ch_names):
                        if 'b4' in ch:
                            continue
                        charge = 0
                        peak_time = 0
                        if ch in wfm.amp_pe:
                            charge = np.sum(wfm.amp_pe[ch])
                            peak_time = np.argmax(wfm.amp_pe[ch]) * 2
                        
                        evt_chg.append(charge)
                        atime.append(peak_time)

                    print("Drawing event display...")
                    display_charge(evt_chg, [], atime, event_id, False, self.event_canvas.fig, self.event_ax1, self.event_ax2, self.event_ax3d)
                    self.event_canvas.draw()
                    self.statusBar().showMessage(f"Event {event_id} displayed.", 2000)
                    print("Event display generated.")
                else:
                    self.statusBar().showMessage(f"Event {event_id} not found.", 2000)
                    print(f"Event {event_id} not found.")
            except Exception as e:
                self.statusBar().showMessage(f"Error displaying event: {e}", 5000)
                print(f"Error displaying event: {e}")
        elif not self.file_path:
            self.statusBar().showMessage("No file loaded.", 2000)
            print("No file loaded for event display.")
        elif not self.event_display:
            self.statusBar().showMessage("Event display not initialized. Please re-load the file.", 5000)
            print("Event display not initialized.")
        else:
            self.statusBar().showMessage("Please enter an Event ID.", 2000)
            print("No Event ID entered for event display.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())