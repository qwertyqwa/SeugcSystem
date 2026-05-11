<template>
  <div class="app-shell">
    <header class="top-bar">
      <RouterLink class="brand" to="/">
        <span class="brand-dot"></span>
        <span>SEUGC Support Flow</span>
      </RouterLink>
      <nav class="nav-links">
        <template v-if="authStore.isAuthenticated">
          <RouterLink v-if="authStore.isClient" to="/client/tickets">Мои обращения</RouterLink>
          <RouterLink v-if="authStore.isClient" to="/client/tickets/new">Создать обращение</RouterLink>
          <RouterLink v-if="authStore.isManager" to="/manager/tickets">Обращения клиентов</RouterLink>
          <button class="text-button" @click="logout">Выйти</button>
        </template>
        <template v-else>
          <RouterLink to="/login">Вход</RouterLink>
          <RouterLink to="/register">Регистрация</RouterLink>
        </template>
      </nav>
    </header>

    <main class="page-container">
      <RouterView />
    </main>
    <AppToasts />
  </div>
</template>

<script setup>
import { RouterLink, RouterView, useRouter } from "vue-router";

import AppToasts from "./components/AppToasts.vue";
import { useAuthStore } from "./stores/auth";
import { useToastStore } from "./stores/toast";

const authStore = useAuthStore();
const toastStore = useToastStore();
const router = useRouter();

function logout() {
  authStore.logout();
  toastStore.info("Вы вышли из системы.");
  router.push("/login");
}
</script>
