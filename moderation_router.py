import logging

from fastapi import APIRouter, HTTPException

import moderation_service
from schemas import PredictRequest

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/predict", response_model=bool)
def predict(ad: PredictRequest) -> bool:
    try:
        return moderation_service.has_violation(ad)
    except Exception as error:
        logger.exception("Moderation prediction failed")
        raise HTTPException(
            status_code=500,
            detail="Не удалось проверить объявление",
        ) from error