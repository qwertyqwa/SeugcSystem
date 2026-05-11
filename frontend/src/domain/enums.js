/**
 * Central app enums for better consistency and safer comparisons.
 */
export const USER_ROLES = Object.freeze({
  CLIENT: "client",
  MANAGER: "manager"
});

export const TICKET_STATUSES = Object.freeze({
  NEW: "new",
  IN_PROGRESS: "in_progress",
  RESOLVED: "resolved",
  CLOSED: "closed"
});

export const TICKET_PRIORITIES = Object.freeze({
  LOW: "low",
  MEDIUM: "medium",
  HIGH: "high"
});

export const TICKET_SENTIMENTS = Object.freeze({
  NEGATIVE: "negative",
  NEUTRAL: "neutral",
  POSITIVE: "positive"
});
