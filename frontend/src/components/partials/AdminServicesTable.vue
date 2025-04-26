<template>
  <div class="container mt-5">
    <h2>Services</h2>
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
            <button class="btn btn-primary btn-sm mx-3" @click="openEditModal(service)">
              Edit
            </button>
            <button class="btn btn-danger btn-sm" @click="deleteService(service.id)">
              Delete
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Service Editing Modal -->
    <div v-if="showEditModal" class="modal-backdrop">
      <div class="modal-dialog modal-content p-3">
        <h5>Edit Service</h5>
        <form @submit.prevent="updateService">
          <div class="mb-3">
            <label>Name</label>
            <input type="text" class="form-control" v-model="currentService.name" required />
          </div>
          <div class="mb-3">
            <label>Description</label>
            <textarea class="form-control" v-model="currentService.description" required></textarea>
          </div>
          <button class="btn btn-success">Save Changes</button>
          <button class="btn btn-danger ms-2" @click="closeModal">Cancel</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "ServicesTable",
  props: ["services"],
  data() {
    return {
      showEditModal: false,
      currentService: {}
    };
  },
  methods: {
    openEditModal(service) {
      this.currentService = { ...service };
      this.showEditModal = true;
    },
    closeModal() {
      this.showEditModal = false;
    },
    async updateService() {
      const res = await fetch("http://localhost:5000/update_service", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(this.currentService),
        credentials: "include"
      });
      const data = await res.json();
      if (data.status === "success") {
        this.$emit("refresh");  // Captured by `async fetchData()` in AdminDashboard.vue which then shows the updated services.
        this.closeModal();
      } else {
        alert("Failed to update service");
      }
    },
    async deleteService(serviceId) {
      if (!confirm("Are you sure you want to delete this service?")) return;

      const res = await fetch(`http://localhost:5000/delete_service`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ service_id: serviceId }),
        credentials: "include"
      });

      const data = await res.json();
      if (data.status === "success") {
        this.$emit("refresh");
      } else {
        alert("Failed to delete service");
      }
    }

  }
};
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
}
.modal-dialog {
  background: white;
  border-radius: 8px;
  width: 100%;
  max-width: 500px;
}
</style>
