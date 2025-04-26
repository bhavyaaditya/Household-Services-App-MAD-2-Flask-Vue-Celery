<template>
  <div>
    <router-view />
  </div>
</template>

<script>
import UserNavbar from './components/UserNavbar.vue';

export default {
  name: 'App',
  components: {
    UserNavbar
  }
};
</script>
