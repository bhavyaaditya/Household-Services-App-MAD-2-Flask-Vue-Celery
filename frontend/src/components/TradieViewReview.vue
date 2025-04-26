<template>
    <TradieNavbar/>
    <div class="container mt-4" v-if="request && user">
      <h3>Review for Request #{{ request.id }}</h3>
  
      <hr />
      <h5>Service Details</h5>
      <p><strong>Service:</strong> {{ request.description }}</p>
      <p><strong>Location:</strong> {{ request.location }}</p>
      <p><strong>Due Date:</strong> {{ request.due_date }}</p>
  
      <hr />
      <h5>User Details</h5>
      <p><strong>Name:</strong> {{ user.first_name }} {{ user.last_name }}</p>
      <p><strong>Email:</strong> {{ user.email }}</p>
  
      <hr />
      <h5>Client Review</h5>
      <p><strong>Rating:</strong> {{ request.rating }}/5</p>
      <p><strong>Review:</strong> {{ request.review }}</p>
      <p><strong>Reviewed on:</strong> {{ request.review_date }}</p>
    </div>
  </template>
  
  <script>
  import TradieNavbar from './TradieNavbar.vue'
  export default {
    data() {
      return {
        request: null,
        user: null
      };
    },
    components:{
      TradieNavbar
    },
    async mounted() {
      const requestId = this.$route.params.request_id;
      const res = await fetch(`http://localhost:5000/review/tradie_view/${requestId}`, {
        credentials: 'include'
      });
      const data = await res.json();
      this.request = data.request;
      this.user = data.user;
    }
  };
  </script>
  