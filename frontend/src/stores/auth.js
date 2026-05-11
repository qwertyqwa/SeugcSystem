import { defineStore } from "pinia";

import { apiClient } from "../api/client";
import { USER_ROLES } from "../domain/enums";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null,
    accessToken: null,
    refreshToken: null
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.accessToken),
    isClient: (state) => state.user?.role === USER_ROLES.CLIENT,
    isManager: (state) => state.user?.role === USER_ROLES.MANAGER
  },
  actions: {
    loadFromStorage() {
      this.accessToken = localStorage.getItem("accessToken");
      this.refreshToken = localStorage.getItem("refreshToken");
      const rawUser = localStorage.getItem("authUser");
      this.user = rawUser ? JSON.parse(rawUser) : null;
    },
    setAuth(data) {
      this.accessToken = data.access;
      this.refreshToken = data.refresh;
      this.user = data.user;

      localStorage.setItem("accessToken", data.access);
      localStorage.setItem("refreshToken", data.refresh);
      localStorage.setItem("authUser", JSON.stringify(data.user));
    },
    async login(credentials) {
      const response = await apiClient.post("/auth/login/", credentials);
      this.setAuth(response.data.data);
    },
    async register(payload) {
      await apiClient.post("/auth/register/", payload);
    },
    async fetchMe() {
      const response = await apiClient.get("/auth/me/");
      this.user = response.data.data;
      localStorage.setItem("authUser", JSON.stringify(this.user));
    },
    logout() {
      this.user = null;
      this.accessToken = null;
      this.refreshToken = null;
      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");
      localStorage.removeItem("authUser");
    }
  }
});
