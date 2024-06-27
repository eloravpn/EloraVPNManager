from pydantic import BaseModel


class ClubProfileBase(BaseModel):
    total_score: int
    total_subset: int


class ClubProfileCreate(ClubProfileBase):
    pass


class ClubProfileModify(ClubProfileBase):
    id: int


class ClubScoreBase(BaseModel):
    unique_id: str
    campaign_key: str
    score: int
    description: str


class ClubScoreCreate(ClubScoreBase):
    pass


class ClubScoreModify(ClubScoreBase):
    id: int
