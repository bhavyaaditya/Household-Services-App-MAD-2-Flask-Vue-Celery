<template>
    <div class="container mt-5">
      <h2>Edit Profile</h2>
      <form @submit.prevent="submitForm">
        <div class="mb-3">
          <label class="form-label">First Name</label>
          <input v-model="form.first_name" type="text" class="form-control" required />
        </div>
  
        <div class="mb-3">
          <label class="form-label">Last Name</label>
          <input v-model="form.last_name" type="text" class="form-control" required />
        </div>
  
        <div class="mb-3">
          <label class="form-label">Email</label>
          <input v-model="form.email" type="email" class="form-control" required />
        </div>
  
        <div class="mb-3">
          <label class="form-label">Phone Number</label>
          <input v-model="form.phone_number" type="text" class="form-control" />
        </div>
  
        <div class="mb-3">
          <label for="cities" class="form-label">Location</label>
          <select v-model="form.cities" id="cities" class="form-select">
            <option v-for="city in cities" :key="city" :value="city.toLowerCase()">{{ city }}</option>
          </select>
        </div>
  
        <button type="submit" class="btn btn-primary">Save Changes</button>
      </form>
    </div>
  </template>
  
  <script>
  export default {
    name: 'EditUserProfile',
    data() {
      return {
        form: {
          first_name: '',
          last_name: '',
          email: '',
          phone_number: '',
          cities: ''
        },
        cities: []
      };
    },
    async mounted() {
      try {
        const res = await fetch('/edit_profile', {
          credentials: 'include'
        });
        const html = await res.text();
        const jsonStart = html.indexOf('{');
        const data = JSON.parse(html.slice(jsonStart));
        this.form = data.user;
        this.cities = data.cities;
      } catch (err) {
        console.error('Failed to load profile:', err);
      }
    },
    methods: {
      async submitForm() {
        const formData = new FormData();
        for (const key in this.form) formData.append(key, this.form[key]);
  
        try {
          const res = await fetch('/edit_profile', {
            method: 'POST',
            credentials: 'include',
            body: formData
          });
  
          if (res.redirected) {
            window.location.href = res.url;
          } else {
            alert('Profile updated successfully.');
          }
        } catch (err) {
          alert('Failed to update profile.');
        }
      }
    }
  };
  </script>
  