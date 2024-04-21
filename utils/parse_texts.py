import json

from pydantic import BaseModel


class Texts(BaseModel):
    back_button: str
    input_user_text: str
    error_input_user: str

    start_policy: str
    start_policy_button: str
    start: str
    start_button_reviews: str
    start_button_profile: str

    my_profile_buy: str
    my_profile_reviews: str
    my_profile_about_me: str

    about_me: str
    about_me_premium: str
    about_me_premium_button: str
    error_long_about_me: str
    success_about_me: str
    user_profile_reviews: str
    user_profile_add_reviews: str
    user_profile_complain: str

    buy_tariff: str
    buy_payment_system: str
    title_invoice: str
    success_invoice: str
    crypto_bot: str
    crypto_boy_false: str

    complaint_input_text: str

    admin: str
    sender_text_input: str
    sender_link_input: str
    sender_begin: str

    price_edit_text: str
    price_input: str
    confirmation_edit: str
    confirmation_block: str

    policy_edit: str
    confirmation_clean_reviews: str

    give_premium: str
    give_premium_success: str




def parse_policy():
    with open("utils/policy.txt", 'r', encoding='utf-8') as f:
        return f.read()


def edit_policy(text):
    with open("utils/policy.txt", 'w', encoding='utf-8') as f:
        f.write(text)



with open('texts.JSON', 'r', encoding='utf-8') as f:
    texts = Texts.model_validate_json(str(f.read()))
