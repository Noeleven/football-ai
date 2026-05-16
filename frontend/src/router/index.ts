import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/Home/HomeView.vue'),
  },
  {
    path: '/news',
    name: 'news',
    component: () => import('@/views/News/NewsView.vue'),
  },
  {
    path: '/teams',
    name: 'teams',
    component: () => import('@/views/Teams/TeamsView.vue'),
  },
  {
    path: '/teams/:id',
    name: 'team-detail',
    component: () => import('@/views/Teams/TeamDetailView.vue'),
  },
  {
    path: '/players/:id',
    name: 'player-detail',
    component: () => import('@/views/Players/PlayerDetailView.vue'),
  },
  {
    path: '/matches',
    name: 'matches',
    component: () => import('@/views/Matches/MatchesView.vue'),
  },
  {
    path: '/matches/:id',
    name: 'match-detail',
    component: () => import('@/views/Matches/MatchDetailView.vue'),
  },
  {
    path: '/admin',
    name: 'admin',
    component: () => import('@/views/Admin/AdminView.vue'),
    children: [
      { path: 'dashboard', name: 'admin-dashboard', component: () => import('@/views/Admin/DashboardView.vue') },
      { path: 'teams', name: 'admin-teams', component: () => import('@/views/Admin/DataManagement/TeamsView.vue') },
      { path: 'players', name: 'admin-players', component: () => import('@/views/Admin/DataManagement/PlayersView.vue') },
      { path: 'matches', name: 'admin-matches', component: () => import('@/views/Admin/DataManagement/MatchesView.vue') },
      { path: 'news', name: 'admin-news', component: () => import('@/views/Admin/DataManagement/NewsView.vue') },
      { path: 'settings', name: 'admin-settings', component: () => import('@/views/Admin/SystemSettings/SettingsView.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router