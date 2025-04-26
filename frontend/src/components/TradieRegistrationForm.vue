<template>
  <AuthNavbar />
    <div class="container mt-5">
      <h3 class="mb-4">Tradie Registration</h3>
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
          <select v-model="form.cities" class="form-select" required>
            <option disabled selected value="">Choose City</option>
            <option v-for="city in cities" :key="city" :value="city">{{ city }}</option>
          </select>
        </div>
        <div class="mb-3">
          <label class="form-label">Service Category</label>
          <select v-model="form.service_category" class="form-select" required>
            <option v-for="service in services" :key="service" :value="service">{{ service }}</option>
          </select>
          <div class="mb-3">
            <label class="form-label">Hourly Rate</label>
            <input 
              v-model="form.hourly_rate" 
              type="number" 
              :min="getBasePrice(form.service_category)" 
              class="form-control" 
              required 
            />
            <small v-if="form.service_category" class="text-muted">
              Minimum hourly rate: {{ getBasePrice(form.service_category) }}
            </small>
          </div>
        </div>
        <div class="mb-3">
          <label class="form-label">Years of Experience</label>
          <input v-model="form.years_of_experience" type="number" min="0" class="form-control" required />
        </div>
        <button class="btn btn-primary" type="submit">Register</button>
        <div v-if="error" class="alert alert-danger mt-3">{{ error }}</div>
      </form>
    </div>
  </template>
  
  <script>
import AuthNavbar from './AuthNavbar.vue';

  export default {
    name: 'TradieRegistrationForm',
    data() {
      return {
        cities: [],
        services: [],
        serviceBasePrices: {},
        form: {
          email: '',
          password: '',
          first_name: '',
          last_name: '',
          phone_number: '',
          address: '',
          cities: '',
          service_category: '',
          years_of_experience: 0,
          hourly_rate: 0
        },
        error: ''
      };
    },
    components: {
      AuthNavbar
    },
    async mounted() {
      try {
        const [citiesRes, servicesRes] = await Promise.all([
          fetch('http://localhost:5000/api/cities'),
          fetch('http://localhost:5000/api/services')
        ]);
        this.cities = await citiesRes.json();
        const servicesData = await servicesRes.json();
        this.services = servicesData.map(service => service.name);
        this.serviceBasePrices = servicesData.reduce((acc, service) => {
          acc[service.name] = service.base_price; // Map service name to its base price
          return acc;
        }, {});
      } catch (e) {
        this.error = 'Failed to load dropdown values.';
      }
    },
    methods: {
      getBasePrice(serviceName) {
        return this.serviceBasePrices[serviceName] || 0; // Return base price or 0 if not found
      },
      async handleSubmit() {
        const formData = new FormData();
        for (const key in this.form) formData.append(key, this.form[key]);
  
        try {
          const res = await fetch('http://localhost:5000/register/tradie', {
            method: 'POST',
            credentials: 'include',
            body: formData
          });
          const data = await res.json();
          if (!res.ok) this.error = data.message;
          else alert('Tradie registered successfully!');
          this.$router.push('/login');
        } catch (err) {
          this.error = 'Something went wrong.';
        }
      }
    }
  };
  </script>
  
  