from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .fraud_rules import check_rules

@csrf_exempt
def check_transaction(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            result = check_rules(data)
            return JsonResponse(result, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Only POST allowed'}, status=405)
