<template>
  <section class="stack-page">
    <header>
      <h1>Карточка обращения</h1>
      <p class="muted">Детали обращения и результаты автоматического анализа текста.</p>
    </header>

    <p v-if="error" class="error-text">{{ error }}</p>
    <div v-if="loading" class="panel">Загрузка...</div>

    <article v-else-if="ticket" class="panel detail-card">
      <div class="detail-head">
        <h2>Обращение #{{ ticket.id }}</h2>
        <span class="chip chip-status">{{ statusLabel }}</span>
      </div>

      <p class="muted">
        Автор: {{ ticket.author.username }} ({{ ticket.author.email }})<br />
        Создано: {{ formatDate(ticket.created_at) }}<br />
        Обновлено: {{ formatDate(ticket.updated_at) }}
      </p>

      <div class="text-block">{{ ticket.text }}</div>

      <section class="analysis-block">
        <h3>Результаты анализа</h3>
        <div class="chip-row">
          <span class="chip" :class="`chip-priority-${ticket.analysis?.priority_label}`">
            Приоритет: {{ priorityLabel }}
          </span>
          <span class="chip" :class="`chip-sentiment-${ticket.analysis?.sentiment_label}`">
            Тональность: {{ sentimentLabel }}
          </span>
        </div>

        <div class="metrics-grid">
          <div class="metric">
            <span>Уверенность приоритета</span>
            <strong>{{ toPercent(ticket.analysis?.priority_score) }}</strong>
          </div>
          <div class="metric">
            <span>Уверенность тональности</span>
            <strong>{{ toPercent(ticket.analysis?.sentiment_score) }}</strong>
          </div>
          <div class="metric">
            <span>P(low)</span>
            <strong>{{ toPercent(ticket.analysis?.priority_prob_low) }}</strong>
          </div>
          <div class="metric">
            <span>P(medium)</span>
            <strong>{{ toPercent(ticket.analysis?.priority_prob_medium) }}</strong>
          </div>
          <div class="metric">
            <span>P(high)</span>
            <strong>{{ toPercent(ticket.analysis?.priority_prob_high) }}</strong>
          </div>
        </div>
      </section>

      <section v-if="authStore.isManager" class="analysis-block">
        <h3>Изменить статус</h3>
        <div class="status-update">
          <select v-model="nextStatus" class="input-select">
            <option value="new">Новый</option>
            <option value="in_progress">В работе</option>
            <option value="resolved">Решен</option>
            <option value="closed">Закрыт</option>
          </select>
          <button class="primary-button" @click="updateStatus">Сохранить</button>
        </div>
      </section>
    </article>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";

import { TICKET_STATUSES } from "../domain/enums";
import { labelBy, priorityLabels, sentimentLabels, statusLabels } from "../domain/labels";
import { getTicketById, updateTicketStatus } from "../api/tickets";
import { useAuthStore } from "../stores/auth";
import { useToastStore } from "../stores/toast";
import { extractApiErrorMessage } from "../utils/apiError";

const route = useRoute();
const authStore = useAuthStore();
const toastStore = useToastStore();

const ticket = ref(null);
const loading = ref(false);
const error = ref("");
const nextStatus = ref(TICKET_STATUSES.NEW);

const statusLabel = computed(() => {
  if (!ticket.value) {
    return "";
  }
  return labelBy(statusLabels, ticket.value.status, ticket.value.status);
});
const priorityLabel = computed(() => {
  const label = ticket.value?.analysis?.priority_label;
  return labelBy(priorityLabels, label, "Не определен");
});
const sentimentLabel = computed(() => {
  const label = ticket.value?.analysis?.sentiment_label;
  return labelBy(sentimentLabels, label, "Не определена");
});

async function loadTicket() {
  loading.value = true;
  error.value = "";
  try {
    ticket.value = await getTicketById(route.params.id);
    nextStatus.value = ticket.value.status;
  } catch (requestError) {
    error.value = extractApiErrorMessage(requestError, "Не удалось загрузить карточку.");
    toastStore.error(error.value);
  } finally {
    loading.value = false;
  }
}

async function updateStatus() {
  if (!ticket.value) {
    return;
  }
  try {
    const updatedTicket = await updateTicketStatus(ticket.value.id, nextStatus.value);
    ticket.value = updatedTicket;
    toastStore.success("Статус обновлен.");
  } catch (requestError) {
    error.value = extractApiErrorMessage(requestError, "Не удалось обновить статус.");
    toastStore.error(error.value);
  }
}

function formatDate(value) {
  return new Date(value).toLocaleString("ru-RU");
}

function toPercent(value) {
  const normalized = Number(value || 0) * 100;
  return `${normalized.toFixed(1)}%`;
}

onMounted(loadTicket);
</script>
