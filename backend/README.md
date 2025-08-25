# Backend Quickstart
1) python -m venv .venv && source .venv/bin/activate
2) pip install -r requirements.txt
3) python manage.py makemigrations apps.users apps.risk && python manage.py migrate
4) python manage.py createsuperuser
5) python manage.py runserver

Seed thresholds in Django shell:
```
from apps.risk.models import Threshold
defaults = {'MAX_GEO_KM': 100,'Z_AMOUNT': 2.5,'MAX_TX_PER_HOUR': 5,'RISK_ALLOW': 30,'RISK_CHALLENGE': 50,'RISK_BLOCK': 80}
for k,v in defaults.items(): Threshold.objects.get_or_create(key=k, defaults={'value':v})
```
