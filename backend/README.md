# automated MS setup 
for name in user_service transaction_service rules_service ai_service alert_service dashboard_service log_service bank_simulator_service; do
  mkdir $name
  python3 -m venv $name/venv
done


