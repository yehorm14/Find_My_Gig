# Find My Gig - Team 1E

Welcome to the Find My Gig repository. The objective of our application is to give musicians and bands a place to connect, collaborate, and fill open gig opportunities near them.

## Tech Stack
* Backend: Django 4.2 LTS (Python 3.11)
* Frontend: HTML, CSS, JavaScript (AJAX)
* Database: SQLite (Default Django)
* APIs: Google Maps API

---

## Local Setup Instructions (VS Code)

To start working on the project, follow these steps exactly. Make sure you have Python 3.11 and VS Code installed on your computer first.

### 1. Clone the Repository
Open your VS Code terminal (Command Prompt) and run:
git clone https://github.com/YOUR-USERNAME/Find_My_Gig.git
cd Find_My_Gig

### 2. Set Up Your Virtual Environment
We use a virtual environment to make sure everyone is using the exact same versions of our packages and to avoid conflicts.
* Mac/Linux: python3 -m venv gig_env
* Windows: python -m venv gig_env

### 3. Activate the Virtual Environment
You must do this every time you open the project in VS Code.
* Mac/Linux: source gig_env/bin/activate
* Windows: gig_env\Scripts\activate
(You will know it worked if you see (gig_env) at the start of your terminal line).

### 4. Install the Dependencies
Now, install our specific version of Django and our other packages:
pip install -r requirements.txt

### 5. Run the Server
To test that everything is working, start up the local development server:
python manage.py runserver
(Open your browser and go to http://127.0.0.1:8000/ to see the site).

---

## Git Workflow

Our main branch is mechanically protected. You cannot push directly to main. 

### How to Build a Feature

1. Create a fresh branch for your task:
Make sure your branch name describes what you are working on (e.g., ross-frontend-nav).
git checkout -b your-branch-name

2. Write your code and save your progress:
git add .
git commit -m "Describe what you added or fixed here"

3. Push your branch to GitHub:
git push -u origin your-branch-name

4. Open a Pull Request (PR):
Go to the repository on GitHub. You will see a green button asking you to "Compare & pull request". Click it, and ask a teammate to review and approve your code before merging it into the main branch.

---

## Acknowledgements & External Sources
* Mapping: Google Maps API was used for location routing and gig display.
* Styling: [Insert CSS Framework used, e.g., Bootstrap]
* Icons/Images: [Insert any external icon libraries or image sources used]
* Other: [Insert any other external code snippets or libraries used during development]
