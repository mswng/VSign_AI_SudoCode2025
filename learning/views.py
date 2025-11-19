from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from users.views import jwt_required
from users.models import Topic, Flashcard, TestQuestion, UserTest, UserFlashcard, Customer
from django.db.models import Count, Q, Sum
import json
from django.utils import timezone

#  danh sách các topic trong giao diện chủ đề 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from users.models import Topic, Flashcard
from users.views import jwt_required   # nếu bạn muốn yêu cầu đăng nhập

#  LẤY DANH SÁCH TOPIC
@csrf_exempt
def get_all_topics(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET required"}, status=400)

    topics = (
        Topic.objects
        .annotate(flashcard_count=Count("flashcards"))
        .values("id", "title", "description", "flashcard_count")
    )

    return JsonResponse(list(topics), safe=False, status=200)



# LẤY TOÀN BỘ FLASHCARD CỦA 1 TOPIC
@csrf_exempt
def get_topic_flashcards(request, topic_id):
    if request.method != "GET":
        return JsonResponse({"error": "GET required"}, status=400)

    try:
        topic = Topic.objects.get(id=topic_id)
    except Topic.DoesNotExist:
        return JsonResponse({"error": "Topic not found"}, status=404)

    flashcards = Flashcard.objects.filter(topic=topic).values(
        "id",
        "front_text",
        "back_text",
        "media",        # nếu dùng URLField → trả URL nguyên bản
    )

    data = {
        "topic_id": topic.id,
        "topic_title": topic.title,
        "topic_description": topic.description,
        "total_flashcards": flashcards.count(),
        "flashcards": list(flashcards)  # Frontend tự xử lý next/prev
    }

    return JsonResponse(data, safe=False, status=200)




# danh sách câu hỏi của một topic 
@csrf_exempt
def get_topic_test_questions(request, topic_id):
    if request.method != "GET":
        return JsonResponse({"error": "GET required"}, status=400)

    # 1. Lấy topic
    try:
        topic = Topic.objects.get(id=topic_id)
    except Topic.DoesNotExist:
        return JsonResponse({"error": "Topic not found"}, status=404)

    # 2. Lấy toàn bộ câu hỏi thuộc các flashcard của topic này
    tests = (
        TestQuestion.objects
        .filter(flashcard__topic=topic)
        .select_related("flashcard")
    )

    questions_data = []

    for t in tests:
        flashcard = t.flashcard

        # Lấy URL đầy đủ của file media nếu có
        media_url = None
        if flashcard.media:
            # build_absolute_uri -> trả full URL: http://localhost:8000/media/...
            media_url = request.build_absolute_uri(flashcard.media) if flashcard.media else None

        questions_data.append({
            "test_id": t.id,
            "flashcard_id": flashcard.id,
            "topic_id": topic.id,
            "topic_title": topic.title,

            # Thông tin câu hỏi
            "question": t.question,
            "options": {
                "A": t.option_a,
                "B": t.option_b,
                "C": t.option_c,
                "D": t.option_d,
            },
            "correct_option": t.correct_option,   # tạm thời cho frontend thấy, sau có thể ẩn đi

            # Thông tin flashcard liên quan (nếu cần hiển thị thêm)
            "media_url": media_url,
            "front_text": flashcard.front_text,
            "back_text": flashcard.back_text,
        })

    return JsonResponse({
        "topic_id": topic.id,
        "topic_title": topic.title,
        "total_questions": len(questions_data),
        "questions": questions_data,
    }, status=200)


@csrf_exempt
@jwt_required
def submit_answer(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    try:
        data = json.loads(request.body)
        question_id = data.get("question_id")
        user_answer = data.get("answer")

        if not question_id or not user_answer:
            return JsonResponse({"error": "Thiếu question_id hoặc answer"}, status=400)

        user = request.user.customer
        question = TestQuestion.objects.get(id=question_id)

        is_correct = (user_answer.upper() == question.correct_option.upper())

        # Chỉ lưu 1 record cho câu hỏi
        UserTest.objects.create(
            user=user,
            test=question,
            user_answer=user_answer.upper(),
            is_correct=is_correct
        )

        return JsonResponse({
            "success": True,
            "is_correct": is_correct,
            "correct_option": question.correct_option,
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@jwt_required
def finish_quiz(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    try:
        data = json.loads(request.body)
        topic_id = data.get("topic_id")
        results = data.get("results")  # list flashcard results

        if not topic_id or results is None:
            return JsonResponse({"error": "Missing data"}, status=400)

        user = request.user.customer

        total_correct = 0
        total_wrong = 0

        for item in results:
            flashcard_id = item["flashcard_id"]
            correct = item["correct"]
            wrong = item["wrong"]

            total_correct += correct
            total_wrong += wrong

            flashcard = Flashcard.objects.get(id=flashcard_id)

            # Tạo bản ghi mới mỗi lần làm quiz
            UserFlashcard.objects.create(
                user=user,
                flashcard=flashcard,
                correct_count=correct,
                wrong_count=wrong,
                learned = (correct > 0),
                last_reviewed=timezone.now()
            )

        return JsonResponse({
            "success": True,
            "total_correct": total_correct,
            "total_wrong": total_wrong,
            "correct_rate": (
                (total_correct / (total_correct + total_wrong)) * 100
                if (total_correct + total_wrong) else 0
            )
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
