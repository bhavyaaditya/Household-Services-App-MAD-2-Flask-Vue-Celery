<template>
    <div class="modal-backdrop">
      <div class="modal-dialog modal-content p-4">
        <h5>Add New Service</h5>
        <form @submit.prevent="addService">
          <div class="mb-3">
            <label>Name</label>
            <input type="text" class="form-control" v-model="service.name" required />
          </div>
          <div class="mb-3">
            <label>Description</label>
            <textarea class="form-control" v-model="service.description" required></textarea>
          </div>
          <div class="mb-3">
            <label>Base Price (₹)</label>
            <input type="number" class="form-control" v-model="service.base_price" min="1" required />
          </div>
          <div class="d-flex justify-content-end">
            <button type="submit" class="btn btn-success me-2">Add</button>
            <button type="button" class="btn btn-danger" @click="$emit('close')">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: "AdminAddServiceModal",
    data() {
      return {
        service: {
          name: "",
          description: "",
          base_price: 1
        }
      };
    },
    methods: {
      async addService() {
        const res = await fetch("http://localhost:5000/add_service", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(this.service),
          credentials: "include"
        });
  
        const data = await res.json();
        if (data.status === "success") {
          this.$emit("added");
        } else {
          alert("Failed to add service.");
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
    z-index: 1050;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.3);
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .modal-dialog {
    background: white;
    border-radius: 8px;
    width: 100%;
    max-width: 500px;
  }
  </style>
  