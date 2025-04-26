<template>
    <div class="container mt-5">
      <h2>Users</h2>
      <table class="table table-striped table-bordered">
        <thead>
          <tr>
            <th>ID</th>
            <th>First Name</th>
            <th>Last Name</th>
            <th>Email</th>
            <th>Location</th>
            <th>activated</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.first_name }}</td>
            <td>{{ user.last_name }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.location }}</td>
            <td>
              <input type="checkbox" :checked="user.activated" @change="updateUseractivated(user)" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
  
  <script>
  export default {
    name: "AdminUserTable",
    props: ["users"],
    methods: {
      async updateUseractivated(user) {
        const res = await fetch("http://localhost:5000/update_user_activated", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: user.id, activated: !user.activated }),
          credentials: "include",
        });
        const data = await res.json();
        if (data.status === "success") {
          user.activated = !user.activated;
        } else {
          alert("Failed to update user activated status");
        }
      },
    },
  };
  </script>
  