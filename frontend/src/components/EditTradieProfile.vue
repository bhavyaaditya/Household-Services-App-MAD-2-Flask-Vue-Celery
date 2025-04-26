<template>
  <div class="container mt-5">
    <h2>Edit Profile</h2>
    <form @submit.prevent="submitForm">
      <!-- Personal Info -->
      <div class="mb-3">
        <label class="form-label">First Name</label>
        <input v-model="form.first_name" type="text" class="form-control" required />
      </div>

      <div class="mb-3">
        <label class="form-label">Last Name</label>
        <input v-model="form.last_name" type="text" class="form-control" required />
      </div>

      <div class="mb-3">
        <label class="form-label">Email</label>
        <input v-model="form.email" type="email" class="form-control" required />
      </div>

      <div class="mb-3">
        <label class="form-label">Phone Number</label>
        <input v-model="form.phone_number" type="text" class="form-control" />
      </div>

      <div class="mb-3">
        <label class="form-label">Location</label>
        <input v-model="form.location" type="text" class="form-control" />
      </div>

      <!-- Professional Details -->
      <div class="mb-3">
        <label class="form-label">Hourly Rate ($)</label>
        <input v-model.number="form.hourly_rate" type="number" class="form-control" step="0.01" />
      </div>

      <div class="mb-3">
        <label class="form-label">Years of Experience</label>
        <input v-model.number="form.years_of_experience" type="number" class="form-control" />
      </div>

      <div class="mb-3">
        <label class="form-label">Availability</label>
        <select v-model="form.is_available" class="form-select">
          <option :value="true">Available</option>
          <option :value="false">Unavailable</option>
        </select>
      </div>

      <button type="submit" class="btn btn-primary">Save Changes</button>
    </form>
  </div>
</template>

<script>
export default {
  name: 'EditTradieProfile',
  data() {
    return {
      form: {
        first_name: '',
        last_name: '',
        email: '',
        phone_number: '',
        location: '',
        hourly_rate: 0,
        years_of_experience: 0,
        is_available: true
      }
    };
  },
  async mounted() {
    try {
      const res = await fetch('/edit_profile', {
        credentials: 'include'
      });
      const html = await res.text();
      const jsonStart = html.indexOf('{');
      const data = JSON.parse(html.slice(jsonStart));
      this.form = data.user;
    } catch (err) {
      console.error('Failed to load profile:', err);
    }
  },
  methods: {
    async submitForm() {
      const formData = new FormData();
      for (const key in this.form) {
        formData.append(key, this.form[key]);
      }

      try {
        const res = await fetch('/edit_profile', {
          method: 'POST',
          credentials: 'include',
          body: formData
        });

        if (res.redirected) {
          window.location.href = res.url;
        } else {
          alert('Profile updated successfully.');
        }
      } catch (err) {
        alert('Failed to update profile.');
      }
    }
  }
}
</script>