import datetime

from db.models.users import User_with_rating


async def get_profile_text(user: User_with_rating, event):
    text = "<u>Профиль</u>:\n"
    text_parts = []
    text_parts.append(f"{user.name}")
    if user.username is not None:
        text_parts.append(f"@{user.username}")

    if user.rating is None:
        text_parts.append(f"\n- Рейтинг: - ")
    else:
        text_parts.append(f"\n- Рейтинг: {user.rating}")

    text_parts.append("- Статус: обычный" if user.premium is None or user.premium < datetime.datetime.utcnow() else "- Статус: Премиум")
    text_parts.append(f"- Кол-во отзывов: {user.count_reviews}")
    text_parts.append(f"- Реферальная ссылка: t.me/{(await event.bot.me()).username}?start=usr_{user.user_id}")
    if user.premium is not None and user.premium > datetime.datetime.utcnow() and user.about is not None:
        text_parts.append(f"O себе: {user.about}")

    return text + "\n".join(text_parts)
