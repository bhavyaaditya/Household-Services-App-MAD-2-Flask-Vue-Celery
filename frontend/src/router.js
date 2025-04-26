import { createRouter, createWebHistory } from 'vue-router';

// Auth imports
import UserRegistrationForm from './components/UserRegistrationForm.vue';
import TradieRegistrationForm from './components/TradieRegistrationForm.vue';
import LoginForm from './components/LoginForm.vue';

//User imports
import UserDashboard from './components/UserDashboard.vue';
import ViewApplicants from './components/ViewApplicants.vue';
import EditUserProfile from './components/EditUserProfile.vue';
import SearchResults from './components/SearchResults.vue';
import TradiesByLocation from './components/TradiesByLocation.vue';
import TradiesByService from './components/TradiesByService.vue';
import ViewTradie from './components/ViewTradie.vue';
import MakeReview from './components/MakeReview.vue';
import UserViewReview from './components/UserViewReview.vue';

//Tradie imports
import TradieDashboard from './components/TradieDashboard.vue';
import EditTradieProfile from './components/EditTradieProfile.vue';
import TradieAnalytics from './components/TradieAnalytics.vue';
import TradieViewReview from './components/TradieViewReview.vue';

//Admin imports
import AdminDashboard from './components/AdminDashboard.vue';
import AdminAnalytics from './components/AdminAnalytics.vue';
import AdminTradieAnalytics from './components/AdminTradieAnalytics.vue'


const routes = [
    // Auth routes
    {
      path: '/login',
      name: 'Login',
      component: LoginForm
    },
    {
      path: '/',
      redirect: '/login'
    },

  {
    path: '/register/user',
    name: 'RegisterUser',
    component: UserRegistrationForm
  },
  {
    path: '/register/tradie',
    name: 'RegisterTradie',
    component: TradieRegistrationForm,
  },

  // User routes
  {
    path: '/user/dashboard',
    name: 'UserDashboard',
    component: UserDashboard
  },
  {
    path: '/view_applications/:requestId',
    name: 'ViewApplicants',
    component: ViewApplicants
  },
  {
    path: '/edit_profile',
    name: 'EditUserProfile',
    component: EditUserProfile
  },
  {
    path: '/search',
    name: 'SearchResults',
    component: SearchResults
  },
  {
    path: '/tradies/location/:location',
    name: 'TradiesByLocation',
    component: TradiesByLocation
  },
  {
    path: '/tradies/service/:service_id',
    name: 'TradiesByService',
    component: TradiesByService
  },
  {
    path: '/tradie/:tradie_id',
    name: 'ViewTradie',
    component: ViewTradie
  },
  {
    path: '/review/make/:request_id',
    name: 'MakeReview',
    component: MakeReview
  },
  {
    path: '/review/user_view/:request_id',
    name: 'UserViewReview',
    component: UserViewReview
  },

  // Tradie routes
  { 
    path: '/tradie/dashboard', 
    name: 'TradieDashboard', 
    component: TradieDashboard 
    },
  { 
    path: '/tradie/edit_profile', 
    name: 'EditTradieProfile', 
    component: EditTradieProfile 
    },
  { 
    path: '/tradie/analytics', 
    name: 'TradieAnalytics', 
    component: TradieAnalytics 
    },
  {
      path: '/review/tradie_view/:request_id',
      name: 'TradieViewReview',
      component: TradieViewReview
    },

    // Admin routes
    {
        path: '/admin/dashboard',
        name: 'AdminDashboard',
        component: AdminDashboard
    },
    {
        path: '/admin/analytics',
        name: 'AdminAnalytics',
        component: AdminAnalytics
    },
    {
      path: '/admin/tradie/:tradie_id/analytics',
      name: 'AdminTradieAnalytics',
      component: AdminTradieAnalytics
    }
    

];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
