from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from users.models import Topic, Flashcard, TestQuestion, UserTest
from django.db.models import Count
import json

#  danh sách các topic trong giao diện chủ đề 
@csrf_exempt
def get_all_topics(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET required"}, status=400)

    topics = (
        Topic.objects
        .annotate(flashcard_count=Count("flashcards"))
        .values("id", "title", "flashcard_count")
    )

    return JsonResponse(list(topics), safe=False, status=200)




#  Thông tin của 1 Flashcard trong 1 topic nào đó
@csrf_exempt
def get_topic_flashcards(request, topic_id):
    if request.method != "GET":
        return JsonResponse({"error": "GET required"}, status=400)

    try:
        topic = Topic.objects.get(id=topic_id)
    except Topic.DoesNotExist:
        return JsonResponse({"error": "Topic not found"}, status=404)

    flashcards = Flashcard.objects.filter(topic=topic).values(
        "id", "front_text", "back_text", "media"
    )

    data = {
        "topic_id": topic.id,
        "topic_title": topic.title,
        "total_flashcards": flashcards.count(),
        "flashcards": list(flashcards)
    }

    return JsonResponse(data, status=200)



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
            media_url = request.build_absolute_uri(flashcard.media.url)

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
# @login_required
def submit_answer(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    data = json.loads(request.body)
    user = request.user.customer

    test_id = data.get("test_id")
    user_answer = data.get("user_answer")

    # Lấy câu hỏi
    try:
        test = TestQuestion.objects.select_related("flashcard", "flashcard__topic").get(id=test_id)
    except TestQuestion.DoesNotExist:
        return JsonResponse({"error": "Test not found"}, status=404)

    # So sánh đáp án
    is_correct = (user_answer.upper() == test.correct_option.upper())

    # Lưu lại kết quả
    result = UserTest.objects.create(
        user=user,
        test=test,
        user_answer=user_answer,
        is_correct=is_correct
    )

    return JsonResponse({
        "success": True,
        "is_correct": is_correct,
        "correct_option": test.correct_option,
        "flashcard_id": test.flashcard.id,
        "topic_id": test.flashcard.topic.id
    })
