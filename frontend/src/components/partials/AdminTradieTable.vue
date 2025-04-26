<template>
  <div class="container mt-5">
    <h2>Tradies</h2>
    <table class="table table-striped table-bordered">
      <thead>
        <tr>
          <th>ID</th>
          <th>First Name</th>
          <th>Last Name</th>
          <th>Email</th>
          <th>Hourly Rate (₹)</th>
          <th>Experience (Years)</th>
          <th>Analytics</th>
          <th>activated</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="tradie in tradies" :key="tradie.id">
          <td>{{ tradie.id }}</td>
          <td>{{ tradie.first_name }}</td>
          <td>{{ tradie.last_name }}</td>
          <td>{{ tradie.email }}</td>
          <td>{{ tradie.hourly_rate }}</td>
          <td>{{ tradie.years_of_experience }}</td>
          <td>
            <router-link :to="`/admin/tradie/${tradie.id}/analytics`" class="btn btn-primary btn-sm">
              View Analytics
            </router-link>
          </td>
          <td>
            <input
              type="checkbox"
              :checked="tradie.activated"
              @change="(e) => updateactivated(tradie, e.target.checked)"
            />
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  name: "AdminTradieTable",
  props: ["tradies"],
  methods: {
    async updateactivated(tradie, newStatus) {
      const res = await fetch("http://localhost:5000/update_tradie_activated", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tradie_id: tradie.id, activated: newStatus }),
        credentials: "include"
      });
      const data = await res.json();
      if (data.status === "success") {
        tradie.activated = newStatus;
      } else {
        alert("Failed to update activated status");
      }
    },
  },
};
</script>
