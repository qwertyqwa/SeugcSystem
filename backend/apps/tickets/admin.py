from django.contrib import admin

from .models import Ticket, TicketAnalysis


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "created_at", "updated_at")
    list_filter = ("status", "created_at")
    search_fields = ("text", "user__username", "user__email")


@admin.register(TicketAnalysis)
class TicketAnalysisAdmin(admin.ModelAdmin):
    list_display = (
        "ticket",
        "priority_label",
        "priority_score",
        "sentiment_label",
        "sentiment_score",
        "created_at",
    )
    list_filter = ("priority_label", "sentiment_label")
