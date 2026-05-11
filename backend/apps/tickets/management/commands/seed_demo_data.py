import random
from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.ml.service import analyze_ticket
from apps.tickets.models import Ticket, TicketAnalysis, TicketStatus
from apps.users.models import UserRole


@dataclass(frozen=True)
class DemoUserSpec:
    username: str
    email: str
    role: str
    password: str


class DemoUserManager:
    def __init__(self, user_model):
        self._user_model = user_model

    def get_or_create_user(self, spec: DemoUserSpec):
        user, created = self._user_model.objects.get_or_create(
            username=spec.username,
            defaults={
                "email": spec.email,
                "role": spec.role,
            },
        )
        if created:
            user.set_password(spec.password)
            user.save(update_fields=["password"])
            return user, True

        fields_to_update = []
        if user.email != spec.email:
            user.email = spec.email
            fields_to_update.append("email")
        if user.role != spec.role:
            user.role = spec.role
            fields_to_update.append("role")
        if fields_to_update:
            user.save(update_fields=fields_to_update)
        return user, False


class DemoTicketManager:
    _ticket_samples = (
        "Срочно: после обновления 1С не открывается карточка клиента, работа отдела встала.",
        "Добрый день. Не печатается счет в PDF, ошибка появляется только на рабочем месте кассира.",
        "Прошу проверить доступ к отчету по продажам, у нового сотрудника пустая страница.",
        "Критично: API интеграции с маркетплейсом возвращает 500, заказы не выгружаются.",
        "Не работает синхронизация остатков с сайтом уже второй час.",
        "Спасибо за прошлое исправление. Сейчас нужно добавить поле комментария в форму заявки.",
        "После входа в личный кабинет вижу белый экран, в консоли ошибка script load failed.",
        "Нужно перенастроить уведомления на новую почту менеджера региона.",
        "Система сильно тормозит при открытии списка заказов за месяц.",
        "Пожалуйста, восстановите доступ сотруднику Петрову, не приходит код подтверждения.",
    )

    def create_demo_tickets(self, users, per_user: int) -> int:
        created_count = 0
        for user in users:
            for index in range(per_user):
                text = self._ticket_samples[index % len(self._ticket_samples)]
                ticket = Ticket.objects.create(
                    user=user,
                    text=text,
                    status=self._pick_status(index),
                )
                self._create_analysis(ticket)
                created_count += 1
        return created_count

    def _pick_status(self, index: int) -> str:
        if index == 0:
            return TicketStatus.NEW
        return random.choice(
            [TicketStatus.NEW, TicketStatus.IN_PROGRESS, TicketStatus.RESOLVED, TicketStatus.CLOSED]
        )

    def _create_analysis(self, ticket: Ticket) -> None:
        result = analyze_ticket(ticket.text)
        priority = result.get("priority", {})
        probabilities = priority.get("probabilities", {}) or {}
        sentiment = result.get("sentiment", {})

        TicketAnalysis.objects.create(
            ticket=ticket,
            priority_label=priority.get("label", "medium"),
            priority_score=float(priority.get("score", 0.0)),
            priority_prob_low=float(probabilities.get("low", 0.0)),
            priority_prob_medium=float(probabilities.get("medium", 0.0)),
            priority_prob_high=float(probabilities.get("high", 0.0)),
            sentiment_label=sentiment.get("label", "neutral"),
            sentiment_score=float(sentiment.get("score", 0.0)),
        )


class DemoDataCoordinator:
    def __init__(self):
        self._user_manager = DemoUserManager(get_user_model())
        self._ticket_manager = DemoTicketManager()

    def seed(self, tickets_per_client: int) -> dict:
        user_specs = (
            DemoUserSpec(
                username="manager_demo",
                email="manager_demo@example.com",
                role=UserRole.MANAGER,
                password="DemoPass123!",
            ),
            DemoUserSpec(
                username="client_anna",
                email="client_anna@example.com",
                role=UserRole.CLIENT,
                password="DemoPass123!",
            ),
            DemoUserSpec(
                username="client_ivan",
                email="client_ivan@example.com",
                role=UserRole.CLIENT,
                password="DemoPass123!",
            ),
            DemoUserSpec(
                username="client_olga",
                email="client_olga@example.com",
                role=UserRole.CLIENT,
                password="DemoPass123!",
            ),
        )

        created_users = 0
        client_users = []
        for spec in user_specs:
            user, created = self._user_manager.get_or_create_user(spec)
            created_users += int(created)
            if user.role == UserRole.CLIENT:
                client_users.append(user)

        created_tickets = self._ticket_manager.create_demo_tickets(client_users, tickets_per_client)
        return {
            "created_users": created_users,
            "total_users_processed": len(user_specs),
            "created_tickets": created_tickets,
            "clients_count": len(client_users),
        }


class Command(BaseCommand):
    help = "Create demo users and tickets with ML analysis."

    def add_arguments(self, parser):
        parser.add_argument(
            "--tickets-per-client",
            type=int,
            default=8,
            help="How many tickets to create for each demo client.",
        )

    def handle(self, *args, **options):
        tickets_per_client = max(1, int(options["tickets_per_client"]))
        result = DemoDataCoordinator().seed(tickets_per_client=tickets_per_client)

        self.stdout.write(self.style.SUCCESS("Demo data created successfully."))
        self.stdout.write(f"Users processed: {result['total_users_processed']}")
        self.stdout.write(f"New users created: {result['created_users']}")
        self.stdout.write(f"Client users: {result['clients_count']}")
        self.stdout.write(f"New tickets created: {result['created_tickets']}")
