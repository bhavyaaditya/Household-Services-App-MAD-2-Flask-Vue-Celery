<template>
  <table class="table table-striped table-bordered">
    <thead>
      <tr>
        <th>Request ID</th>
        <th>Service</th>
        <th>Client Name</th>
        <th>Location</th>
        <th>Due Date</th>
        <th>Estimated Hours</th>
        <th>Total Payment</th>
        <th>Review</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="req in requests" :key="req.id">
        <td>{{ req.id }}</td>
        <td>{{ req.service_category?.name }}</td>
        <td>{{ req.client?.first_name }} {{ req.client?.last_name }}</td>
        <td>{{ req.location }}</td>
        <td>{{ req.due_date }}</td>
        <td>{{ req.estimated_hours }}</td>
        <td>₹ {{ req.total_cost }} </td>
        <td>
          <button v-if="req.review" class="btn btn-primary btn-sm" @click="viewReview(req.id)">
            View Review
          </button>
          <span v-else>No review yet</span>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script>
export default {
  name: "CompletedTable",
  props: {
    requests: Array
  },
  methods: {
    viewReview(requestId) {
      this.$router.push({ name: "TradieViewReview", params: { request_id: requestId } });
    }
  }
};
</script>