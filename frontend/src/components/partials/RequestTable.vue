<template>
  <table class="table table-striped table-bordered">
    <thead>
      <tr>
        <th>ID</th>
        <th>Service Name</th>
        <th v-if="!viewOnly">Client</th>
        <th>Location</th>
        <th>Description</th>
        <th>Due Date</th>
        <th v-if="!viewOnly">Estimated Hours</th>
        <th v-if="!viewOnly">Total Payment</th>
        <th v-if="!viewOnly">Action</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="req in requests" :key="req.id">
        <td>{{ req.id }}</td>
        <td>{{ req.category?.name || serviceName }}</td>
        <td v-if="!viewOnly">{{ req.client?.first_name }} {{ req.client?.last_name }} ({{ req.client?.email }})</td>
        <td>{{ req.location }}</td>
        <td>{{ req.description }}</td>
        <td>{{ req.due_date }}</td>
        <td v-if="!viewOnly">{{ req.estimated_hours }}</td>
        <td v-if="!viewOnly">{{ req.total_cost }}</td>
        <td v-if="!viewOnly">
          <button
            v-if="appliedIds?.includes(req.id)"
            class="btn btn-secondary btn-sm"
            disabled
          >
            Applied
          </button>
          <button
            v-else
            class="btn btn-primary btn-sm"
            @click="$emit('apply', { id: req.id, name: req.category?.name || serviceName })"
          >
            Apply
          </button>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script>
export default {
  name: "RequestTable",
  props: {
    requests: Array,
    appliedIds: Array,
    viewOnly: Boolean,
    serviceName: String
  }
};
</script>