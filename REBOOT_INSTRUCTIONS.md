# What to do after Rebooting

To bring your web app back online with the **SAME** link, follow these 2 steps:

## Step 1: Start the Web App
1.  Open a terminal.
2.  Run this command:
    ```bash
    /home/guang/.gemini/antigravity/scratch/bnl1t_web/run.sh
    ```
    *Keep this terminal open.*

## Step 2: Start the Public Link
1.  Open a **NEW** terminal window (Ctrl+Shift+T).
2.  Run this command (use the SAME name you chose before):
    ```bash
    cd /home/guang/.gemini/antigravity/scratch/bnl1t_web
    npx localtunnel --port 5001 --subdomain my-bnl1t-app
    ```
    *(Replace `my-bnl1t-app` with your chosen name)*

3.  **Done!** Your link `https://my-bnl1t-app.loca.lt` is back online.
