<template>
    <AdminNavbar />
    <div class="container mt-5">
      <h1>Admin Dashboard</h1>

      <div class="mb-4">
        <!-- <a href="http://localhost:5000/download/service_requests/csv" class="btn btn-warning me-2">Download Service Requests (CSV)</a> -->
        <button class="btn btn-warning me-2" @click="downloadCSV">Download Service Requests (CSV)</button>
        <p v-if="isGenerating" class="mt-2 text-success">Generating CSV file...</p>
      </div>

  
      <!-- Tradies Section -->
      <section class="mt-5">
        <AdminTradieTable :tradies="tradies" @status-updated="fetchData" />
      </section>
  
      <!-- Services Section -->
      <section class="mt-5">
        <AdminServicesTable :services="services" @edit-service="openEditModal" @refresh="fetchData"/>
        <button class="btn btn-success mt-3" @click="showAddServiceModal = true">
          Create Service
        </button>
      </section>
  
      <!-- Users Section -->
      <section class="mt-5">
        <AdminUserTable :users="users" @status-updated="fetchData" />
      </section>
  
      <!-- Edit Modal -->
      <AdminEditServiceModal
        v-if="selectedService"
        :key="selectedService.id + '_' + modalVersion"
        :service="selectedService"
        @close="selectedService = null"
        @saved="handleServiceUpdate"
      />
  
      <!-- Add Modal -->
      <AdminAddServiceModal
        v-if="showAddServiceModal"
        @close="showAddServiceModal = false"
        @added="handleServiceAdded"
      />
    </div>
  </template>
  
  <script>
  import AdminTradieTable from './partials/AdminTradieTable.vue'
  import AdminServicesTable from './partials/AdminServicesTable.vue'
  import AdminUserTable from './partials/AdminUserTable.vue'
  import AdminEditServiceModal from './partials/AdminEditServiceModal.vue'
  import AdminAddServiceModal from './partials/AdminAddServiceModal.vue'
  import AdminNavbar from './AdminNavbar.vue'
  
  export default {
    name: 'AdminDashboard',
    components: {
      AdminTradieTable,
      AdminServicesTable,
      AdminUserTable,
      AdminEditServiceModal,
      AdminAddServiceModal,
      AdminNavbar
    },
    data() {
      return {
        tradies: [],
        users: [],
        services: [],
        selectedService: null,
        showAddServiceModal: false,
        modalVersion: 0,
        isGenerating: false,
      };
    },
    methods: {
      // This method is called initially to get the data from backend. It is also called when a new service is added. Without this, once a service is edited, the new details of that service are not visible unless the page is refreshed. This method captures the `$emit('refresh')` event from the `AdminEditServiceModal` component and fetches the updated data.
      async fetchData() {
        try {
          const res = await fetch('http://localhost:5000/admin/dashboard/', {
            credentials: 'include'
          });
          // const html = await res.text();
          // const jsonStart = html.indexOf('{');
          // const { tradies, users, services } = JSON.parse(html.slice(jsonStart));
          const data = await res.json();
          const { tradies, users, services } = data;
          console.log(services);
          this.tradies = tradies;
          this.users = users;
          this.services = services;
        } catch (err) {
          console.error('Error fetching admin dashboard data:', err);
        }
      },
      openEditModal(service) {
        this.selectedService = service;
        this.modalVersion += 1;
        console.log("MODAL VERSION from open: ", this.modalVersion);
      },
      handleServiceUpdate() {
        this.selectedService = null;
        this.fetchData();
      },
      handleServiceAdded() {
        this.showAddServiceModal = false;
        this.fetchData();
      },
      downloadCSV() {
        this.isGenerating = true;
        setTimeout(() => {
          this.isGenerating = false;
          window.location.href = 'http://localhost:5000/download/service_requests/csv'; 
        }, 5000);
      }
    },
    mounted() {
      this.fetchData();
      console.log("MODAL VERSION from dash mounted: ", this.modalVersion);
    }
  };
  </script>
  