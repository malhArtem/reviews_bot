from sqlalchemy import select, or_, func

from db.models.parameters import ParametersModel
from db.models.publications import Publications
from db.models.subscription import Subscription

#
# search_list = ["brand1", "country33"]
#
# stmt_1 = select(Publications).filter(Publications.status == "open").filter(Publications.type == "lot").subquery()
# stmt = select(stmt_1, ParametersModel).join(stmt_1, stmt_1.c.id == ParametersModel.id, isouter=True).subquery()
#
# stmt2 = select(stmt.c.id, func.array_agg(stmt.c.value, ' ').label('value'), stmt.c.description).group_by(stmt.c.id)
# stmt3 = select(stmt2.c.id)
#
# # for word in search_list:
# #     stmt3 = stmt3.filter(or_(stmt2.c.array_agg_1.ilike(f"%{word}%"), stmt2.c.description.ilike(f"%{word}%")))
#
#
#
#
# print(stmt2)

query = "мама мыла раму папой"
stmt = select(Subscription).filter(Subscription.status).filter(Subscription.query.contained_by(query.split()))

print(stmt)



"""SELECT anon_1.user_id, anon_1.chat_id, anon_1.name, anon_1.username, anon_1.premium, anon_1.about, anon_1.created_at, avg(anon_1.evaluation) OVER (PARTITION BY anon_1.user_id) AS anon_2, count(anon_1.evaluation) OVER (PARTITION BY anon_1.user_id) AS anon_3 
FROM (SELECT users_1.user_id AS user_id, users_1.chat_id AS chat_id, users_1.name AS name, users_1.username AS username, users_1.premium AS premium, users_1.agree AS agree, users_1.referral_code AS referral_code, users_1.about AS about, users_1.created_at AS created_at, users_1.updated_at AS updated_at, reviews_1.id AS id, reviews_1.reviewer_id AS reviewer_id, reviews_1.about_id AS about_id, reviews_1.evaluation AS evaluation, reviews_1.text AS text, reviews_1.created_at AS created_at_1, reviews_1.updated_at AS updated_at_1 
FROM users AS users_1 LEFT OUTER JOIN reviews AS reviews_1 ON users_1.user_id = reviews_1.about_id 
WHERE users_1.username = $1::VARCHAR ORDER BY users.updated_at DESC 
 LIMIT $2::INTEGER) AS anon_1"""