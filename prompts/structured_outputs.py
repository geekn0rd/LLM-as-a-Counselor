from pydantic import BaseModel


class CognitiveDistortion(BaseModel):
    distortion_type: str
    utterance: str
    score: int


class DialogueRequest(BaseModel):
    messages: str


class DialogueResponse(BaseModel):
    response: str
    distortion_type: CognitiveDistortion
    cbt_technique: str
    cbt_stage: str
