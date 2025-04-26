<template>
    <nav class="navbar navbar-expand-lg navbar-light bg-light mb-4">
      <div class="container-fluid">
        <!-- <router-link class="navbar-brand fw-bold" to="/">Household Services</router-link> -->
        <router-link to="/login"><img class="navbar-brand me-3 btn btn-danger" src="@/assets/logo_transparent.png" alt="Logo" height="60" /></router-link>
        <div>
          <router-link class="btn btn-outline-primary me-2" to="/register/user">Register as User</router-link>
          <router-link class="btn btn-outline-success" to="/register/tradie">Register as Tradie</router-link>
        </div>
      </div>
    </nav>
  </template>
  
  <script>
  export default {
    name: "AuthNavbar"
  }
  </script>
  