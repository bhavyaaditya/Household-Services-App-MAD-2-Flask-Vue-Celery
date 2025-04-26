<template>
  <AdminNavbar />
  <div class="container mt-5">
    <!-- Analytics PDF Download Button -->
    <div class="mb-4">
        <a href="http://localhost:5000/admin/download/admin_analytics/pdf" class="btn btn-danger">Download Analytics (PDF)</a>
    </div>

    <!--  Celery CSV Download Button -->
    <!-- <div class="mb-5">
      <button @click="startCeleryDownload" class="btn btn-success">CELERY Download Service Requests (CSV)</button>
      <p>{{ downloadStatus }}</p>
      <a v-if="downloadReady" :href="downloadLink" class="btn btn-primary">CELERY Download CSV</a>
    </div> -->

    <!-- Revenue and Service Stats -->
    <div class="row mb-5">
      <div class="col-md-6">
        <div class="card p-3">
          <h4>Total Revenue</h4>
          <h2>₹{{ analytics.total_revenue }}</h2>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card p-3">
          <h4>Total Services Completed</h4>
          <h2>{{ analytics.total_services }}</h2>
        </div>
      </div>
    </div>

    <!-- Location Breakdown -->
    <div class="mb-5">
      <h3>Location-wise Breakdown</h3>
      <table class="table table-striped">
        <thead>
          <tr>
            <th>Location</th>
            <th>Services Completed</th>
            <th>Total Revenue</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in analytics.location_data" :key="index">
            <td>{{ row[0] }}</td>
            <td>{{ row[1] }}</td>
            <td>₹{{ row[2].toFixed(2) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Weekly Chart -->
    <div class="mb-5">
      <h3>Week-wise Performance</h3>
      <canvas ref="weeklyChart"></canvas>
    </div>

    <!-- Monthly Chart -->
    <div>
      <h3>Month-wise Performance</h3>
      <canvas ref="monthlyChart"></canvas>
    </div>
  </div>
</template>

<script>
import Chart from 'chart.js/auto';
import AdminNavbar from './AdminNavbar.vue';

export default {
  name: 'AdminAnalytics',
  data() {
    return {
      analytics: {
        total_revenue: 0,
        total_services: 0,
        location_data: [],
        week_data: [],
        month_data: []
      },
      downloadStatus: '',
      downloadLink: '',
      downloadReady: false
    };
  },
  components: {
    AdminNavbar
  },
  methods: {
    startCeleryDownload() {
      this.downloadStatus = 'Generating CSV...';
      fetch('http://localhost:5000/admin/download/service_requests', 
          { method: 'POST',
            credentials: 'include',
          },
        )
        .then(res => res.json())
        .then(data => this.checkTaskStatus(data.task_id));
    },
    checkTaskStatus(taskId) {
      fetch(`http://localhost:5000/admin/download/service_requests/status/${taskId}`,{
        method: 'GET',
        credentials: 'include',
      })
        .then(res => res.json())
        .then(data => {
          if (data.status === 'Completed') {
            this.downloadStatus = 'CSV Ready!';
            this.downloadLink = 'http://localhost:5000/admin/download/service_requests/file';
            this.downloadReady = true;
          } else if (data.status === 'Failed') {
            this.downloadStatus = 'Failed to generate CSV.';
          } else {
            setTimeout(() => this.checkTaskStatus(taskId), 1000);
          }
        });
    },
    renderChart(refName, data) {
      const ctx = this.$refs[refName];
      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: data.map(row => row.label || row[0]),
          datasets: [
            {
              label: 'Revenue Earned (₹)',
              data: data.map(row => row.revenue || row[2]),
              type: 'bar',
              yAxisID: 'y',
            },
            {
              label: 'Services Completed',
              data: data.map(row => row.services || row[1]),
              type: 'line',
              yAxisID: 'y1',
              fill: false
            }
          ]
        },
        options: {
          responsive: true,
          scales: {
            y: {
              type: 'linear',
              position: 'left',
              title: { display: true, text: 'Revenue Earned (₹)' }
            },
            y1: {
              type: 'linear',
              position: 'right',
              title: { display: true, text: 'Services Completed' },
              grid: { drawOnChartArea: false }
            }
          }
        }
      });
    }
  },
  mounted() {
    fetch('http://localhost:5000/admin/analytics', {
      method: 'GET',
      credentials: 'include'
    })
      .then(res => res.json())
      .then(data => {
        this.analytics.total_revenue = data.total_revenue;
        this.analytics.total_services = data.total_services;
        this.analytics.location_data = data.location_data;
        this.analytics.week_data = data.week_data;
        this.analytics.month_data = data.month_data;

        this.renderChart('weeklyChart', this.analytics.week_data);
        this.renderChart('monthlyChart', this.analytics.month_data);
      });
  }
};
</script>
