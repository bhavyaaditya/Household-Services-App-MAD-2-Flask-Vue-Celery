<template>
  <div>
    <AuthNavbar />
    <div class="container mt-5" style="max-width: 500px;">
      <h2 class="mb-4 text-center">Login</h2>
      <form @submit.prevent="submitForm">
        <div class="mb-3">
          <label for="email" class="form-label">Email address</label>
          <input
            type="email"
            class="form-control"
            id="email"
            v-model="email"
            required
          />
        </div>
        <div class="mb-3">
          <label for="password" class="form-label">Password</label>
          <input
            type="password"
            class="form-control"
            id="password"
            v-model="password"
            required
          />
        </div>
        <div class="d-grid">
          <button type="submit" class="btn btn-primary">Login</button>
        </div>
        <p v-if="errorMessage" class="text-danger mt-3 text-center">{{ errorMessage }}</p>
      </form>
    </div>
  </div>
</template>

<script>
import AuthNavbar from "./AuthNavbar.vue";

export default {
  name: "LoginForm",
  components: {
    AuthNavbar
  },
  data() {
    return {
      email: "",
      password: "",
      errorMessage: ""
    };
  },
  methods: {
    async submitForm() {
      this.errorMessage = "";

      try {
        const response = await fetch("http://localhost:5000/login/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          credentials: "include",
          body: JSON.stringify({
            email: this.email,
            password: this.password
          })
        });

        const data = await response.json();

        if (response.ok && data.redirect_url) {
          this.$router.push(data.redirect_url);
        } else {
          this.errorMessage = data.message || "Login failed. Try again.";
        }
      } catch (error) {
        console.error("Login error:", error);
        this.errorMessage = "Something went wrong. Please try again.";
      }
    }
  }
};
</script>
