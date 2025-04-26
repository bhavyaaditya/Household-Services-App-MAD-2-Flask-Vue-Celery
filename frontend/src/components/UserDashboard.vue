<template>
  <UserNavbar />
  <div v-if="!activated" class="alert alert-warning text-center">
    Your account has been deactivated by the admin. You can view past service requests but cannot create new ones.
  </div>
  <div class="container mt-4">
    <!-- Search Bar -->
    <form @submit.prevent="handleSearch">
      <div class="input-group mb-3">
        <input v-model="searchQuery" type="text" class="form-control" placeholder="Search locations, services, or tradies" required>
        <button class="btn btn-primary" type="submit">Search</button>
      </div>
      <div class="form-check form-check-inline" v-for="filter in ['location', 'service', 'tradie']" :key="filter">
        <input class="form-check-input" type="checkbox" v-model="selectedFilters" :value="filter" :id="filter">
        <label class="form-check-label" :for="filter">{{ filter.charAt(0).toUpperCase() + filter.slice(1) }}</label>
      </div>
    </form>

    <!-- Available Services -->
    <div class="mt-5">
      <h2>Available Services</h2>
      <table class="table table-striped table-bordered">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Description</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="service in services" :key="service.id">
            <td>{{ service.id }}</td>
            <td>{{ service.name }}</td>
            <td>{{ service.description }}</td>
            <td>
              <div v-if="activated">
                <button class="btn btn-primary btn-sm" @click="openCreateModal(service)">
                  Create Request
                </button>
              </div>
              <div v-else class="text-muted">
              <p>You cannot create service requests because your account has been deactivated.</p>
            </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Service Requests by Status -->
    <div class="mt-5" v-for="status in statuses" :key="status">
      <h2>{{ formatStatus(status) }} Service Requests</h2>
      <table class="table table-striped table-bordered">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Tradie Name</th>
            <th>Location</th>
            <th>Description</th>
            <th>Created On</th>
            <th>Due Date</th>
            <th v-if="status === 'open'">Action</th>
            <th v-if="status === 'completed'">Review</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="req in serviceRequestsByStatus(status)" :key="req.id">
            <td>{{ req.id }}</td>
            <td>{{ req.service_name }}</td>
            <td>{{ req.tradie_name || 'N/A' }}</td>
            <td>{{ req.location }}</td>
            <td>{{ req.description }}</td>
            <td>{{ req.created_date }}</td>
            <td>{{ req.due_date || 'N/A' }}</td>
            <td v-if="status === 'open'">
              <button class="btn btn-danger btn-sm" @click="confirmCancel(req.id)">Cancel</button>
              <router-link class="btn btn-warning btn-sm ms-2" :to="`/view_applications/${req.id}`">View Applicants</router-link>
            </td>
            <td v-if="status === 'completed'">
              <router-link
                class="btn btn-sm"
                :class="req.review ? 'btn-success' : 'btn-warning'"
                :to="req.review ? `/review/user_view/${req.id}` : `/review/make/${req.id}`"
              >
                {{ req.review ? 'View Review' : 'Leave a Review' }}
              </router-link>

            </td>
          </tr>
        </tbody>
      </table>
    </div>


    <!-- Create Request Modal -->
    <div class="modal fade" id="createRequestModal" tabindex="-1" role="dialog">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <form @submit.prevent="submitCreateRequest">
            <div class="modal-header">
              <h5 class="modal-title">
                Create Service Request - <strong>{{ modalData.serviceName }}</strong>
              </h5>
              <button type="button" class="close" data-bs-dismiss="modal">
                <span>&times;</span>
              </button>
            </div>
            <div class="modal-body">
              <input type="hidden" v-model="modalData.serviceId" />

              <div class="form-group">
                <label for="requestLocation">Location</label>
                <select v-model="modalData.location" class="form-control" required>
                  <option v-for="city in cities" :key="city" :value="city">{{ city }}</option>
                </select>
              </div>

              <div class="form-group">
                <label>Description</label>
                <textarea v-model="modalData.description" class="form-control" rows="3" required></textarea>
              </div>

              <div class="form-group">
                <label>Due Date</label>
                <input type="date" v-model="modalData.dueDate" class="form-control" required />
              </div>

              <div class="form-group">
                <label>Hourly Rate (₹)</label>
                <input type="number" v-model.number="modalData.hourly_rate" class="form-control"
                  :min="modalData.basePrice" @input="calculateTotal" required />
              </div>

              <div class="form-group">
                <label>Estimated Hours</label>
                <input type="number" v-model.number="modalData.hours" class="form-control"
                  step="0.5" @input="calculateTotal" required />
              </div>

              <div class="form-group">
                <label>Total Cost</label>
                <input type="text" class="form-control" :value="modalData.totalCost.toFixed(2)" readonly />
              </div>
            </div>

            <div class="modal-footer">
              <button class="btn btn-success" type="submit">Submit Request</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import UserNavbar from './UserNavbar.vue';
