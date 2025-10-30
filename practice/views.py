from django.shortcuts import render

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .agent import query_agent

def ask_ai_page(request):
    return render(request, "chatbot.html", {
        "page_name": "chatbot"
    })

@csrf_exempt
@require_POST
def ask_ai(request):
    try:
        data = json.loads(request.body)
        query = data.get("query", "")
        if not query:
            return JsonResponse({"error": "Missing 'query' field"}, status=400)

        response = query_agent(query)
        return JsonResponse({"answer": response}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

