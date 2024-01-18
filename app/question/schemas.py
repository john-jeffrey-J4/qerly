from pydantic import BaseModel
class AnswerItem(BaseModel):
    ranking: str
    importance: str
    performance: str
    question_id: int
class Ranking(BaseModel):
    ranking: str
    importance: str
    performance: str
class UserAnswerRequest(BaseModel):
    user_id: int
    pair_id: int
    answer_json:AnswerItem
    sort_order: int

class UserFeedback(BaseModel):
    user: dict
    questionnaire_results: list
    closing_message: str
    team_message: str
