<template>
  <section class="stack-page">
    <header>
      <h1>Создать обращение</h1>
      <p class="muted">Опишите проблему, система автоматически определит приоритет и тональность.</p>
    </header>

    <div class="panel">
      <form class="form-stack" @submit.prevent="submit">
        <label class="field">
          <span>Текст обращения</span>
          <textarea
            v-model="text"
            rows="8"
            maxlength="10000"
            placeholder="Например: с утра не работает выгрузка и горят ошибки в личном кабинете"
            required
          ></textarea>
        </label>

        <p v-if="error" class="error-text">{{ error }}</p>
        <div v-if="loading" class="loader-inline" role="status" aria-live="polite">
          <span class="loader-spinner" aria-hidden="true"></span>
          <span>Анализируем текст, это может занять до 10-20 секунд...</span>
        </div>

        <button class="primary-button" :disabled="loading || !text.trim()">
          {{ loading ? "Отправляем..." : "Отправить обращение" }}
        </button>
      </form>
    </div>
  </section>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

import { createTicket } from "../api/tickets";
import { useToastStore } from "../stores/toast";
import { extractApiErrorMessage } from "../utils/apiError";

const router = useRouter();
const toastStore = useToastStore();
const text = ref("");
const loading = ref(false);
const error = ref("");

async function submit() {
  loading.value = true;
  error.value = "";
  try {
    const ticket = await createTicket({ text: text.value });
    toastStore.success("Обращение создано, анализ готов.");
    router.push(`/tickets/${ticket.id}`);
  } catch (requestError) {
    error.value = extractApiErrorMessage(requestError, "Не удалось создать обращение.");
    toastStore.error(error.value);
  } finally {
    loading.value = false;
  }
}
</script>
