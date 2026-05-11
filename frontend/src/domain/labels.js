import { TICKET_PRIORITIES, TICKET_SENTIMENTS, TICKET_STATUSES } from "./enums";

export const statusLabels = Object.freeze({
  [TICKET_STATUSES.NEW]: "Новый",
  [TICKET_STATUSES.IN_PROGRESS]: "В работе",
  [TICKET_STATUSES.RESOLVED]: "Решен",
  [TICKET_STATUSES.CLOSED]: "Закрыт"
});

export const priorityLabels = Object.freeze({
  [TICKET_PRIORITIES.LOW]: "Низкий",
  [TICKET_PRIORITIES.MEDIUM]: "Средний",
  [TICKET_PRIORITIES.HIGH]: "Высокий"
});

export const sentimentLabels = Object.freeze({
  [TICKET_SENTIMENTS.NEGATIVE]: "Негативная",
  [TICKET_SENTIMENTS.NEUTRAL]: "Нейтральная",
  [TICKET_SENTIMENTS.POSITIVE]: "Позитивная"
});

export function labelBy(map, key, fallback) {
  return map[key] || fallback;
}
