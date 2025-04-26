<template>
    <div class="container mt-4">
      <h2>Tradies Available in {{ location }}</h2>
  
      <div v-for="(tradies, service) in services" :key="service">
        <h3>{{ service }}</h3>
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
    name: 'TradiesByLocation',
    data() {
      return {
        location: '',
        services: {}
      };
    },
    async mounted() {
      this.location = this.$route.params.location;
  
      try {
        const res = await fetch(`http://localhost:5000/tradies/location/${this.location}`, {
          credentials: 'include'
        });
  
        const html = await res.text();
        const jsonStart = html.indexOf('{');
        const data = JSON.parse(html.slice(jsonStart));
  
        this.services = data.services || {};
      } catch (err) {
        console.error('Failed to load tradies by location:', err);
      }
    }
  };
  </script>
  