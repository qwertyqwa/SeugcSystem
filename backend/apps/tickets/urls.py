from django.urls import path

from .views import (
    AnalyzeTextView,
    ClientTicketListView,
    ManagerTicketListView,
    TicketCreateView,
    TicketDetailView,
    TicketStatusUpdateView,
)


urlpatterns = [
    path("tickets/", TicketCreateView.as_view(), name="ticket_create"),
    path("tickets/my/", ClientTicketListView.as_view(), name="ticket_list_client"),
    path("tickets/manager/", ManagerTicketListView.as_view(), name="ticket_list_manager"),
    path("tickets/<int:pk>/", TicketDetailView.as_view(), name="ticket_detail"),
    path("tickets/<int:pk>/status/", TicketStatusUpdateView.as_view(), name="ticket_status_update"),
    path("analyze/", AnalyzeTextView.as_view(), name="analyze_text"),
]
