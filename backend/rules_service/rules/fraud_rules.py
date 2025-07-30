from datetime import datetime

# Mock user trusted locations for MVP
USER_LOCATIONS = {
    1: ['Tunis', 'Sfax'],
    2: ['Paris', 'Lyon']
}

def check_rules(transaction):
    reasons = []

    amount = transaction.get('amount', 0)
    location = transaction.get('location', '')
    user_id = transaction.get('user_id')

    # Rule 1: Amount check
    if amount > 5000:
        reasons.append("High amount")

    # Rule 2: Location check
    trusted_locations = USER_LOCATIONS.get(user_id, [])
    if location not in trusted_locations:
        reasons.append("Unusual location")

    is_fraud = len(reasons) > 0
    return {
        "is_fraud": is_fraud,
        "reasons": reasons
    }
