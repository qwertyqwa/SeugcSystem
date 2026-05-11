import { createRouter, createWebHistory } from "vue-router";

import { USER_ROLES } from "../domain/enums";
import { useAuthStore } from "../stores/auth";
import ClientTicketsView from "../views/ClientTicketsView.vue";
import CreateTicketView from "../views/CreateTicketView.vue";
import LoginView from "../views/LoginView.vue";
import ManagerTicketsView from "../views/ManagerTicketsView.vue";
import RegisterView from "../views/RegisterView.vue";
import TicketDetailView from "../views/TicketDetailView.vue";

function homePathByRole(role) {
  return role === USER_ROLES.MANAGER ? "/manager/tickets" : "/client/tickets";
}

const routes = [
  { path: "/login", name: "login", component: LoginView, meta: { guestOnly: true } },
  { path: "/register", name: "register", component: RegisterView, meta: { guestOnly: true } },
  { path: "/client/tickets", name: "client-tickets", component: ClientTicketsView, meta: { requiresAuth: true, role: USER_ROLES.CLIENT } },
  { path: "/client/tickets/new", name: "create-ticket", component: CreateTicketView, meta: { requiresAuth: true, role: USER_ROLES.CLIENT } },
  { path: "/manager/tickets", name: "manager-tickets", component: ManagerTicketsView, meta: { requiresAuth: true, role: USER_ROLES.MANAGER } },
  { path: "/tickets/:id", name: "ticket-detail", component: TicketDetailView, meta: { requiresAuth: true } },
  {
    path: "/",
    name: "home",
    redirect: () => {
      const authStore = useAuthStore();
      if (!authStore.isAuthenticated) {
        return "/login";
      }
      return homePathByRole(authStore.user?.role);
    }
  },
  { path: "/:pathMatch(.*)*", redirect: "/" }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach(async (to) => {
  const authStore = useAuthStore();
  if (authStore.isAuthenticated && !authStore.user) {
    try {
      await authStore.fetchMe();
    } catch (error) {
      authStore.logout();
      return "/login";
    }
  }

  if (to.meta.guestOnly && authStore.isAuthenticated) {
    return homePathByRole(authStore.user?.role);
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return "/login";
  }

  if (to.meta.role && authStore.user?.role !== to.meta.role) {
    return homePathByRole(authStore.user?.role);
  }

  return true;
});

export default router;
