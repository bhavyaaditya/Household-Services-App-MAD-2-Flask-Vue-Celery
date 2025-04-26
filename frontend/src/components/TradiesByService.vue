<template>
    <div class="container mt-4">
      <h2>Tradies Providing {{ serviceName }}</h2>
  
      <div v-for="(tradies, location) in locations" :key="location">
        <h3>{{ location }}</h3>
        <table class="table table-striped">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Years of Experience</th>
              <th>Hourly Rate</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="tradie in tradies" :key="tradie.id">
              <td>
                <a :href="`/tradie/${tradie.id}`">
                  {{ tradie.first_name }} {{ tradie.last_name }}
                </a>
              </td>
              <td>{{ tradie.email }}</td>
              <td>{{ tradie.years_of_experience }}</td>
              <td>₹{{ tradie.hourly_rate }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'TradiesByService',
    data() {
      return {
        serviceName: '',
        locations: {}
      };
    },
    async mounted() {
      const serviceId = this.$route.params.service_id;
  
      try {
        const res = await fetch(`http://localhost:5000/tradies/service/${serviceId}`, {
          credentials: 'include'
        });
  
        const html = await res.text();
        const jsonStart = html.indexOf('{');
        const data = JSON.parse(html.slice(jsonStart));
  
        this.serviceName = data.service.name;
        this.locations = data.locations || {};
      } catch (err) {
        console.error('Failed to load tradies by service:', err);
      }
    }
  };
  </script>
  