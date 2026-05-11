from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Ticket, TicketAnalysis, TicketStatus


User = get_user_model()


def make_analysis(ticket, priority="medium", sentiment="neutral"):
    probabilities = {
        "low": 0.2,
        "medium": 0.6,
        "high": 0.2,
    }
    if priority == "high":
        probabilities = {"low": 0.05, "medium": 0.15, "high": 0.8}
    if priority == "low":
        probabilities = {"low": 0.8, "medium": 0.15, "high": 0.05}

    return TicketAnalysis.objects.create(
        ticket=ticket,
        priority_label=priority,
        priority_score=probabilities[priority],
        priority_prob_low=probabilities["low"],
        priority_prob_medium=probabilities["medium"],
        priority_prob_high=probabilities["high"],
        sentiment_label=sentiment,
        sentiment_score=0.8 if sentiment != "neutral" else 0.7,
    )


class TicketApiTests(APITestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            username="client_a",
            email="client_a@example.com",
            password="StrongPass123",
            role="client",
        )
        self.client_user_2 = User.objects.create_user(
            username="client_b",
            email="client_b@example.com",
            password="StrongPass123",
            role="client",
        )
        self.manager_user = User.objects.create_user(
            username="manager_a",
            email="manager_a@example.com",
            password="StrongPass123",
            role="manager",
            is_staff=True,
        )

    @patch("apps.tickets.services.analyze_ticket")
    def test_client_can_create_ticket_and_analysis(self, analyze_ticket_mock):
        analyze_ticket_mock.return_value = {
            "priority": {
                "label": "high",
                "score": 0.92,
                "probabilities": {"low": 0.02, "medium": 0.06, "high": 0.92},
            },
            "sentiment": {"label": "negative", "score": 0.89},
        }
        self.client.force_authenticate(self.client_user)
        url = reverse("ticket_create")

        response = self.client.post(url, {"text": "Срочно, не работает выгрузка!"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        ticket = Ticket.objects.get(id=response.data["data"]["id"])
        self.assertEqual(ticket.user_id, self.client_user.id)
        self.assertTrue(hasattr(ticket, "analysis"))
        self.assertEqual(ticket.analysis.priority_label, "high")
        self.assertEqual(ticket.analysis.sentiment_label, "negative")
        analyze_ticket_mock.assert_called_once()

    def test_manager_cannot_create_ticket(self):
        self.client.force_authenticate(self.manager_user)
        url = reverse("ticket_create")

        response = self.client.post(url, {"text": "Менеджер пытается создать тикет"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_client_list_returns_only_own_tickets(self):
        self.client.force_authenticate(self.client_user)
        own_ticket = Ticket.objects.create(user=self.client_user, text="Мой тикет")
        foreign_ticket = Ticket.objects.create(user=self.client_user_2, text="Чужой тикет")
        make_analysis(own_ticket, priority="low", sentiment="neutral")
        make_analysis(foreign_ticket, priority="high", sentiment="negative")

        response = self.client.get(reverse("ticket_list_client"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["id"], own_ticket.id)

    def test_manager_list_filters_by_priority_and_sentiment(self):
        self.client.force_authenticate(self.manager_user)
        ticket_a = Ticket.objects.create(user=self.client_user, text="Критичная проблема в личном кабинете")
        ticket_b = Ticket.objects.create(user=self.client_user_2, text="Небольшой вопрос по отчету")
        make_analysis(ticket_a, priority="high", sentiment="negative")
        make_analysis(ticket_b, priority="low", sentiment="positive")

        response = self.client.get(
            reverse("ticket_list_manager"),
            {"priority": "high", "sentiment": "negative"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["id"], ticket_a.id)

    def test_client_cannot_open_other_client_ticket(self):
        ticket = Ticket.objects.create(user=self.client_user_2, text="Закрытая информация")
        make_analysis(ticket, priority="medium", sentiment="neutral")

        self.client.force_authenticate(self.client_user)
        response = self.client.get(reverse("ticket_detail", kwargs={"pk": ticket.id}))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data["success"])

    def test_manager_can_update_ticket_status(self):
        ticket = Ticket.objects.create(user=self.client_user, text="Требуется обновить статус")
        make_analysis(ticket, priority="medium", sentiment="neutral")

        self.client.force_authenticate(self.manager_user)
        response = self.client.patch(
            reverse("ticket_status_update", kwargs={"pk": ticket.id}),
            {"status": TicketStatus.RESOLVED},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, TicketStatus.RESOLVED)

    def test_client_cannot_update_ticket_status(self):
        ticket = Ticket.objects.create(user=self.client_user, text="Попытка обновления статуса")
        make_analysis(ticket, priority="medium", sentiment="neutral")
        self.client.force_authenticate(self.client_user)

        response = self.client.patch(
            reverse("ticket_status_update", kwargs={"pk": ticket.id}),
            {"status": TicketStatus.CLOSED},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("apps.tickets.views.analyze_ticket")
    def test_analyze_endpoint_returns_result_for_authenticated_user(self, analyze_ticket_mock):
        analyze_ticket_mock.return_value = {
            "priority": {"label": "high", "score": 0.91, "probabilities": {"low": 0.03, "medium": 0.06, "high": 0.91}},
            "sentiment": {"label": "negative", "score": 0.86},
        }
        self.client.force_authenticate(self.manager_user)

        response = self.client.post(reverse("analyze_text"), {"text": "critical outage"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["priority"]["label"], "high")
        self.assertEqual(response.data["data"]["sentiment"]["label"], "negative")

    def test_analyze_endpoint_requires_authentication(self):
        response = self.client.post(reverse("analyze_text"), {"text": "text"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
