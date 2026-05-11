import { defineStore } from "pinia";

const DEFAULT_DURATION_MS = 3500;

/**
 * @typedef {"success" | "error" | "info"} ToastType
 */

export const useToastStore = defineStore("toast", {
  state: () => ({
    items: []
  }),
  actions: {
    push(message, type = "info", duration = DEFAULT_DURATION_MS) {
      const id = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
      this.items.push({ id, message, type });
      if (duration > 0) {
        setTimeout(() => this.remove(id), duration);
      }
      return id;
    },
    success(message, duration) {
      return this.push(message, "success", duration);
    },
    error(message, duration) {
      return this.push(message, "error", duration);
    },
    info(message, duration) {
      return this.push(message, "info", duration);
    },
    remove(id) {
      this.items = this.items.filter((item) => item.id !== id);
    }
  }
});
