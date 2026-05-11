<template>
  <article class="ticket-card">
    <header class="ticket-card-header">
      <div>
        <h3 class="ticket-title">Обращение #{{ ticket.id }}</h3>
        <p class="ticket-meta">
          <span>{{ formatDate(ticket.created_at) }}</span>
          <span v-if="ticket.author">• {{ ticket.author.username }}</span>
        </p>
      </div>
      <div class="chip-row">
        <span class="chip" :class="priorityClass">{{ priorityLabel }}</span>
        <span class="chip" :class="sentimentClass">{{ sentimentLabel }}</span>
        <span class="chip chip-status">{{ statusLabel }}</span>
      </div>
    </header>

    <p class="ticket-text">{{ ticket.text }}</p>

    <footer class="ticket-footer">
      <RouterLink class="action-link" :to="`/tickets/${ticket.id}`">Открыть карточку</RouterLink>
    </footer>
  </article>
</template>

<script setup>
import { computed } from "vue";
import { RouterLink } from "vue-router";

import { labelBy, priorityLabels, sentimentLabels, statusLabels } from "../domain/labels";

const props = defineProps({
  ticket: {
    type: Object,
    required: true
  }
});

const priorityLabel = computed(
  () => `${labelBy(priorityLabels, props.ticket.analysis?.priority_label, "Не определен")} приоритет`
);
const sentimentLabel = computed(
  () => labelBy(sentimentLabels, props.ticket.analysis?.sentiment_label, "Не определена")
);
const statusLabel = computed(() => labelBy(statusLabels, props.ticket.status, props.ticket.status));

const priorityClass = computed(() => `chip-priority-${props.ticket.analysis?.priority_label || "neutral"}`);
const sentimentClass = computed(() => `chip-sentiment-${props.ticket.analysis?.sentiment_label || "neutral"}`);

function formatDate(value) {
  return new Date(value).toLocaleString("ru-RU");
}
</script>
