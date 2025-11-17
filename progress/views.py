from django.db.models import Count, Q
from django.http import JsonResponse
from users.models import UserTest,TestQuestion, UserTest, UserFlashcard, Topic
from django.views.decorators.csrf import csrf_exempt
from users.views import jwt_required
from django.utils import timezone
from datetime import timedelta, date, datetime



# Biểu đồ
@csrf_exempt
@jwt_required
def get_progress(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET required"}, status=400)
    
    user = request.user.customer
    today = timezone.now().date()

    # Tháng hiện tại
    month_start = today.replace(day=1)

    # Tìm tháng tiếp theo
    if month_start.month == 12:
        next_month = month_start.replace(year=month_start.year + 1, month=1)
    else:
        next_month = month_start.replace(month=month_start.month + 1)

    month_end = next_month - timedelta(days=1)

    # Lấy tất cả câu user làm trong tháng
    tests = UserTest.objects.filter(
        user=user,
        attempted_at__date__range=[month_start, month_end]
    ).select_related("test", "test__flashcard", "test__flashcard__topic")

    # Lấy flashcard đã học trong tháng
    flashcards = UserFlashcard.objects.filter(
        user=user,
        learned=True,
        last_reviewed__date__range=[month_start, month_end]
    )

    # Kết quả theo tuần ISO
    weekly_stats = {}

    def get_week_label(date_obj):
        year, week, _ = date_obj.isocalendar()
        return f"Year: {year} - Week{week}"

    # ============================
    # 🔥 Đếm số BÀI TEST theo tuần
    # ============================
    tests_per_week = {}

    for t in tests:
        week_label = get_week_label(t.attempted_at.date())
        topic_id = t.test.flashcard.topic.id

        if week_label not in tests_per_week:
            tests_per_week[week_label] = set()

        # thêm topic → unique → 1 topic = 1 bài test
        tests_per_week[week_label].add(topic_id)

    # ============================
    # 🔥 Đếm FLASHCARD theo tuần
    # ============================
    flashcard_per_week = {}

    for f in flashcards:
        if f.last_reviewed:
            week_label = get_week_label(f.last_reviewed.date())
            flashcard_per_week[week_label] = flashcard_per_week.get(week_label, 0) + 1

    # Ghép 2 loại dữ liệu lại
    all_weeks = set(tests_per_week.keys()) | set(flashcard_per_week.keys())

    for w in all_weeks:
        weekly_stats[w] = {
            "test": len(tests_per_week.get(w, [])),          # số topic làm trong tuần
            "flashcard": flashcard_per_week.get(w, 0)       # số flashcard learned
        }

    return JsonResponse({
        "month": today.month,
        "weeks": weekly_stats
    })

#  Top 3 câu sai nhiều nhất
@csrf_exempt
@jwt_required
def get_top_wrong_questions(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET required"}, status=400)
    
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



@csrf_exempt
@jwt_required
def overview_progress(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET required"}, status=400)
    
    user = request.user.customer

    # 1. Flashcard đã học
    flashcard_learned = UserFlashcard.objects.filter(
        user=user,
        learned=True
    ).count()

    # 2. Chủ đề đã hoàn thành
    # (topic có ít nhất 1 câu thuộc mọi flashcard trong topic)
    # Topic mà user đã làm test
    tested_topics = set(
        UserTest.objects.filter(user=user)
        .values_list("test__flashcard__topic_id", flat=True)
    )

    completed_topics = len(tested_topics)

    # 3. Điểm trung bình
    tests = UserTest.objects.filter(user=user)
    total = tests.count()
    correct = tests.filter(is_correct=True).count()

    avg_score = (correct / total) if total > 0 else 0

    # 4. Streak - ngày liên tiếp
    # Lấy danh sách ngày user có hoạt động
    activity_dates = sorted(
        set(
            list(
                UserTest.objects.filter(user=user)
                .values_list("attempted_at__date", flat=True)
            ) +
            list(
                UserFlashcard.objects.filter(user=user, learned=True)
                .values_list("last_reviewed__date", flat=True)
            )
        ),
        reverse=True
    )

    streak = 0
    today = timezone.now().date()

    # Đếm ngày liên tiếp
    for i, d in enumerate(activity_dates):
        if i == 0:
            if d == today or d == today - timedelta(days=1):
                streak += 1
            else:
                break
        else:
            prev = activity_dates[i - 1]
            if prev - d == timedelta(days=1):
                streak += 1
            else:
                break

    return JsonResponse({
        "flashcard_learned": flashcard_learned,
        "completed_topics": completed_topics,
        "avg_score": round(avg_score, 2),
        "streak": streak
    })