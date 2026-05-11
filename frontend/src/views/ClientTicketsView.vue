<template>
  <section class="stack-page">
    <header class="page-head">
      <div>
        <h1>Мои обращения</h1>
        <p class="muted">Список всех созданных вами обращений с рассчитанными метками.</p>
      </div>
      <RouterLink class="primary-button as-link" to="/client/tickets/new">Новое обращение</RouterLink>
    </header>

    <div class="panel filter-panel">
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
        <span>Сортировка по дате</span>
        <select v-model="filters.ordering" @change="loadTickets">
          <option value="-created_at">Сначала новые</option>
          <option value="created_at">Сначала старые</option>
        </select>
      </label>
    </div>

    <p v-if="error" class="error-text">{{ error }}</p>

    <div v-if="loading" class="panel">Загрузка...</div>
    <div v-else-if="tickets.length === 0" class="panel">Пока нет обращений.</div>
    <div v-else class="tickets-grid">
      <TicketCard v-for="ticket in tickets" :key="ticket.id" :ticket="ticket" />
    </div>
  </section>
</template>

<script setup>
import { reactive, ref, onMounted } from "vue";
import { RouterLink } from "vue-router";

import { getMyTickets } from "../api/tickets";
import TicketCard from "../components/TicketCard.vue";
import { useToastStore } from "../stores/toast";
import { extractApiErrorMessage } from "../utils/apiError";

const filters = reactive({
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
    tickets.value = await getMyTickets(filters);
  } catch (requestError) {
    error.value = extractApiErrorMessage(requestError, "Не удалось загрузить обращения.");
    toastStore.error(error.value);
  } finally {
    loading.value = false;
  }
}

onMounted(loadTickets);
</script>
