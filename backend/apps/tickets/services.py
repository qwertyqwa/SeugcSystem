import logging

from apps.ml.service import analyze_ticket

from .models import TicketAnalysis


logger = logging.getLogger(__name__)


def run_analysis_for_ticket(ticket):
    result = analyze_ticket(ticket.text)
    priority = result.get("priority", {})
    sentiment = result.get("sentiment", {})
    probs = priority.get("probabilities", {}) or {}

    analysis = TicketAnalysis.objects.create(
        ticket=ticket,
        priority_label=str(priority.get("label", "medium")),
        priority_score=float(priority.get("score", 0.0)),
        priority_prob_low=float(probs.get("low", 0.0)),
        priority_prob_medium=float(probs.get("medium", 0.0)),
        priority_prob_high=float(probs.get("high", 0.0)),
        sentiment_label=str(sentiment.get("label", "neutral")),
        sentiment_score=float(sentiment.get("score", 0.0)),
    )

    logger.info(
        "Ticket %s analyzed: priority=%s sentiment=%s",
        ticket.pk,
        analysis.priority_label,
        analysis.sentiment_label,
    )
    return analysis
