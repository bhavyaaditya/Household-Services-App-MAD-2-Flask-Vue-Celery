<template>
  <div class="container mt-4" v-if="tradie">
    <h2>{{ tradie.first_name }} {{ tradie.last_name }}</h2>
    <p><strong>Email:</strong> {{ tradie.email }}</p>
    <p><strong>Location:</strong> {{ tradie.location }}</p>
    <p><strong>Hourly Rate:</strong> ₹{{ tradie.hourly_rate }}</p>
    <p><strong>Years of Experience:</strong> {{ tradie.years_of_experience }}</p>

    <h4>Services Provided:</h4>
    <ul>
      <li v-for="service in tradie.service_categories" :key="service.id">{{ service.name }}</li>
    </ul>

    <hr v-if="showForm" />
    <div v-if="showForm">
      <h3>Request Service from {{ tradie.first_name }}</h3>
      <form @submit.prevent="submitRequest">
        <label for="service_id">Select Service:</label>
        <select class="form-control" v-model="form.service_id" required>
          <option v-for="service in tradie.service_categories" :key="service.id" :value="service.id">
            {{ service.name }}
          </option>
        </select>

        <label for="due_date">Due Date:</label>
        <input type="date" class="form-control" v-model="form.due_date" required>

        <label for="description">Description:</label>
        <textarea class="form-control" v-model="form.description" required></textarea>

        <label for="location">Location:</label>
        <select id="location" class="form-control" v-model="form.location">
          <option v-for="city in cities" :key="city" :value="city">
            {{ city }}
          </option>
        </select>

        <br />
        <label for="estimated_hours">Estimated Hours:</label>
        <input type="number" class="form-control" v-model.number="form.estimated_hours" step="0.1" required>

        <label for="hourly_rate">Hourly Rate (Min: ₹{{ tradie.hourly_rate }}):</label>
        <input
          type="number"
          class="form-control"
          v-model.number="form.hourly_rate"
          step="0.5"
          :min="tradie.hourly_rate"
          required
        >

        <label for="total_cost">Total Cost:</label>
        <input type="text" class="form-control" :value="totalCost.toFixed(2)" readonly>

        <button type="submit" class="btn btn-primary mt-2">Request Tradie</button>
      </form>
    </div>
  </div>
  <div class="container mt-4" v-else>
    Loading tradie details...
  </div>
</template>

<script>
export default {
  name: 'ViewTradie',
  data() {
    return {
      tradie: null,
      cities: [],
      form: {
        service_id: '',
        due_date: '',
        description: '',
        location: '',
        estimated_hours: 0,
        hourly_rate: 0
      },
      showForm: false
    };
  },
  computed: {
    totalCost() {
      return this.form.estimated_hours * this.form.hourly_rate;
    }
  },
  async mounted() {
    const tradieId = this.$route.params.tradie_id;
    try {
      const res = await fetch(`http://localhost:5000/tradie/${tradieId}`, {  // Corrected backend URL here
        credentials: 'include'
      });
      const data = await res.json();

      this.tradie = data.tradie;
      this.cities = data.cities;
      this.showForm = data.showForm;
      this.form.location = this.tradie.location || '';
      this.form.hourly_rate = this.tradie.hourly_rate;
    } catch (err) {
      console.error('Failed to load tradie profile:', err);
    }
  },
  methods: {
    async submitRequest() {
      const formData = new FormData();
      for (const key in this.form) formData.append(key, this.form[key]);

      const tradieId = this.$route.params.tradie_id;

      try {
        const res = await fetch(`http://localhost:5000/tradie/${tradieId}`, {
          method: 'POST',
          credentials: 'include',
          body: formData
        });

        const result = await res.json();

        if (result.status === 'success') {
          this.$router.push('/user/dashboard');  // Redirects to user dashboard
        } else {
          alert('Failed to submit request.');
        }
      } catch (err) {
        alert('Request failed.');
      }
    }
  }
};
</script>