
## Instructions

### Backend
```powershell
flask --debug run
```

### Celery
```powershell
celery -A tradie_match.celery_worker worker --loglevel=info --pool=solo
celery -A tradie_match.celery_worker beat --loglevel=info
```

### Frontend
```powershell
npm run serve
```

### Redis on WSL
```bash
redis-cli
```

### Email Testing
Run MailHog locally and open http://localhost:8025
