<template>
  <div class="toast-stack" aria-live="polite" aria-atomic="true">
    <article
      v-for="toast in toastStore.items"
      :key="toast.id"
      class="toast-item"
      :class="`toast-${toast.type}`"
    >
      <p>{{ toast.message }}</p>
      <button class="toast-close" @click="toastStore.remove(toast.id)" aria-label="Закрыть">×</button>
    </article>
  </div>
</template>

<script setup>
import { useToastStore } from "../stores/toast";

const toastStore = useToastStore();
</script>
