from __future__ import annotations


def review_queue_badge(request):
    """
    Injecte le nombre de tickets de revue en attente dans chaque template.
    Permet d'afficher le badge de notification dans la navigation.
    Non-bloquant : toute erreur retourne 0.
    """
    if not request.user.is_authenticated:
        return {"pending_reviews_count": 0}
    try:
        from .models import RecognitionReviewQueue
        count = RecognitionReviewQueue.objects.filter(
            status=RecognitionReviewQueue.STATUS_PENDING
        ).count()
        return {"pending_reviews_count": count}
    except Exception:
        return {"pending_reviews_count": 0}
