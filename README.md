# AI Fraud Detection MVP (Django + React)

## Run backend
```
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations apps.users apps.risk && python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Seed thresholds in Django shell if empty (see backend/README.md).

## Run frontend
```
cd frontend
npm install
npm run dev
```
Login/register first, then create a client user, a profile + account in Django admin (or extend endpoints), and test transfers.
