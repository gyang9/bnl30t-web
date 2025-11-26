# Alternative: Deploy to PythonAnywhere (Easier)

Render is having persistent cache issues. Let's try **PythonAnywhere** instead - it's simpler and free.

## Steps:

1. **Sign up** at https://www.pythonanywhere.com (free account)

2. **Upload your code**:
   - Go to **Files** tab
   - Click "Upload a file" and upload your entire `bnl1t_web` folder as a zip
   - Or use **Git**: Go to **Consoles** → **Bash** and run:
     ```bash
     git clone https://github.com/gyang9/bnl30t-web.git
     cd bnl30t-web
     ```

3. **Install dependencies**:
   - In the Bash console:
     ```bash
     pip3.9 install --user -r requirements.txt
     ```

4. **Set up Web App**:
   - Go to **Web** tab
   - Click "Add a new web app"
   - Choose **Flask**
   - Python version: **3.9**
   - Path to your Flask app: `/home/YOUR_USERNAME/bnl30t-web/app.py`
   - Click through the setup

5. **Configure**:
   - In the Web tab, find "WSGI configuration file" and click to edit
   - Replace the contents with:
     ```python
     import sys
     path = '/home/YOUR_USERNAME/bnl30t-web'
     if path not in sys.path:
         sys.path.append(path)
     
     from app import app as application
     ```

6. **Reload** the web app

Your app will be at: `https://YOUR_USERNAME.pythonanywhere.com`

---

## OR: Fix Render by Deleting and Recreating

If you want to stick with Render:
1. Delete the current `bnl30t-display` service
2. Create a new one from scratch
3. This will force a completely fresh environment
