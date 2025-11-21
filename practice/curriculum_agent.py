from datetime import datetime, timedelta
from users.models import Customer, UserFlashcard, UserTest, Flashcard, Reminder
from .ai_clients import get_ai_model  
import random

class CurriculumAgent:
    def __init__(self, user_id, prefer_model="openrouter"):
        self.user_id = user_id
        self.llm = get_ai_model(prefer_model)  
        try:
            self.user = Customer.objects.get(user__id=user_id)
        except Customer.DoesNotExist:
            self.user = None

    # --- Lấy profile học viên ---
    def get_profile(self):
        flashcards = UserFlashcard.objects.filter(user__user__id=self.user_id)
        tests = UserTest.objects.filter(user__user__id=self.user_id)
        
        profile = {
            "total_flashcards": flashcards.count(),
            "correct_flashcards": flashcards.filter(wrong_count=0).count(),
            "wrong_flashcards": flashcards.filter(wrong_count__gt=0).count(),
            "total_tests": tests.count(),
            "correct_tests": tests.filter(is_correct=True).count(),
            "wrong_tests": tests.filter(is_correct=False).count(),
            "streak_days": self.calculate_streak()
        }
        return profile

    # --- Tính streak học liên tiếp ---
    def calculate_streak(self):
        flashcards = UserFlashcard.objects.filter(
            user__user__id=self.user_id, last_reviewed__isnull=False
        ).order_by('-last_reviewed')
        if not flashcards.exists():
            return 0

        streak = 0
        today = datetime.today().date()
        for fc in flashcards:
            last_day = fc.last_reviewed.date()
            if last_day == today - timedelta(days=streak):
                streak += 1
            else:
                break
        return streak

    # --- Gợi ý ôn tập flashcards theo lỗi ---
    def suggest_review(self, top_n=10):
        wrong_flashcards = UserFlashcard.objects.filter(
            user__user__id=self.user_id, wrong_count__gt=0
        ).order_by('-wrong_count')
        return list(wrong_flashcards[:top_n].values_list('flashcard__front_text', flat=True))

    # --- Sinh câu hỏi kiểm tra dưới dạng hội thoại ---
    def generate_check_questions(self, num_questions=10):
        learned = list(
            UserFlashcard.objects.filter(user__user__id=self.user_id, learned=True)
            .values_list("flashcard__front_text", flat=True)
        )

        if not learned:
            return [
                "Bạn chưa học ký hiệu nào cả. Hãy học một vài flashcard trước rồi quay lại đây nhé!"
            ]

        random.shuffle(learned)
        selected = learned[:num_questions]

        questions = []
        for sign in selected:
            questions.append(
                f"🤖 **Hệ thống:** Này, bạn còn nhớ không? Khi làm ký hiệu **'{sign}'**, bạn sẽ thực hiện như thế nào?\n"
                f"🧑 **Bạn:** (Hãy trả lời mô tả ký hiệu)"
            )
        return questions


    # --- Gợi ý bài tập dựa trên các ký hiệu sai trong session ---
    def generate_practice_tasks(self, wrong_signs=None, top_n=5):
        if wrong_signs:
            base_list = wrong_signs
        else:
            base_list = list(
                UserFlashcard.objects.filter(user_id=self.user_id, wrong_count__gt=0)
                .values_list("flashcard__front_text", flat=True)
            )

        if not base_list:
            return ["🎉 Bạn làm rất tốt! Không có ký hiệu nào cần ôn lại ngay."]

        random.shuffle(base_list)
        selected = base_list[:top_n]

        tasks = [
            f"🔁 Thực hành ký hiệu '{sign}' trước gương, chú ý các ngón tay và hướng bàn tay."
            for sign in selected
        ]
        return tasks

    # --- Tạo prompt cho LLM ---
    def create_llm_prompt(self, top_n=5):
        review_items = self.suggest_review(top_n)
        profile = self.get_profile()
        prompt = f"""
        Bạn là SignTutor, một trợ lý giúp học viên luyện ngôn ngữ ký hiệu Việt Nam.
        Học viên hiện có profile: {profile}.
        Họ cần ôn tập các ký hiệu: {', '.join(review_items)}.

        Hãy tạo:
        1. 5 câu hỏi trắc nghiệm kiểm tra ký hiệu còn yếu.
        2. 5 bài tập thực hành để luyện tay.
        3. 1 đoạn hội thoại tự nhiên, thân thiện, giúp người học luyện tập thêm.
        """
        return prompt.strip()

    # --- Gọi AI sinh bài tập và hội thoại ---
    def generate_llm_content(self, top_n=5):
        """
        Gọi model AI qua LangChain để sinh nội dung học tập.
        """
        prompt = self.create_llm_prompt(top_n)

        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            return f"⚠️ Lỗi khi sinh nội dung với LLM: {e}"
