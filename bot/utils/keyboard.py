from aiogram.filters.callback_data import CallbackData


class ReviewsCallbackFactory(CallbackData, prefix="reviews"):
    user_id: str
    page: int = 0


class ProfileCallbackFactory(CallbackData, prefix="profile"):
    user_id: str


class TariffCallbackFactory(CallbackData, prefix="tariff"):
    id: int
    action: str = "look"


class CheckInvoiceCallbackFactory(CallbackData, prefix="check_invoice"):
    id: int



class AddReviewCallbackFactory(CallbackData, prefix="add_review"):
    about_user_id: str


class EvaluationReviewCallbackFactory(CallbackData, prefix="mark"):
    evaluation: int


class ComplaintCallbackFactory(CallbackData, prefix="complaint"):
    about: str


class AnswerComplaintCallbackFactory(CallbackData, prefix="answer_c"):
    answer: bool
    author: str
    about: str
