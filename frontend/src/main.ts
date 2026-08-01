import "./assets/global.css";

import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import WebApp from "@twa-dev/sdk";
import "virtual:svg-icons-register";
import { ensureAuthenticated } from "@/api/apiClient";

WebApp.ready();

ensureAuthenticated()
  .catch((err) => {
    console.error("Initial login failed:", err);
  })
  .finally(() => {
    const app = createApp(App);
    app.use(router);
    app.mount("#app");
  });
