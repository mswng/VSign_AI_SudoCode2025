import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .agent import query_agent
from users.models import Topic, Flashcard 
from .curriculum_agent import CurriculumAgent
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

from .curriculum_agent import CurriculumAgent

@csrf_exempt
def curriculum_profile_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Bạn cần đăng nhập để dùng chức năng này."}, status=403)

    agent = CurriculumAgent(user_id=request.user.id)
    
    # --- Lấy profile ---
    profile = agent.get_profile()
    
    # --- Lấy flashcards cần ôn tập ---
    suggested_review = agent.suggest_review(top_n=5)
    
    # --- Lấy trạng thái flashcards ---
    status = agent.get_flashcards_status()
    
    # --- Tạo prompt cho LLM ---
    llm_prompt = agent.create_llm_prompt(top_n=5)
    
    return JsonResponse({
        "profile": profile,
        "suggested_review": suggested_review,
        "flashcards_status": status,
        "llm_prompt": llm_prompt
    })

@csrf_exempt
def test_session_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = request.user.id if request.user.is_authenticated else None
            action = data.get("action")
            agent = CurriculumAgent(user_id=user_id)

            if action == "start":
                questions = agent.generate_check_questions(num_questions=10)
                request.session["test_questions"] = questions
                request.session["current_index"] = 0
                request.session["wrong_signs"] = []
                return JsonResponse({
                    "question": questions[0],
                    "remaining": len(questions) - 1
                })
            
            elif action == "answer":
                answer = data.get("answer", "").strip()
                questions = request.session.get("test_questions", [])
                idx = request.session.get("current_index", 0)
                wrong_signs = request.session.get("wrong_signs", [])

                if idx >= len(questions):
                    # Hoàn tất, sinh bài tập gợi ý
                    practice_tasks = agent.generate_practice_tasks(wrong_signs)
                    return JsonResponse({
                        "done": True,
                        "message": "🎉 Bạn đã hoàn thành bài kiểm tra!",
                        "practice_tasks": practice_tasks
                    })
                current_q = questions[idx]
                correct_answer = current_q.split("'")[1]  # Lấy ký hiệu
                correct = agent.check_answer(answer, correct_answer)

                if correct:
                    idx += 1
                    request.session["current_index"] = idx
                    if idx < len(questions):
                        return JsonResponse({
                            "correct": True,
                            "next_question": questions[idx],
                            "remaining": len(questions) - idx - 1
                        })
                    else:
                        # ✅ Sinh practice_tasks khi hoàn thành hết
                        wrong_signs = request.session.get("wrong_signs", [])
                        practice_tasks = agent.generate_practice_tasks(wrong_signs)
                        return JsonResponse({
                            "done": True,
                            "message": "✅ Hoàn thành tất cả câu hỏi!",
                            "practice_tasks": practice_tasks
                        })

                else:
                    wrong_signs.append(correct_answer)
                    request.session["wrong_signs"] = wrong_signs
                    return JsonResponse({"correct": False, "message": f"Sai rồi, hãy ôn lại ký hiệu '{correct_answer}'!"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid method"}, status=405)