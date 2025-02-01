from pydantic import BaseModel

class CognitiveDistortion(BaseModel):
    distortion_type: str
    utterance: str
    score: int