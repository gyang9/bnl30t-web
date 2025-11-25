# How to Deploy to the Cloud (Render.com)

This will put your app on the public internet permanently (e.g., `https://bnl1t-display.onrender.com`).

## Prerequisites
1.  A **GitHub** account.
2.  A **Render** account (sign up at [render.com](https://render.com)).

## Step 1: Upload Code to GitHub

1.  **Create a New Repository** on GitHub (name it `bnl1t-web`).
2.  **Push your code** (Run these commands in your terminal):
    ```bash
    cd /home/guang/.gemini/antigravity/scratch/bnl1t_web
    git init
    git add .
    git commit -m "Initial commit"
    git branch -M main
    # Replace URL below with YOUR GitHub repository URL
    git remote add origin https://github.com/YOUR_USERNAME/bnl1t-web.git
    git push -u origin main
    ```

## Step 2: Deploy on Render

1.  Go to your **Render Dashboard**.
2.  Click **New +** -> **Web Service**.
3.  Select **Build and deploy from a Git repository**.
4.  Connect your GitHub account and select the `bnl1t-web` repository.
5.  **Configure the Service**:
    *   **Name**: `bnl1t-display` (or whatever you want)
    *   **Region**: US East (or closest to you)
    *   **Branch**: `main`
    *   **Runtime**: `Python 3`
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `gunicorn app:app`
    *   **Free Plan**: Select "Free".
6.  Click **Create Web Service**.

## Step 3: Use the App

1.  Wait a few minutes for the build to finish.
2.  Render will give you a URL (e.g., `https://bnl1t-display.onrender.com`).
3.  **Important**: The app will start EMPTY. You must use the **"Upload & Load"** button to upload your ROOT file to analyze it.
