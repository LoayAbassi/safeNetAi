from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count
from .models import Transaction, Account, Threshold, RiskEvent
from .serializers import QuoteSerializer, TransactionSerializer, ThresholdSerializer, AccountSerializer
from .engine import evaluate

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_accounts(request):
    accounts = Account.objects.filter(owner__user=request.user)
    return Response(AccountSerializer(accounts, many=True).data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def quote(request):
    s = QuoteSerializer(data=request.data); s.is_valid(raise_exception=True)
    data = s.validated_data
    acc = get_object_or_404(Account, id=data["account_id"], owner__user=request.user)
    profile = {
        "avg_amount": acc.owner.avg_amount,
        "std_amount": acc.owner.std_amount,
        "last_known_lat": acc.owner.last_known_lat,
        "last_known_lng": acc.owner.last_known_lng,
    }
    T = {t.key: t.value for t in Threshold.objects.all()}
    result = evaluate(data, profile, T)
    return Response({"decision": result["decision"], "risk_score": result["score"], "reasons": result["reasons"]})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initiate(request):
    s = QuoteSerializer(data=request.data); s.is_valid(raise_exception=True)
    data = s.validated_data
    acc = get_object_or_404(Account, id=data["account_id"], owner__user=request.user)
    T = {t.key: t.value for t in Threshold.objects.all()}
    profile = {
        "avg_amount": acc.owner.avg_amount,
        "std_amount": acc.owner.std_amount,
        "last_known_lat": acc.owner.last_known_lat,
        "last_known_lng": acc.owner.last_known_lng,
    }
    result = evaluate(data, profile, T)
    tx = Transaction.objects.create(account=acc, to_iban=data["to_iban"], amount=data["amount"], currency=data["currency"], lat=data.get("lat"), lng=data.get("lng"), device_id=data.get("device_id"), ip=data.get("ip"), status=result["decision"], risk_score=result["score"], decision_reason=result["reasons"])    
    if result["decision"] == "STEP_UP":
        request.session[f"otp:{tx.id}"] = "123456"
        RiskEvent.objects.create(transaction=tx, signals_json=result["signals"], rules_triggered=result["reasons"], decision="STEP_UP")
        return Response({"challenge_id": tx.id, "decision": "STEP_UP"})
    elif result["decision"] == "BLOCK":
        RiskEvent.objects.create(transaction=tx, signals_json=result["signals"], rules_triggered=result["reasons"], decision="BLOCK")
        return Response({"decision": "BLOCK"}, status=403)
    else:
        acc.balance = acc.balance - data["amount"]; acc.save(update_fields=["balance"]) 
        tx.status = "EXECUTED"; tx.save(update_fields=["status"]) 
        return Response(TransactionSerializer(tx).data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def confirm(request):
    tx_id = request.data.get("challenge_id"); otp = request.data.get("otp")
    tx = get_object_or_404(Transaction, id=tx_id, account__owner__user=request.user)
    good = request.session.get(f"otp:{tx.id}") == otp
    if not good:
        return Response({"detail":"Invalid OTP"}, status=400)
    acc = tx.account
    acc.balance = acc.balance - float(tx.amount); acc.save(update_fields=["balance"]) 
    tx.status = "EXECUTED"; tx.save(update_fields=["status"]) 
    return Response(TransactionSerializer(tx).data)
