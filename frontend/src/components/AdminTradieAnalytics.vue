<template>
  <div class="container mt-4">
    <h3>Tradie Analytics - Admin View</h3>

    <div class="mt-3">
      <h5>Tradie Info</h5>
      <ul>
        <li><strong>Name:</strong> {{ tradie.first_name }} {{ tradie.last_name }}</li>
        <li><strong>Email:</strong> {{ tradie.email }}</li>
        <li><strong>Phone:</strong> {{ tradie.phone_number }}</li>
        <li><strong>Location:</strong> {{ tradie.location }}</li>
      </ul>
    </div>

    <div class="analytics-summary mt-4">
      <p><strong>Total Revenue:</strong> ₹{{ analytics.total_revenue }}</p>
      <p><strong>Total Services Completed:</strong> {{ analytics.total_services }}</p>
      <p><strong>Average Rating:</strong> {{ analytics.average_rating || 'NA' }}</p>
    </div>

    <div class="location-analytics mt-4">
      <h5>Location-wise Analytics</h5>
      <table class="table">
        <thead>
          <tr>
            <th>Location</th>
            <th>Services</th>
            <th>Revenue (₹)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="loc in analytics.location_data" :key="loc[0]">
            <td>{{ loc[0] }}</td>
            <td>{{ loc[1] }}</td>
            <td>{{ loc[2].toFixed(2) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="graph-section mt-4">
      <h5>Weekly Revenue & Services</h5>
      <canvas id="weeklyChart"></canvas>
    </div>

    <div class="graph-section mt-4">
      <h5>Monthly Revenue & Services</h5>
      <canvas id="monthlyChart"></canvas>
    </div>

    <div class="reviews-section mt-5">
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
import Chart from 'chart.js/auto';

export default {
  data() {
    return {
      tradie: {},
      analytics: {
        total_revenue: 0,
        total_services: 0,
        average_rating: null,
        location_data: [],
        reviews: [],
        week_data: [],
        month_data: []
      }
    };
  },
  mounted() {
    const tradieId = this.$route.params.tradie_id;
    fetch(`http://localhost:5000/admin/tradie/${tradieId}/analytics`, {
      method: 'GET',
      credentials: 'include'
    })
      .then(res => res.json())
      .then(data => {
        this.tradie = data.tradie;
        this.analytics.total_revenue = data.total_revenue;
        this.analytics.total_services = data.total_services;
        this.analytics.average_rating = data.average_rating;
        this.analytics.location_data = data.location_data;
        this.analytics.reviews = data.reviews;
        this.analytics.week_data = data.week_data;
        this.analytics.month_data = data.month_data;
        this.renderCharts();
      })
      .catch(err => console.error('Error fetching tradie analytics:', err));
  },
  methods: {
    renderCharts() {
      const weeklyChart = document.getElementById('weeklyChart');
      const monthlyChart = document.getElementById('monthlyChart');

      new Chart(weeklyChart, {
        type: 'bar',
        data: {
          labels: this.analytics.week_data.map(d => d.label),
          datasets: [
            {
              label: 'Revenue (₹)',
              data: this.analytics.week_data.map(d => d.revenue),
              yAxisID: 'y1'
            },
            {
              label: 'Services Completed',
              data: this.analytics.week_data.map(d => d.services),
              type: 'line',
              yAxisID: 'y2'
            }
          ]
        },
        options: {
          responsive: true,
          scales: {
            y1: {
              position: 'left',
              title: { display: true, text: 'Revenue (₹)' }
            },
            y2: {
              position: 'right',
              grid: { drawOnChartArea: false },
              title: { display: true, text: 'Services Completed' }
            }
          }
        }
      });

      new Chart(monthlyChart, {
        type: 'bar',
        data: {
          labels: this.analytics.month_data.map(d => d.label),
          datasets: [
            {
              label: 'Revenue (₹)',
              data: this.analytics.month_data.map(d => d.revenue),
              yAxisID: 'y1'
            },
            {
              label: 'Services Completed',
              data: this.analytics.month_data.map(d => d.services),
              type: 'line',
              yAxisID: 'y2'
            }
          ]
        },
        options: {
          responsive: true,
          scales: {
            y1: {
              position: 'left',
              title: { display: true, text: 'Revenue (₹)' }
            },
            y2: {
              position: 'right',
              grid: { drawOnChartArea: false },
              title: { display: true, text: 'Services Completed' }
            }
          }
        }
      });
    }
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
.location-analytics .table {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>
