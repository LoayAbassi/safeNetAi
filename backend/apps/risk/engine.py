from math import radians, sin, cos, asin, sqrt

def haversine_km(lat1, lon1, lat2, lon2):
    if None in [lat1, lon1, lat2, lon2]:
        return 0
    R = 6371.0
    dlat = radians(lat2-lat1); dlon = radians(lon2-lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return 2*R*asin(sqrt(a))

def z_amount(amount, avg, std):
    std = std if std and std>0 else 1.0
    return (float(amount) - float(avg)) / float(std)

def evaluate(tx, profile, thresholds, recent_count=0, new_device=False, ip_change=False):
    T = thresholds
    signals, reasons = {}, []
    # geo signal
    dist = haversine_km(tx.get("lat"), tx.get("lng"), profile.get("last_known_lat"), profile.get("last_known_lng"))
    if dist > T.get("MAX_GEO_KM", 100):
        signals["geo_far"] = 30; reasons.append(f"geo_far:{dist:.1f}km")
    # amount outlier
    z = abs(z_amount(tx["amount"], profile.get("avg_amount",0), profile.get("std_amount",1)))
    if z > T.get("Z_AMOUNT", 2.5):
        signals["amount_outlier"] = 40; reasons.append(f"amount_outlier:z={z:.2f}")
    # velocity (placeholder)
    if recent_count > T.get("MAX_TX_PER_HOUR", 5):
        signals["velocity"] = 15; reasons.append("velocity")
    # device/ip
    if new_device or ip_change:
        signals["new_device_ip"] = 20; reasons.append("new_device_ip")
    score = min(100, sum(signals.values()))
    decision = "ALLOW"
    if score >= T.get("RISK_CHALLENGE", 50) and score < T.get("RISK_BLOCK", 80):
        decision = "STEP_UP"
    elif score >= T.get("RISK_BLOCK", 80):
        decision = "BLOCK"
    return {"score": score, "reasons": reasons, "decision": decision, "signals": signals}
