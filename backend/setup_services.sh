#!/bin/bash

services=(
  user_service
  transaction_service
  rules_service
  ai_service
  alert_service
  dashboard_service
  log_service
  bank_simulator_service
)

for service in "${services[@]}"; do
  echo "Setting up $service..."
  mkdir -p backend/$service
  cd backend/$service
  python3 -m venv venv
  source venv/bin/activate
  pip install django
  django-admin startproject config .
  deactivate
  cd ../../
done

echo "✅ All microservices created with Django & venv!"
