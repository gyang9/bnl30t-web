# Fix Python Version in Render

The `runtime.txt` file is not being recognized. You need to set the Python version manually:

## Steps:

1. Go to https://dashboard.render.com
2. Click on your `bnl30t-display` service
3. Go to **"Environment"** tab (left sidebar)
4. Click **"Add Environment Variable"**
5. Add this variable:
   - **Key**: `PYTHON_VERSION`
   - **Value**: `3.9.18`
6. Click **"Save Changes"**
7. The service will automatically redeploy

## Alternative: Use Docker

If the above doesn't work, Render might require a Dockerfile for Python version control. Let me know if you need help with that approach.
