<template>
    <div class="container mt-5">
      <h3>Applicants for {{ serviceType }} Service Request #{{ serviceRequestId }}</h3>
      <h5>Created On: {{ createdDate }}</h5>
      <h5>Due Date: {{ dueDate }}</h5>
  
      <table class="table table-striped table-bordered" v-if="applicants.length">
        <thead>
          <tr>
            <th>Tradie ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Hourly Rate</th>
            <th>Years of Experience</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="tradie in applicants" :key="tradie.id">
            <td>{{ tradie.id }}</td>
            <td>{{ tradie.first_name }} {{ tradie.last_name }}</td>
            <td>{{ tradie.email }}</td>
            <td>{{ tradie.hourly_rate }}</td>
            <td>{{ tradie.years_of_experience }}</td>
            <td>
              <button class="btn btn-success btn-sm" @click="selectTradie(tradie.id)">Select Tradie</button>
            </td>
          </tr>
        </tbody>
      </table>
  
      <h5 v-else class="text-danger">No tradies have applied for this job yet.</h5>
    </div>
  </template>
  
  <script>
  export default {
    name: 'ViewApplicants',
    data() {
      return {
        serviceRequestId: this.$route.params.requestId,
        serviceType: '',
        createdDate: '',
        dueDate: '',
        applicants: []
      };
    },
    methods: {
      async fetchData() {
        try {
          const res = await fetch(`http://localhost:5000/view_applications/${this.serviceRequestId}`, {
            credentials: 'include'
          });
          const html = await res.text();
          const jsonStart = html.indexOf('{');
          const data = JSON.parse(html.slice(jsonStart));
  
          this.serviceType = data.service_type;
          this.createdDate = data.created_date;
          this.dueDate = data.due_date;
          this.applicants = data.applicants;
        } catch (err) {
          console.error('Error loading applicants:', err);
        }
      },
      async selectTradie(tradieId) {
        const formData = new FormData();
        formData.append('tradie_id', tradieId);

        try {
          const res = await fetch(`http://localhost:5000/service_requests/${this.serviceRequestId}/select_tradie`, {
            method: 'POST',
            credentials: 'include',
            body: formData
          });

          const result = await res.json();

          // Redirect to dashboard using the redirect_url passed by flask
          if (result.redirect_url) {
            this.$router.push(result.redirect_url);
            return;
          }

          if (result.status !== 'success') {
            alert(result.message || 'Failed to select tradie.');
          }
        } catch (err) {
          console.error('Error selecting tradie:', err);
          alert('An unexpected error occurred.');
        }
      },
    },
    mounted() {
      this.fetchData();
    }
  };
  </script>
  