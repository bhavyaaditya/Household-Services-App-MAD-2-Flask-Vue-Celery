<template>
    <div class="container mt-4" v-if="request && tradie">
      <h3>Review for Request #{{ request.id }}</h3>
    
      <hr/>

      <h5>Service Details</h5>
      <p><strong>Service:</strong> {{ request.description }}</p>
      <p><strong>Location:</strong> {{ request.location }}</p>
      <p><strong>Due Date:</strong> {{ request.due_date }}</p>
    
      <hr/>

      <h5>Tradie Details</h5>
      <p><strong>Name:</strong> {{ tradie.first_name }} {{ tradie.last_name }}</p>
      <p><strong>Email:</strong> {{ tradie.email }}</p>
    
      <hr/>
    
      <h5>Your Review</h5>
      <p><strong>Rating:</strong> {{ request.rating }}/5</p>
      <p><strong>Review:</strong> {{ request.review }}</p>
      <p><strong>Reviewed on:</strong> {{ request.review_date }}</p>
    </div>
    </template>
    
    <script>
    export default {
      data() {
        return {
          request: null,
          tradie: null
        };
      },
      async mounted() {
        const requestId = this.$route.params.request_id;
        const res = await fetch(`http://localhost:5000/review/user_view/${requestId}`, {credentials: 'include'});
        const data = await res.json();
        this.request = data.request;
        this.tradie = data.tradie;
      }
    };
    </script>
    