import { Modal } from 'bootstrap';

export default {
name: 'UserDashboard',
data() {
  return {
    searchQuery: '',
    selectedFilters: ['location', 'service', 'tradie'],
    services: [],
    serviceRequests: [],
    statuses: ['open', 'booked', 'due_today', 'completed'],
    defaultLocation: '',
    activated: true,

    cities: [],
    modalData: {
      serviceId: null,
      serviceName: '',
      basePrice: 0,
      location: '',
      description: '',
      dueDate: '',
      hourly_rate: 0,
      hours: 0,
      totalCost: 0
    }
  };
},
components: {
  UserNavbar
},
methods: {
  async fetchData() {
    try {
      const response = await fetch("http://localhost:5000/user/dashboard", {
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error(`HTTP status: ${response.status}`);
      }

      const data = await response.json();
      this.serviceRequests = data.service_requests;
      console.log(this.serviceRequests);
      this.services = data.services;
      this.cities = data.cities;
      this.activated = Boolean(data.activated);
      console.log(this.activated);

      if (data.user && data.user.location) {
        this.defaultLocation = data.user.location;
      }
    } catch (error) {
      console.error("Error in /user/dashboard:", error);
    }
  },
  formatStatus(status) {
    return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  },
  serviceRequestsByStatus(status) {
    return this.serviceRequests.filter(req => req.status === status);
  },
  async confirmCancel(requestId) {
    const formData = new FormData();
    formData.append('request_id', requestId);

    const res = await fetch('http://localhost:5000/cancel_request', {
      method: 'POST',
      credentials: 'include',
      body: formData
    });
    const result = await res.json();
    if (result.status === 'success') this.fetchData();
    else alert('Failed to cancel request.');
  },
  handleSearch() {
    const params = new URLSearchParams({ q: this.searchQuery });
    this.selectedFilters.forEach(filter => params.append('filter', filter));
    this.$router.push(`/search?${params.toString()}`);
  },

  openCreateModal(service) {
    this.modalData.serviceId = service.id;
    this.modalData.serviceName = service.name;
    this.modalData.basePrice = service.base_price;
    this.modalData.hourly_rate = service.base_price;
    this.modalData.location = this.defaultLocation;
    this.modalData.description = '';
    this.modalData.dueDate = '';
    this.modalData.hours = 0;
    this.modalData.totalCost = 0;
    const modal = new Modal(document.getElementById("createRequestModal"));
    modal.show();
  },
  calculateTotal() {
    const { hourly_rate, hours } = this.modalData;
    this.modalData.totalCost = (hourly_rate || 0) * (hours || 0);
  },
  async submitCreateRequest() {
    try {
      const formData = new FormData();
      formData.append('service_id', this.modalData.serviceId);
      formData.append('location', this.modalData.location);
      formData.append('description', this.modalData.description);
      formData.append('due_date', this.modalData.dueDate);
      formData.append('estimated_hours', this.modalData.hours);
      formData.append('total_cost', this.modalData.totalCost);
      formData.append('hourly_rate', this.modalData.hourly_rate);

      const res = await fetch('http://localhost:5000/create_request', {
        method: 'POST',
        credentials: 'include',
        body: formData
      });
      const result = await res.json();
      if (result.status === 'success') {
        location.reload();
      } else {
        alert('Failed to create request');
      }
    } catch (err) {
      console.error(err);
      alert('Error occurred');
    }
  }
},
watch: {
  defaultLocation(newVal) {
    if (!this.modalData.location && newVal) {
      this.modalData.location = newVal;
    }
    this.modalData.location = newVal;
  }
},
mounted() {
  this.fetchData();
},
};
</script>
