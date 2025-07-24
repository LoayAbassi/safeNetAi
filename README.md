# Fraud Detection System – Microservices + Frontend MVP

## Project Structure

project/
├── frontend/ # React app: login, dashboard, transactions
└── backend/
├── user_service/ # Django REST API: auth, registration, JWT
├── transaction_service/ # Receive & store transactions
├── rules_service/ # Simple fraud detection rules
├── ai_service/ # Dummy ML fraud scoring
├── alert_service/ # Send email alerts on fraud
├── dashboard_service/ # Admin dashboard data (alerts, logs)
├── log_service/ # Store audit logs & events
└── bank_simulator_service/ # Generate & send fake transactions

yaml
Copy
Edit

---

## Backend Microservices

- **user_service:** Register/login users, return JWT tokens, user profiles, role management  
- **transaction_service:** Receive transactions, store them, call rules and AI services for fraud checks  
- **rules_service:** Run simple fraud detection rules, return fraud flag and triggered rules  
- **ai_service:** Return dummy ML fraud probability score  
- **alert_service:** Send fraud alert emails (console backend in dev)  
- **dashboard_service:** Provide data for frontend dashboard (alerts, logs, transactions)  
- **log_service:** Store logs of fraud checks and events, provide log retrieval APIs  
- **bank_simulator_service:** Generate fake transactions and send to transaction_service for testing  

---

## Frontend

- Login/Register pages calling user_service  
- Dashboard showing alerts, logs, and transactions from dashboard_service  
- Manual transaction submission calling transaction_service  
- Manage JWT tokens, Axios for API calls  
- Use React Router for navigation  
- Basic styling with Bootstrap or Tailwind  

---

## Communication & Notes

- Backend services communicate via REST calls using Python `requests`  
- Use JWT for authentication across services and frontend  
- Keep code modular, clean, and RESTful  
- Start with user_service and frontend login page, then build others stepwise  
- Use SQLite for fast prototyping  
- No Docker needed now  

---
