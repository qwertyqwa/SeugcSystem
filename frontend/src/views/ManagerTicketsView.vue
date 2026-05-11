<template>
  <section class="stack-page">
    <header class="page-head">
      <div>
        <h1>Все обращения</h1>
        <p class="muted">Фильтруйте и сортируйте обращения клиентов по ключевым признакам.</p>
      </div>
    </header>

    <div class="panel filter-panel grid-filters">
      <label class="field compact-field">
        <span>Поиск по тексту</span>
        <input v-model.trim="filters.q" @keyup.enter="loadTickets" placeholder="например, не работает" />
      </label>
      <label class="field compact-field">
        <span>Приоритет</span>
        <select v-model="filters.priority" @change="loadTickets">
          <option value="">Все</option>
          <option value="high">Высокий</option>
          <option value="medium">Средний</option>
          <option value="low">Низкий</option>
        </select>
      </label>
      <label class="field compact-field">
        <span>Тональность</span>
        <select v-model="filters.sentiment" @change="loadTickets">
          <option value="">Все</option>
          <option value="negative">Негатив</option>
          <option value="neutral">Нейтрально</option>
          <option value="positive">Позитив</option>
        </select>
      </label>
      <label class="field compact-field">
        <span>Статус</span>
        <select v-model="filters.status" @change="loadTickets">
          <option value="">Все</option>
          <option value="new">Новый</option>
          <option value="in_progress">В работе</option>
          <option value="resolved">Решен</option>
          <option value="closed">Закрыт</option>
        </select>
      </label>
      <label class="field compact-field">
        <span>Сортировка</span>
        <select v-model="filters.ordering" @change="loadTickets">
          <option value="-created_at">Сначала новые</option>
          <option value="created_at">Сначала старые</option>
        </select>
      </label>
      <button class="secondary-button" @click="loadTickets">Применить</button>
    </div>

    <p v-if="error" class="error-text">{{ error }}</p>

    <div v-if="loading" class="panel">Загрузка...</div>
    <div v-else-if="tickets.length === 0" class="panel">Обращений по фильтрам не найдено.</div>
    <div v-else class="tickets-grid">
      <article v-for="ticket in tickets" :key="ticket.id" class="ticket-card">
        <header class="ticket-card-header">
          <div>
            <h3 class="ticket-title">Обращение #{{ ticket.id }}</h3>
            <p class="ticket-meta">
              {{ formatDate(ticket.created_at) }} • {{ ticket.author.username }} ({{ ticket.author.email }})
            </p>
          </div>
          <RouterLink class="action-link" :to="`/tickets/${ticket.id}`">Карточка</RouterLink>
        </header>

        <p class="ticket-text">{{ ticket.text }}</p>

        <div class="chip-row">
          <span class="chip" :class="`chip-priority-${ticket.analysis?.priority_label}`">
            Приоритет: {{ getPriorityLabel(ticket.analysis?.priority_label) }}
          </span>
          <span class="chip" :class="`chip-sentiment-${ticket.analysis?.sentiment_label}`">
            Тональность: {{ getSentimentLabel(ticket.analysis?.sentiment_label) }}
          </span>
        </div>

        <div class="status-row">
          <label class="field compact-field">
            <span>Статус</span>
            <select :value="ticket.status" @change="onStatusChange(ticket.id, $event.target.value)">
              <option value="new">Новый</option>
              <option value="in_progress">В работе</option>
              <option value="resolved">Решен</option>
              <option value="closed">Закрыт</option>
            </select>
          </label>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { reactive, ref, onMounted } from "vue";
import { RouterLink } from "vue-router";

import { labelBy, priorityLabels, sentimentLabels } from "../domain/labels";
import { getManagerTickets, updateTicketStatus } from "../api/tickets";
import { useToastStore } from "../stores/toast";
import { extractApiErrorMessage } from "../utils/apiError";

const filters = reactive({
  q: "",
  priority: "",
  sentiment: "",
  status: "",
  ordering: "-created_at"
});

const tickets = ref([]);
const loading = ref(false);
const error = ref("");
const toastStore = useToastStore();

async function loadTickets() {
  loading.value = true;
  error.value = "";
  try {
    tickets.value = await getManagerTickets(filters);
  } catch (requestError) {
    error.value = extractApiErrorMessage(requestError, "Не удалось загрузить обращения.");
    toastStore.error(error.value);
  } finally {
    loading.value = false;
  }
}

async function onStatusChange(ticketId, status) {
  try {
    await updateTicketStatus(ticketId, status);
    const ticket = tickets.value.find((item) => item.id === ticketId);
    if (ticket) {
      ticket.status = status;
    }
    toastStore.success("Статус обновлен.");
  } catch (requestError) {
    error.value = extractApiErrorMessage(requestError, "Не удалось обновить статус.");
    toastStore.error(error.value);
  }
}

function formatDate(value) {
  return new Date(value).toLocaleString("ru-RU");
}

function getPriorityLabel(label) {
  return labelBy(priorityLabels, label, "Не определен");
}

function getSentimentLabel(label) {
  return labelBy(sentimentLabels, label, "Не определена");
}

onMounted(loadTickets);
</script>
