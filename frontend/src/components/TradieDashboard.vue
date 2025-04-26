<template>
  <TradieNavbar />
  <div v-if="!activated" class="alert alert-warning text-center">
    Your account has been deactivated by the admin. You can still view your dashboard, but cannot apply to or receive new service requests.
  </div>
  <div class="container mt-5" v-if="loaded">
    <!-- ALERT if tradie has no activated service -->
    <div v-if="needsServiceSelection" class="alert alert-warning">
      Your current service category has been removed. Please select a new one in your
      <router-link to="/tradie/edit_profile">profile settings</router-link>.
    </div>

    <!-- REQUESTED REQUESTS -->
    <h2>Service Requests Requested for You</h2>
    <RequestTable :requests="requested_requests" :appliedIds="applied_request_ids" @apply="openApplyModal" @refresh="fetchDashboard" />

    <!-- AVAILABLE REQUESTS -->
    <div v-if="activated">
      <h2 class="mt-5">Available Service Requests</h2>
      <RequestTable
        :requests="available_service_requests"
        :appliedIds="applied_request_ids"
        :serviceName="service_name"
        @apply="openApplyModal"
        @refresh="fetchDashboard"
      />
    </div>
    <div v-else class="mt-4 alert alert-warning">
      You have been flagged by the admin and cannot view open service requests
    </div>

    <!-- APPLIED REQUESTS -->
    <h2 class="mt-5">Service Requests You've Applied For</h2>
    <RequestTable :requests="applied_service_requests" :serviceName="service_name" viewOnly />

    <!-- BOOKED REQUESTS -->
    <h2 class="mt-5">Booked Service Requests</h2>
    <BookedTable :requests="booked_requests" @complete="openCompleteModal" @refresh="fetchDashboard" />

    <!-- COMPLETED REQUESTS -->
    <h2 class="mt-5">Completed Service Requests</h2>
    <CompletedTable :requests="completed_requests" />

    <!-- Apply Confirmation Modal -->
    <div class="modal fade" id="applyRequestModal" tabindex="-1" aria-hidden="true" ref="applyModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Confirm Application</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            Are you sure you want to apply for <strong>{{ selectedRequestName }}</strong>?
          </div>
          <div class="modal-footer">
            <button class="btn btn-success" @click="confirmApply">Yes, Apply</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Complete Modal -->
    <div class="modal fade" id="completeRequestModal" tabindex="-1" aria-hidden="true" ref="completeModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Complete Service Request</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            Are you sure you want to mark <strong>{{ selectedRequestName }}</strong> as completed?
          </div>
          <div class="modal-footer">
            <button class="btn btn-success" @click="confirmComplete">Yes, Mark as Completed</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import RequestTable from './partials/RequestTable.vue';
import BookedTable from './partials/BookedTable.vue';
import CompletedTable from './partials/CompletedTable.vue';
import TradieNavbar from './TradieNavbar.vue';
import { Modal } from 'bootstrap';

export default {
  name: "TradieDashboard",
  components: { RequestTable, BookedTable, CompletedTable, TradieNavbar },
  data() {
    return {
      requested_requests: [],
      available_service_requests: [],
      applied_service_requests: [],
      booked_requests: [],
      completed_requests: [],
      applied_request_ids: [],
      service_name: '',
      activated: true,
      loaded: false,
      needsServiceSelection: false,

      showApplyModal: false,
      showCompleteModal: false,
      selectedRequestId: null,
      selectedRequestName: '',

      first_name: '',
      last_name: '',
      email: '',
      hourly_rate: 0,
      years_of_experience: 0,
      location: '',

      applyModalInstance: null,
      completeModalInstance: null
    };
  },
  methods: {
    openApplyModal({ id, name }) {
      this.selectedRequestId = id;
      this.selectedRequestName = name;
      if (!this.applyModalInstance) {
        this.applyModalInstance = new Modal(this.$refs.applyModal);
      }
      this.applyModalInstance.show();
    },
    async confirmApply() {
      try {
        const formData = new FormData();
        formData.append("request_id", this.selectedRequestId);

        const res = await fetch("http://localhost:5000/apply_request", {
          method: "POST",
          credentials: "include",
          body: formData
        });

        const data = await res.json();
        if (data.status === "success") {
          this.fetchDashboard();
          this.applyModalInstance.hide();
        } else {
          alert(data.message || "Failed to apply.");
        }
      } catch {
        alert("Error applying for request.");
      }
    },
    openCompleteModal({ id, name }) {
      this.selectedRequestId = id;
      this.selectedRequestName = name;
      if (!this.completeModalInstance) {
        this.completeModalInstance = new Modal(this.$refs.completeModal);
      }
      this.completeModalInstance.show();
    },
    async confirmComplete() {
      try {
        const res = await fetch(`http://localhost:5000/tradie/complete_service/${this.selectedRequestId}`, {
          method: "POST",
          credentials: "include"
        });

        if (res.redirected) {
          window.location.href = res.url;
        } else {
          alert("Marked as completed.");
          this.fetchDashboard();
          this.completeModalInstance.hide();
        }
      } catch {
        alert("Error completing request.");
      }
    },
    async fetchDashboard() {
      try {
        const res = await fetch("http://localhost:5000/tradie/dashboard", {
          credentials: "include"
        });
        const data = await res.json();

        this.requested_requests = data.requested_requests;
        this.available_service_requests = data.available_service_requests;
        this.applied_service_requests = data.applied_service_requests;
        this.applied_request_ids = data.applied_service_requests_ids;
        this.booked_requests = data.booked_requests;
        console.log("Booked requests: ", this.booked_requests);
        this.completed_requests = data.completed_requests;
        this.service_name = data.service_name;
        this.needsServiceSelection = data.needs_service_selection;
        this.loaded = true;

        this.first_name = data.tradie.first_name;
        this.last_name = data.tradie.last_name;
        this.email = data.tradie.email;
        this.hourly_rate = data.tradie.hourly_rate;
        this.years_of_experience = data.tradie.years_of_experience;
        this.location = data.tradie.location;
        this.activated = Boolean(data.tradie.activated);

        console.log("Tradie data: ", data);
        console.log("activated status (this): ", this.activated);
        console.log("activated status (data): ", data.tradie.activated);
      } catch (err) {
        console.error("Failed to load tradie dashboard:", err);
      }
    }
  },
  mounted() {
    this.fetchDashboard();
  }
};
</script>