<template>
  <TradieNavbar/>
  <div class="container mt-4">
    <h3>Tradie Analytics</h3>

    <div class="analytics-summary mt-3">
      <p><strong>Total Revenue:</strong> ₹{{ analytics.total_revenue }}</p>
      <p><strong>Total Services Completed:</strong> {{ analytics.total_services }}</p>
      <p><strong>Average Rating:</strong> {{ analytics.average_rating || 'NA' }}</p>
    </div>

    <!-- Location-wise Analytics -->
    <div class="location-analytics mt-4">
      <h5>Location-wise Analytics</h5>
      <table class="table">
        <thead>
          <tr>
            <th>Location</th>
            <th>Services Completed</th>
            <th>Revenue (₹)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="loc in analytics.location_data" :key="loc.location">
            <td>{{ loc.location }}</td>
            <td>{{ loc.services_completed }}</td>
            <td>{{ loc.revenue }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Weekly Analytics -->
    <div class="weekly-analytics mt-4">
      <h5>Weekly Revenue & Services</h5>
      <table class="table">
        <thead>
          <tr>
            <th>Week</th>
            <th>Services Completed</th>
            <th>Revenue (₹)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="week in analytics.week_data" :key="week.label">
            <td>{{ week.label }}</td>
            <td>{{ week.services }}</td>
            <td>{{ week.revenue }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Monthly Analytics -->
    <div class="monthly-analytics mt-4">
      <h5>Monthly Revenue & Services</h5>
      <table class="table">
        <thead>
          <tr>
            <th>Month</th>
            <th>Services Completed</th>
            <th>Revenue (₹)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="month in analytics.month_data" :key="month.label">
            <td>{{ month.label }}</td>
            <td>{{ month.services }}</td>
            <td>{{ month.revenue }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Reviews -->
    <div class="reviews-section mt-4">
      <h5>Service Reviews</h5>
      <div v-if="analytics.reviews.length">
        <div class="card mb-3" v-for="review in analytics.reviews" :key="review.id">
          <div class="card-body">
            <h6 class="card-title">{{ review.service_name }}</h6>
            <p class="card-text"><strong>Rating:</strong> {{ review.rating }}/5</p>
            <p class="card-text">"{{ review.review }}"</p>
            <p class="card-text"><small class="text-muted">Reviewed on {{ review.review_date }}</small></p>
          </div>
        </div>
      </div>
      <div v-else>
        <p>No reviews available.</p>
      </div>
    </div>
  </div>
</template>

<script>
import TradieNavbar from './TradieNavbar.vue';

export default {
  components:{
    TradieNavbar,
  },
  data() {
    return {
      analytics: {
        total_revenue: 0,
        total_services: 0,
        average_rating: null,
        location_data: [],
        week_data: [],
        month_data: [],
        reviews: []
      }
    };
  },
  mounted() {
    fetch('http://localhost:5000/tradie/analytics', {
      method: 'GET',
      credentials: 'include'
    })
      .then(res => res.json())
      .then(data => {
        this.analytics.total_revenue = data.total_revenue;
        this.analytics.total_services = data.total_services;

        this.analytics.location_data = data.location_data.map(loc => ({
          location: loc[0],
          services_completed: loc[1],
          revenue: loc[2].toFixed(2)
        }));

        this.analytics.week_data = data.week_data.map(d => ({
          label: d.label,
          services: d.services,
          revenue: d.revenue.toFixed(2)
        }));

        this.analytics.month_data = data.month_data.map(d => ({
          label: d.label,
          services: d.services,
          revenue: d.revenue.toFixed(2)
        }));

        const ratedServices = data.completed_services.filter(s => s.rating);
        if (ratedServices.length) {
          const totalRating = ratedServices.reduce((sum, s) => sum + s.rating, 0);
          this.analytics.average_rating = (totalRating / ratedServices.length).toFixed(2);

          this.analytics.reviews = ratedServices.map(s => ({
            id: s.id,
            service_name: s.category.name,
            rating: s.rating,
            review: s.review,
            review_date: s.review_date
          }));
        }
      })
      .catch(err => console.error('Error fetching analytics:', err));
  }
};
</script>

<style scoped>
.analytics-summary {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 5px;
}

.reviews-section .card,
.location-analytics .table,
.weekly-analytics .table,
.monthly-analytics .table {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>
