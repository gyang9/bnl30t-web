function openTab(tabName) {
    const contents = document.querySelectorAll('.tab-content');
    contents.forEach(content => content.classList.remove('active'));

    const buttons = document.querySelectorAll('.tab-btn');
    buttons.forEach(btn => btn.classList.remove('active'));

    document.getElementById(tabName).classList.add('active');
    event.currentTarget.classList.add('active');
}

async function loadFile() {
    const filePath = document.getElementById('file-path').value;
    const statusSpan = document.getElementById('file-status');
    const rangeSpan = document.getElementById('event-range');

    statusSpan.textContent = "Loading...";
    statusSpan.style.color = "orange";

    try {
        const response = await fetch('/load_file', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ file_path: filePath })
        });

        const data = await response.json();

        if (data.success) {
            statusSpan.textContent = `Loaded: ${data.filename}`;
            statusSpan.style.color = "#27ae60";
            rangeSpan.textContent = ` (Events: ${data.min_id} - ${data.max_id})`;
        } else {
            statusSpan.textContent = `Error: ${data.error}`;
            statusSpan.style.color = "#c0392b";
        }
    } catch (e) {
        statusSpan.textContent = `Error: ${e.message}`;
        statusSpan.style.color = "#c0392b";
    }
}

async function uploadFile() {
    const fileInput = document.getElementById('upload-file');
    const statusSpan = document.getElementById('file-status');

    if (fileInput.files.length === 0) {
        alert("Please select a file to upload.");
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    statusSpan.textContent = "Uploading...";
    statusSpan.style.color = "orange";

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            let errorMsg = `Server Error: ${response.status} ${response.statusText}`;
            if (response.status === 413) {
                errorMsg = "File too large (Limit is 500MB, but Render Free Tier may fail earlier).";
            } else if (response.status === 504) {
                errorMsg = "Upload timed out (Render limit is ~100s). Try a smaller file or faster connection.";
            } else if (response.status === 502) {
                errorMsg = "Server unavailable (likely out of memory). Try a smaller file.";
            }
            throw new Error(errorMsg);
        }

        const data = await response.json();

        if (data.success) {
            document.getElementById('file-path').value = data.filepath;
            loadFile(); // Auto-load after upload
        } else {
            statusSpan.textContent = `Upload Error: ${data.error}`;
            statusSpan.style.color = "#c0392b";
        }
    } catch (e) {
        console.error(e);
        statusSpan.textContent = `Upload Error: ${e.message}`;
        statusSpan.style.color = "#c0392b";
    }
}

async function generateHistogram(title) {
    const channels = document.getElementById('hist-channels').value;
    const trigger = document.getElementById('hist-trigger').value;
    const container = document.getElementById('hist-plot');

    container.innerHTML = "Generating...";

    try {
        const response = await fetch('/histogram', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ channels, trigger, title })
        });

        const data = await response.json();

        if (data.success) {
            container.innerHTML = `<img src="data:image/png;base64,${data.image}" alt="Histogram">`;
        } else {
            container.innerHTML = `Error: ${data.error}`;
        }
    } catch (e) {
        container.innerHTML = `Error: ${e.message}`;
    }
}

async function generateEventDisplay() {
    const eventId = document.getElementById('ed-event-id').value;
    const container = document.getElementById('ed-plot');

    container.innerHTML = "Generating...";

    try {
        const response = await fetch('/event_display', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ event_id: eventId })
        });

        const data = await response.json();

        if (data.success) {
            container.innerHTML = `<img src="data:image/png;base64,${data.image}" alt="Event Display">`;
        } else {
            container.innerHTML = `Error: ${data.error}`;
        }
    } catch (e) {
        container.innerHTML = `Error: ${e.message}`;
    }
}

async function generateWaveform() {
    const eventId = document.getElementById('wf-event-id').value;
    const container = document.getElementById('wf-plot');

    container.innerHTML = "Generating...";

    try {
        const response = await fetch('/waveform', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ event_id: eventId })
        });

        const data = await response.json();

        if (data.success) {
            container.innerHTML = `<img src="data:image/png;base64,${data.image}" alt="Waveform">`;
        } else {
            container.innerHTML = `Error: ${data.error}`;
        }
    } catch (e) {
        container.innerHTML = `Error: ${e.message}`;
    }
}

async function generatePersistence() {
    const channels = document.getElementById('hist-channels').value;
    const trigger = document.getElementById('hist-trigger').value;
    const plotContainer = document.getElementById('histogram-plot');

    plotContainer.innerHTML = '<p>Generating persistence plot...</p>';

    try {
        const response = await fetch('/persistence', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                channels: channels,
                trigger: trigger,
                title: 'Persistence Plot'
            })
        });

        const data = await response.json();

        if (data.success) {
            plotContainer.innerHTML = `<img src="data:image/png;base64,${data.image}" alt="Persistence Plot">`;
        } else {
            plotContainer.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
        }
    } catch (e) {
        console.error(e);
        plotContainer.innerHTML = `<p style="color: red;">Error: ${e.message}</p>`;
    }
}
