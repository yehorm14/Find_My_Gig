# Find My Gig - Team 1E

Welcome to the Find My Gig repository. The objective of our application is to give musicians and bands a place to connect, collaborate, and fill open gig opportunities near them.

## Tech Stack
* **Backend:** Django 4.2 LTS (Python 3.11)
* **Frontend:** HTML, CSS, JavaScript (AJAX)
* **Database:** SQLite (Default Django)
* **APIs:** Google Maps API

---

## Local Setup Instructions (VS Code)

To start working on the project, follow these steps exactly. Make sure you have Python 3.11 and VS Code installed on your computer first.

### 1. Clone the Repository
Open your VS Code terminal (Command Prompt) and run:
```bash
git clone [https://github.com/YOUR-USERNAME/Find_My_Gig.git](https://github.com/YOUR-USERNAME/Find_My_Gig.git)
cd Find_My_Gig
```

### 2. Set Up Your Virtual Environment
We use a virtual environment to make sure everyone is using the exact same versions of our packages and to avoid conflicts.
* **Mac/Linux:** `python3 -m venv gig_env`
* **Windows:** `python -m venv gig_env`

### 3. Activate the Virtual Environment
You must do this every time you open the project in VS Code.
* **Mac/Linux:** `source gig_env/bin/activate`
* **Windows:** `gig_env\Scripts\activate`
*(You will know it worked if you see `(gig_env)` at the start of your terminal line).*

### 4. Install the Dependencies
Now, install our specific version of Django and our other packages:
```bash
pip install -r requirements.txt
```

### 5. Run the Server
To test that everything is working, start up the local development server:
```bash
python manage.py runserver
```
*(Open your browser and go to http://127.0.0.1:8000/ to see the site).*

---

## 🛠️ Our Team's Git Workflow

Because our `main` branch is mechanically protected, **nobody is allowed to push directly to main.** All work must be done on personal feature branches and approved via Pull Requests (PRs). 

Please follow these exact steps to ensure we don't overwrite each other's code or create massive merge conflicts!

### 1. Starting a New Task
Never create a new branch from an outdated blueprint. Always update your local `main` first.
```bash
# 1. Go to your local main branch
git checkout main

# 2. Download the absolute newest code from GitHub
git pull origin main

# 3. Create your new task branch and switch to it
git checkout -b your-descriptive-branch-name
```

### 2. Saving and Pushing Your Work
Commit often! Once your feature is working locally, push it up to GitHub.
```bash
# 1. Stage all your changed files
git add .

# 2. Save them with a clear, descriptive message
git commit -m "feat: Describe what you added or fixed here"

# 3. Push your branch to GitHub (use -u ONLY the very first time you push a new branch)
git push -u origin your-descriptive-branch-name
```

### 3. ⚠️ IMPORTANT: Updating an Active Branch
If a teammate just merged their code into `main`, your active feature branch is now out of date! **You MUST pull their new code into your workspace before you open a Pull Request.**

```bash
# 1. Save whatever you are currently working on
git add .
git commit -m "chore: save progress before pulling updated main"

# 2. Switch to your local main branch
git checkout main

# 3. Download the new code from GitHub
git pull origin main

# 4. Switch back to your active feature branch
git checkout your-descriptive-branch-name

# 5. Inject the newly updated main code into your workspace
git merge main
```
*(Note: If step 5 causes a Merge Conflict, open the conflicting files in your VS Code editor, choose which code to keep, save the file, and run `git commit -am "Resolved merge conflicts"`).*

### 4. Opening a Pull Request
Once your code is pushed and your branch is fully up-to-date with `main`:
1. Go to our repository on GitHub.
2. Click the green **Compare & pull request** button next to your branch.
3. Leave a brief description of what you built.
4. Ask a teammate to review and approve your code. Once approved, click **Merge**!

---

## Acknowledgements & External Sources
* **Mapping:** Google Maps API was used for location routing and gig display.
* **Styling:** [Insert CSS Framework used, e.g., Bootstrap]
* **Icons/Images:** [Insert any external icon libraries or image sources used]
* **Other:** [Insert any other external code snippets or libraries used during development]
