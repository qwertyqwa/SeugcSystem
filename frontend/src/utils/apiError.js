function normalizeDetailMessages(details) {
  if (!details || typeof details !== "object") {
    return [];
  }
  const messages = [];
  for (const value of Object.values(details)) {
    if (Array.isArray(value)) {
      for (const item of value) {
        if (typeof item === "string" && item.trim()) {
          messages.push(item.trim());
        }
      }
      continue;
    }
    if (typeof value === "string" && value.trim()) {
      messages.push(value.trim());
    }
  }
  return messages;
}

export function extractApiErrorMessage(error, fallbackMessage) {
  if (error?.code === "ECONNABORTED") {
    return "Сервер отвечает слишком долго. Запрос продолжает обрабатываться, попробуйте обновить страницу.";
  }

  const errorData = error?.response?.data?.error;
  const detailMessages = normalizeDetailMessages(errorData?.details);
  if (detailMessages.length > 0) {
    return detailMessages.join(" ");
  }

  if (typeof errorData?.message === "string" && errorData.message.trim()) {
    return errorData.message.trim();
  }

  return fallbackMessage;
}
