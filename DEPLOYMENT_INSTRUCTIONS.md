# How to Deploy to the Cloud (Render.com)

This will put your app on the public internet permanently (e.g., `https://bnl30t-display.onrender.com`).

## Prerequisites
1.  A **GitHub** account.
2.  A **Render** account (sign up at [render.com](https://render.com)).

## Step 1: Upload Code to GitHub

1.  **Create a New Repository** on GitHub (name it `bnl1t-web` or `bnl30t-web`).
2.  **Push your code** (Run these commands in your terminal):
    ```bash
    cd /home/guang/.gemini/antigravity/scratch/bnl1t_web
    git init
    git add .
    git commit -m "Add render.yaml and fix config path"
    git branch -M main
    # Replace URL below with YOUR GitHub repository URL
    git remote add origin https://github.com/YOUR_USERNAME/bnl1t-web.git
    git push -u origin main
    ```

## Step 2: Deploy on Render (Automated)

1.  Go to your **Render Dashboard**.
2.  Click **New +** -> **Blueprint**.
3.  Connect your GitHub account and select the repository you just pushed.
4.  Render will automatically detect `render.yaml` and configure everything (Python version, build command, etc.).
5.  Click **Apply** or **Create Service**.

## Step 3: Use the App

1.  Wait a few minutes for the build to finish.
2.  Render will give you a URL.
3.  **Important**: The app will start EMPTY. You must use the **"Upload & Load"** button to upload your ROOT file to analyze it.
