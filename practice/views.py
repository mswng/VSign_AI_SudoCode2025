import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .agent import query_agent
from users.models import Topic, Flashcard 
from django.shortcuts import render #React thì ko cần import cái này

def ask_ai_page(request):
    if request.method == "POST":
        user_input = request.POST.get("message", "")
        user_id = request.user.id  # nếu có user đăng nhập
        ai_reply = query_agent(user_input, user_id)
        return render(request, "chatbot.html", {"response": ai_reply, "user_input": user_input})
    
    return render(request, "chatbot.html")


# nếu gọi API cho giao diện dùng React
# def ask_ai_api(request):
#     if request.method == "POST":
#         user_input = request.POST.get("message", "")
#         user_id = request.user.id
#         ai_reply = query_agent(user_input, user_id)
#         return JsonResponse({"response": ai_reply})
#     return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def vocab_topics_api(request):
    """
    Trả về danh sách topics và flashcards để frontend dùng.
    """
    if request.method == "GET":
        topics = list(Topic.objects.values("id", "title"))
        flashcards = list(Flashcard.objects.values("id", "front_text", "back_text", "topic_id"))
        return JsonResponse({"topics": topics, "flashcards": flashcards})
    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def chatbot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query', '')
            user_id = request.user.id if request.user.is_authenticated else None

            # Lấy danh sách vocab + topics mới nhất từ DB
            topics_list = list(Topic.objects.values_list("title", flat=True))
            flashcards_list = list(Flashcard.objects.values_list("front_text", flat=True))
            vocab_list = ", ".join(flashcards_list)
            topics = ", ".join(topics_list)

            reply = query_agent(
                user_id=user_id,
                learner_input=query,
                vocab_list=vocab_list,
                topics=topics
            )
            return JsonResponse({'answer': reply})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


def chat_ai(request):
    if not request.user.is_authenticated:
        return JsonResponse({"reply": "⚠️ Bạn cần đăng nhập để học với SignTutor!"})
    message = request.GET.get("msg", "")
    if not message:
        return JsonResponse({"reply": "Hãy nhập câu hỏi hoặc ký hiệu bạn muốn học!"})

    reply = query_agent(user_id=request.user.id, learner_input=message)
    return JsonResponse({"reply": reply})
