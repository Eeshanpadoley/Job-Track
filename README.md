# JobTrack — redesigned Django project

A redesigned Job Application Analytics & Skill Intelligence System. It keeps the existing Django app and SQLite database structure, while adding a shared responsive layout and a more polished UI.

## Features
- Login and registration
- Job application create, list, search/filter, edit and delete
- Dashboard KPIs and recent applications
- Pandas-powered analytics and CSV export
- Skill gap comparison based on skills saved in job postings
- Resume library (PDF/DOC/DOCX, max 5 MB)
- Link a resume version to a job application
- Follow-up date reminders and interview/recruiter notes
- Responsive navigation and layout

## Run on Windows
1. Extract this ZIP into a new folder. Do not overwrite your old project folder.
2. Open the extracted `JobTrack_Redesigned` folder in VS Code.
3. Open Terminal in that folder and run:
   ```powershell
   py -m venv venv
   .\venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py check
   python manage.py runserver
   ```
4. Open http://127.0.0.1:8000/

You can also double-click `run_windows.bat` if your Windows execution policy permits it.

## Database note
The supplied `db.sqlite3` is included from the original project and contains 5 job application rows (verified by SQLite integrity check). The new migration adds resume/follow-up/notes support without deleting existing job application rows. Keep a separate backup of your database before using migrations.

## Notes
- Uploaded resumes are stored under `media/resumes/`. Keep this folder backed up.
- The app is intended for local development; configure production security settings before deploying publicly.
