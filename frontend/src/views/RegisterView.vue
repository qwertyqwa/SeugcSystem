<template>
  <section class="auth-layout">
    <div class="panel auth-panel">
      <h1>Регистрация</h1>
      <p class="muted">Создайте аккаунт клиента.</p>

      <form class="form-stack" @submit.prevent="submit">
        <label class="field">
          <span>Имя пользователя</span>
          <input v-model.trim="form.username" required autocomplete="username" />
        </label>

        <label class="field">
          <span>Email адрес</span>
          <input v-model.trim="form.email" required type="email" autocomplete="email" />
        </label>

        <label class="field">
          <span>Пароль</span>
          <input v-model="form.password" required type="password" autocomplete="new-password" />
        </label>

        <p v-if="error" class="error-text">{{ error }}</p>
        <p v-if="success" class="success-text">
          Аккаунт создан. Теперь выполните вход.
        </p>

        <button class="primary-button" :disabled="loading">
          {{ loading ? "Создаем..." : "Зарегистрироваться" }}
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
  email: "",
  role: USER_ROLES.CLIENT,
  password: ""
});

const loading = ref(false);
const success = ref(false);
const error = ref("");

async function submit() {
  loading.value = true;
  error.value = "";
  success.value = false;
  try {
    await authStore.register(form);
    success.value = true;
    toastStore.success("Аккаунт создан. Можно входить.");
    setTimeout(() => router.push("/login"), 700);
  } catch (requestError) {
    error.value = extractApiErrorMessage(requestError, "Не удалось зарегистрироваться.");
    toastStore.error(error.value);
  } finally {
    loading.value = false;
  }
}
</script>
