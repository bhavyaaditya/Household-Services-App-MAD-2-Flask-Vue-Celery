<template>
    <AuthNavbar />

    <div class="container mt-5">
      <h3 class="mb-4">User Registration</h3>
      <form @submit.prevent="handleSubmit">
        <div class="mb-3">
          <label class="form-label">Email</label>
          <input v-model="form.email" type="email" class="form-control" required />
        </div>
        <div class="mb-3">
          <label class="form-label">Password</label>
          <input v-model="form.password" type="password" class="form-control" required />
        </div>
        <div class="mb-3">
          <label class="form-label">First Name</label>
          <input v-model="form.first_name" type="text" class="form-control" required />
        </div>
        <div class="mb-3">
          <label class="form-label">Last Name</label>
          <input v-model="form.last_name" type="text" class="form-control" required />
        </div>
        <div class="mb-3">
          <label class="form-label">Phone Number</label>
          <input v-model="form.phone_number" type="tel" class="form-control" />
        </div>
        <div class="mb-3">
          <label class="form-label">Address</label>
          <textarea v-model="form.address" class="form-control" rows="3"></textarea>
        </div>
        <div class="mb-3">
          <label class="form-label">City</label>
          <select v-model="form.cities" class="form-select">
            <option disabled selected value="">Choose City</option>
            <option v-for="city in cities" :key="city" :value="city">{{ city }}</option>
          </select>
        </div>
        <button class="btn btn-primary" type="submit">Register</button>
        <div v-if="error" class="alert alert-danger mt-3">{{ error }}</div>
      </form>
    </div>
  </template>
  
  <script>
  import AuthNavbar from './AuthNavbar.vue';

  export default {
    name: 'UserRegistrationForm',
    data() {
      return {
        form: {
          email: '',
          password: '',
          first_name: '',
          last_name: '',
          phone_number: '',
          address: '',
          cities: ''
        },
        cities: [],
        error: ''
      };
    },
    components: {
      AuthNavbar
    },
    async mounted() {
      try {
        const res = await fetch('http://localhost:5000/api/cities');
        this.cities = await res.json();
      } catch (e) {
        this.error = 'Failed to load cities.';
      }
    },
    methods: {
      async handleSubmit() {
        const formData = new FormData();
        for (const key in this.form) formData.append(key, this.form[key]);
  
        try {
          const res = await fetch('http://localhost:5000/register/user', {
            method: 'POST',
            credentials: 'include',
            body: formData
          });
          const data = await res.json();
          if (!res.ok) this.error = data.message;
          else alert('User registered successfully!');
          this.$router.push('/login');
        } catch (err) {
          this.error = 'Something went wrong.';
        }
      }
    }
  };
  </script>