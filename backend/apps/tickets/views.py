from django.db.models import QuerySet
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied

from common.responses import success_response

from apps.ml.service import analyze_ticket
from apps.users.permissions import IsClient, IsManager

from .models import Ticket
from .serializers import (
    AnalyzeTextSerializer,
    TicketCreateSerializer,
    TicketSerializer,
    TicketStatusUpdateSerializer,
)
from .services import run_analysis_for_ticket


class TicketCreateView(generics.CreateAPIView):
    serializer_class = TicketCreateSerializer
    permission_classes = [IsClient]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ticket = Ticket.objects.create(
            user=request.user,
            text=serializer.validated_data["text"],
        )
        run_analysis_for_ticket(ticket)
        ticket.refresh_from_db()
        return success_response(TicketSerializer(ticket).data, status_code=status.HTTP_201_CREATED)


class ClientTicketListView(generics.ListAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsClient]

    def get_queryset(self) -> QuerySet[Ticket]:
        qs = (
            Ticket.objects.select_related("user", "analysis")
            .filter(user=self.request.user)
        )
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        ordering = self.request.query_params.get("ordering", "-created_at")
        if ordering in {"created_at", "-created_at"}:
            qs = qs.order_by(ordering)
        return qs

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return success_response(serializer.data)


class ManagerTicketListView(generics.ListAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsManager]

    def get_queryset(self) -> QuerySet[Ticket]:
        qs = Ticket.objects.select_related("user", "analysis").all()
        priority = self.request.query_params.get("priority")
        sentiment = self.request.query_params.get("sentiment")
        status_filter = self.request.query_params.get("status")
        search_text = self.request.query_params.get("q")
        ordering = self.request.query_params.get("ordering", "-created_at")

        if priority:
            qs = qs.filter(analysis__priority_label=priority)
        if sentiment:
            qs = qs.filter(analysis__sentiment_label=sentiment)
        if status_filter:
            qs = qs.filter(status=status_filter)
        if search_text:
            qs = qs.filter(text__icontains=search_text)

        allowed_orderings = {"created_at", "-created_at", "status", "-status"}
        if ordering in allowed_orderings:
            qs = qs.order_by(ordering)
        return qs

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return success_response(serializer.data)


class TicketDetailView(generics.RetrieveAPIView):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Ticket.objects.select_related("user", "analysis").all()

    def get_object(self):
        ticket = super().get_object()
        user = self.request.user
        if user.role == "manager":
            return ticket
        if user.role == "client" and ticket.user_id == user.id:
            return ticket
        raise PermissionDenied("You do not have access to this ticket.")

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return success_response(serializer.data)


class TicketStatusUpdateView(generics.UpdateAPIView):
    serializer_class = TicketStatusUpdateSerializer
    permission_classes = [IsManager]
    queryset = Ticket.objects.select_related("user", "analysis").all()

    def patch(self, request, *args, **kwargs):
        ticket = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ticket.status = serializer.validated_data["status"]
        ticket.save(update_fields=["status", "updated_at"])
        return success_response(TicketSerializer(ticket).data)


class AnalyzeTextView(generics.GenericAPIView):
    serializer_class = AnalyzeTextSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = analyze_ticket(serializer.validated_data["text"])
        return success_response(result)
