from django.db.models import Count, Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from users.models import UserTest,TestQuestion, UserTest

# Biểu đồ tiến độ
@login_required
def get_progress(request):
    user = request.user.customer

    stats = UserTest.objects.filter(user=user).aggregate(
        total=Count("id"),
        correct=Count("id", filter=Q(is_correct=True)),
        wrong=Count("id", filter=Q(is_correct=False))
    )

    return JsonResponse(stats)


#  Top 3 câu sai nhiều nhất
# @login_required
def get_top_wrong_questions(request):
    user = request.user.customer

    wrong_tests = (
        UserTest.objects.filter(user=user, is_correct=False)
        .values("test_id")
        .annotate(wrong_count=Count("test_id"))
        .order_by("-wrong_count")[:3]
    )

    result = []
    for item in wrong_tests:
        test = TestQuestion.objects.select_related("flashcard", "flashcard__topic").get(id=item["test_id"])
        flashcard = test.flashcard

        result.append({
            "test_id": test.id,
            "wrong_count": item["wrong_count"],

            # Thông tin flashcard & topic
            "flashcard_id": flashcard.id,
            "topic_id": flashcard.topic.id,
            "topic_title": flashcard.topic.title,

            # Media (image/video)
            "media_url": request.build_absolute_uri(flashcard.media.url),

            # Câu hỏi
            "question": test.question,
            "correct_option": test.correct_option
        })

    return JsonResponse(result, safe=False)
