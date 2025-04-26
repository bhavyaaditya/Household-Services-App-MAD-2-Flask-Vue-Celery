<template>
  <div class="container mt-4">
    <h2>Search Results for "{{ query }}"</h2>

    <!-- Search Filters -->
    <form @change="submitFilters">
      <input type="hidden" name="q" :value="query" />

      <div class="form-check form-check-inline" v-for="filter in allFilters" :key="filter">
        <input
          class="form-check-input"
          type="checkbox"
          :name="'filter'"
          :value="filter"
          v-model="filters"
        />
        <label class="form-check-label">{{ filter.charAt(0).toUpperCase() + filter.slice(1) }}</label>
      </div>
    </form>

    <hr />

    <!-- Locations -->
    <div v-if="filters.includes('location') || filters.length === 0">
      <h3>Matching Locations</h3>
      <table class="table table-striped">
        <thead>
          <tr>
            <th>Location</th>
            <th>Tradie Name</th>
            <th>Service Type</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="tradie in locations" :key="tradie.id">
            <td>
              <router-link :to="`/tradie/${tradie.id}`" v-html="highlight(tradie.location)"></router-link>
            </td>
            <td>{{ tradie.first_name }} {{ tradie.last_name }}</td>
            <td>{{ tradie.service_categories.map(s => s.name).join(', ') }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Services -->
    <div v-if="filters.includes('service') || filters.length === 0">
      <h3>Matching Services</h3>
      <table class="table table-striped">
        <thead><tr><th>Service Name</th></tr></thead>
        <tbody>
          <tr v-for="service in services" :key="service.id">
            <td>
              <router-link :to="`/tradies/service/${service.id}`" v-html="highlight(service.name)"></router-link>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Tradies -->
    <div v-if="filters.includes('tradie') || filters.length === 0">
      <h3>Matching Tradies</h3>
      <table class="table table-striped">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Location</th>
            <th>Years of Experience</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="tradie in tradies" :key="tradie.id">
            <td>
              <router-link :to="`/tradie/${tradie.id}`" v-html="highlight(`${tradie.first_name} ${tradie.last_name}`)"></router-link>
            </td>
            <td>{{ tradie.email }}</td>
            <td>
              <router-link
                v-if="tradie.location"
                :to="`/tradies/location/${tradie.location}`"
                v-html="highlight(tradie.location)"
              ></router-link>
              <span v-else>N/A</span>
            </td>
            <td>{{ tradie.years_of_experience }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SearchResults',
  data() {
    return {
      query: '',
      filters: [],
      allFilters: ['location', 'service', 'tradie'],
      locations: [],
      services: [],
      tradies: []
    };
  },
  async mounted() {
    const urlParams = new URLSearchParams(window.location.search);
    this.query = urlParams.get('q') || '';
    this.filters = urlParams.getAll('filter');

    try {
      const params = new URLSearchParams({ q: this.query });
      this.filters.forEach(filter => params.append('filter', filter));

      const res = await fetch(`http://localhost:5000/search?${params.toString()}`, {
        credentials: 'include'
      });

      const data = await res.json();

      this.locations = data.locations || [];
      this.services = data.services || [];
      this.tradies = data.tradies || [];
    } catch (err) {
      console.error('Failed to load search results:', err);
    }
  },
  methods: {
    submitFilters() {
      const params = new URLSearchParams({ q: this.query });
      this.filters.forEach(filter => params.append('filter', filter));
      this.$router.push(`/search?${params.toString()}`);
    },
    highlight(text) {
      if (!text || !this.query) return text;
      const words = this.query.split(/\s+/).filter(Boolean);
      let result = text;
      words.forEach(word => {
        const regex = new RegExp(`(${word})`, 'gi');
        result = result.replace(regex, '<mark>$1</mark>');
      });
      return result;
    }
  }
};
</script>
