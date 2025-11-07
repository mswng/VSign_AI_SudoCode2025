from users.models import AISession, AISessionLog, Customer
from django.utils import timezone


def start_session(user: Customer) -> AISession:
    """
    Tạo session mới khi học viên bắt đầu buổi học.
    """
    session = AISession.objects.create(user=user)
    return session


def log_message(session: AISession, recognized: str, expected: str, correct: bool, explanation: str):
    """
    Ghi lại từng phản hồi AI hoặc hành động học viên.
    """
    AISessionLog.objects.create(
        session=session,
        recognized_symbol=recognized,
        expected_symbol=expected,
        is_correct=correct,
        ai_explanation=explanation,
    )


def end_session(session: AISession, summary: str = None, feedback: str = None):
    """
    Kết thúc session — lưu lại thời gian, nhận xét, và phản hồi học viên.
    """
    session.end_time = timezone.now()
    if summary:
        session.result_summary = summary
    if feedback:
        session.feedback = feedback
    session.save()
