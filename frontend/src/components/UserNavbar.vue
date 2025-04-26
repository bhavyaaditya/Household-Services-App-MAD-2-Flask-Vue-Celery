<template>
  <nav class="navbar bg-success py-3" >
    <div class="container-fluid d-flex justify-content-between align-items-center w-100">

      <!-- Left Links -->
      <div class="d-flex align-items-center">
        <img class="navbar-brand me-3" src="@/assets/logo_transparent.png" alt="Logo" height="60" />
        <router-link to="/user/dashboard" class="nav-link me-4">Home</router-link>
        <router-link to="/edit_profile" class="nav-link text-black">Edit Profile</router-link>
      </div>

      <!-- Center User Info -->
      <div class="text-center text-black">
        <div>
          <strong>{{ first_name }} {{ last_name }}</strong> (ID: {{ user_id }})
        </div>
        <div style="font-size: 0.9em;">{{ email }}</div>
        <div style="font-size: 0.9em;">{{ location }}</div>
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
  name: 'UserNavbar',
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
        const user_res = await fetch('http://localhost:5000/user/profile', {
          method: 'GET',
          credentials: 'include'
        });
        const user_data_ = await user_res.json();
        const user_data = user_data_.user;
        this.user_id = user_data.id;
        this.first_name = user_data.first_name;
        this.last_name = user_data.last_name;
        this.email = user_data.email;
        this.location = user_data.location;
        this.phone_number = user_data.phone_number;
        console.log('User:', user_data);
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
