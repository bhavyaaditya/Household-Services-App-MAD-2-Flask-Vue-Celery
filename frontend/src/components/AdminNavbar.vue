<template>
    <nav class="navbar navbar-expand-lg navbar-light bg-dark mb-4">
      <div class="container-fluid">
        <img class="navbar-brand me-3" src="@/assets/logo_transparent.png" alt="Logo" height="60" />
        <div class="text-center text-light mx-5"><h5>Admin Dashboard</h5></div>
        <div class="d-flex align-items-center ms-auto">
          <router-link
            class="btn btn-outline-success me-2"
            :to="toggleRoute"
          >
            {{ toggleLabel }}
          </router-link>
          <button class="btn btn-outline-danger" @click.prevent="logout">Logout</button>
        </div>
      </div>
    </nav>
  </template>
  
  <script>
  export default {
    name: "AdminNavbar",
    computed: {
      toggleRoute() {
        return this.$route.path === '/admin/dashboard' ? '/admin/analytics' : '/admin/dashboard';
      },
      toggleLabel() {
        return this.$route.path === '/admin/dashboard' ? 'Analytics' : 'Dashboard';
      }
    },
    methods: {
      async logout() {
        try {
          await fetch('http://localhost:5000/logout', {
            method: 'POST',
            credentials: 'include'
          });
          this.$router.push('/login');
        } catch (err) {
          console.error("Logout error:", err);
          this.$router.push('/login');
        }
      }
    }
  };
  </script>
  