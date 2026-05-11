from django.conf import settings
from django.db import models


class TicketStatus(models.TextChoices):
    NEW = "new", "New"
    IN_PROGRESS = "in_progress", "In Progress"
    RESOLVED = "resolved", "Resolved"
    CLOSED = "closed", "Closed"


class Ticket(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tickets")
    text = models.TextField()
    status = models.CharField(max_length=20, choices=TicketStatus.choices, default=TicketStatus.NEW)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Ticket #{self.pk} ({self.status})"


class TicketAnalysis(models.Model):
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name="analysis")
    priority_label = models.CharField(max_length=20)
    priority_score = models.FloatField(default=0.0)
    priority_prob_low = models.FloatField(default=0.0)
    priority_prob_medium = models.FloatField(default=0.0)
    priority_prob_high = models.FloatField(default=0.0)
    sentiment_label = models.CharField(max_length=20)
    sentiment_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Analysis for ticket #{self.ticket_id}"
