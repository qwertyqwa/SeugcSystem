<template>
  <section class="auth-layout">
    <div class="panel auth-panel">
      <h1>Вход в систему</h1>
      <p class="muted">Авторизуйтесь, чтобы работать с обращениями.</p>

      <form class="form-stack" @submit.prevent="submit">
        <label class="field">
          <span>Имя пользователя</span>
          <input v-model.trim="form.username" required autocomplete="username" />
        </label>

        <label class="field">
          <span>Пароль</span>
          <input
            v-model="form.password"
            required
            type="password"
            autocomplete="current-password"
          />
        </label>

        <p v-if="error" class="error-text">{{ error }}</p>

        <button class="primary-button" :disabled="loading">
          {{ loading ? "Входим..." : "Войти" }}
        </button>
      </form>
    </div>
  </section>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";

import { USER_ROLES } from "../domain/enums";
import { extractApiErrorMessage } from "../utils/apiError";
import { useAuthStore } from "../stores/auth";
import { useToastStore } from "../stores/toast";

const authStore = useAuthStore();
const toastStore = useToastStore();
const router = useRouter();

const form = reactive({
  username: "",
  password: ""
});

const loading = ref(false);
const error = ref("");

async function submit() {
  loading.value = true;
  error.value = "";
  try {
    await authStore.login(form);
    toastStore.success("Вход выполнен.");
    const nextPath = authStore.user?.role === USER_ROLES.MANAGER ? "/manager/tickets" : "/client/tickets";
    router.push(nextPath);
  } catch (requestError) {
    error.value = extractApiErrorMessage(requestError, "Не удалось выполнить вход.");
    toastStore.error(error.value);
  } finally {
    loading.value = false;
  }
}
</script>
