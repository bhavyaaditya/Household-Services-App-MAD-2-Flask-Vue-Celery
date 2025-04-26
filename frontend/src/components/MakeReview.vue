<template>
    <div class="container mt-4" v-if="request && tradie">
      <h3>Leave Review for Request #{{ request.id }}</h3>
    
      <h5>Service Details</h5>
      <p><strong>Service:</strong> {{ request.description }}</p>
      <p><strong>Location:</strong> {{ request.location }}</p>
      <p><strong>Due Date:</strong> {{ request.due_date }}</p>
    
      <h5>Tradie Details</h5>
      <p><strong>Name:</strong> {{ tradie.first_name }} {{ tradie.last_name }}</p>
      <p><strong>Email:</strong> {{ tradie.email }}</p>
    
      <form @submit.prevent="submitReview">
        <div class="mb-3">
          <label>Rating:</label>
          <input type="number" class="form-control" v-model.number="rating" min="1" max="5" step="1" required />
        </div>
        <div class="mb-3">
          <label>Review:</label>
          <textarea class="form-control" v-model="review" required></textarea>
        </div>
        <button class="btn btn-primary">Submit Review</button>
      </form>
    </div>
    </template>
    
    <script>
    export default {
      data() {
        return {
          request: null,
          tradie: null,
          rating: 5,
          review: ''
        };
      },
      async mounted() {
        const requestId = this.$route.params.request_id;
        const res = await fetch(`http://localhost:5000/review/make/${requestId}`, {credentials: 'include'});
        const data = await res.json();
        this.request = data.request;
        this.tradie = data.tradie;
      },
      methods: {
        async submitReview() {
          const formData = new FormData();
          formData.append('rating', this.rating);
          formData.append('review', this.review);
    
          const requestId = this.$route.params.request_id;
          const res = await fetch(`http://localhost:5000/review/make/${requestId}`, {
            method: 'POST',
            credentials: 'include',
            body: formData
          });
          const result = await res.json();
          if(result.status==='success'){
            this.$router.push('/user/dashboard');
          }
        }
      }
    };
    </script>
    