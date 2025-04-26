<template>
    <nav class="navbar bg-warning py-3" >
      <div class="container-fluid d-flex justify-content-between align-items-center w-100">
  
        <!-- Left Links -->
        <div class="d-flex align-items-center">
          <img class="navbar-brand me-3" src="@/assets/logo_transparent.png" alt="Logo" height="60" />
          <a class="nav-link me-4" href="/tradie/dashboard">Home</a>
          <router-link to="/edit_profile" class="nav-link text-black">Edit Profile</router-link>
        </div>
  
        <!-- Center User Info -->
        <div class="text-center text-black">
          <div>
            <strong>{{ first_name }} {{ last_name }}</strong> (ID: {{ user_id }})
          </div>
          <div style="font-size: 0.9em;">{{ email }}</div>
          <div style="font-size: 0.9em;">{{ location }}</div>
          <div style="font-size: 0.9em;" class="btn btn-dark">Service Category: {{ service_category }}</div>
        </div>
  
        <!-- Right Logout -->
        <div>
          <a class="nav-link text-black" href="/logout" @click.prevent="logout">Logout</a>
        </div>
  
      </div>
    </nav>
  </template>
  
  <script>
  export default {
    name: 'TradieNavbar',
    data() {
      return {
        user_id: null,
        email: "",
        first_name: "",
        last_name: "",
        location: "",
        phone_number: "",
      };
    },
    methods: {
      async logout() {
        try {
          const res = await fetch('http://localhost:5000/logout', {
            method: 'POST',
            credentials: 'include'
          });
          // const result = await res.json();
          // if (result.message === 'Successfully logged out') {
          //   window.location.href = 'http://localhost:8080/login';
          // }
          this.$router.push('/login');
        } catch (err) {
          console.error('Logout failed:', err);
        }
      },
      async userDetails() {
        try {
          const tradie_res = await fetch('http://localhost:5000/tradie/profile', {
            method: 'GET',
            credentials: 'include'
          });
          const tradie_data_ = await tradie_res.json();
          console.log('Tradie Data:', tradie_data_);
          const tradie_data = tradie_data_.tradie;
          this.user_id = tradie_data.id;
          this.first_name = tradie_data.first_name;
          this.last_name = tradie_data.last_name;
          this.email = tradie_data.email;
          this.location = tradie_data.location;
          this.phone_number = tradie_data.phone_number;
          this.service_category = tradie_data.service_categories[0].name;
          console.log('Tradie:', tradie_data);
        } catch (err) {
          console.error('Error in fetching user details: ', err);
        }
      }
    },
    mounted() {
      this.userDetails();
    }
  };
  </script>
  