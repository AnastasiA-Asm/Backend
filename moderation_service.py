from moderation_repository import get_min_images_for_unverified_seller
from schemas import PredictRequest

def has_violation(ad: PredictRequest) -> bool:
    if ad.is_verified_seller:
        return False

    return ad.images_qty < get_min_images_for_unverified_seller()