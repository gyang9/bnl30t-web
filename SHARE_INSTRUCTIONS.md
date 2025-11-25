# How to Share and Run BNL1T Web App

## Option 1: Share the Source Code (Downloadable)

1.  **Send the Zip File**: Share the `bnl1t_web_app.zip` file with the other person.
2.  **They Unzip it**:
    ```bash
    unzip bnl1t_web_app.zip
    cd bnl1t_web
    ```
3.  **They Run it**:
    ```bash
    ./run.sh
    ```
    (They need Python 3 installed).

## Option 2: Share on Local Network

If the other person is on the same WiFi/Network as you:
1.  Find your computer's IP address:
    Run `hostname -I` in your terminal.
2.  Give them the URL:
    `http://<YOUR_IP_ADDRESS>:5001`
    (e.g., `http://192.168.1.50:5001`)

## Option 3: Public Internet (ngrok)

To share with someone outside your network using ngrok:

1.  **Install ngrok**:
    -   Go to [ngrok.com](https://ngrok.com) and sign up (it's free).
    -   Download the Linux version.
    -   Unzip it: `tar xvzf ngrok-v3-stable-linux-amd64.tgz`
    -   Connect your account: `./ngrok config add-authtoken <YOUR_TOKEN>` (from their dashboard).

2.  **Start the Tunnel**:
    ```bash
    ./ngrok http 5001
    ```

3.  **Share the Link**:
    -   ngrok will show a URL like `https://8f32-130-199-23-193.ngrok-free.app`.
    -   Send this link to the other person.

## Option 4: Public Internet (Localtunnel - Recommended)

This is free and allows you to pick a **custom name** so the link stays the same even after rebooting.

1.  Run this command:
    ```bash
    npx localtunnel --port 5001 --subdomain my-bnl1t-app
    ```
    *(Replace `my-bnl1t-app` with any unique name you want)*

2.  Your link will be: `https://my-bnl1t-app.loca.lt`
3.  **To keep the same link after rebooting**: Just run the exact same command again.

## Option 5: Public Internet (No Install - SSH)

If you don't want to install ngrok, you can use `localhost.run` (requires SSH):

1.  Run this command in your terminal:
    ```bash
    ssh -R 80:localhost:5001 nokey@localhost.run
    ```
2.  It will print a URL (e.g., `https://random-name.localhost.run`).
3.  Share that URL.
