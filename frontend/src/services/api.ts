import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
})

// API helpers
export const getTeams = (competitionId = '') => api.get('/api/teams', { params: { competition_id: competitionId } })
export const getTeam = (id: string) => api.get(`/api/teams/${id}`)
export const searchTeams = (keyword: string) => api.get(`/api/teams/search/${keyword}`)

export const getPlayers = (teamId: string) => api.get(`/api/players/${teamId}`)
export const getKeyPlayers = (teamId: string) => api.get(`/api/players/key/${teamId}`)
export const searchPlayers = (keyword: string) => api.get(`/api/players/search/${keyword}`)

export const getUpcomingMatches = (competitionId = '', limit = 20) => api.get('/api/matches/upcoming', { params: { competition_id: competitionId, limit } })
export const getRecentMatches = (competitionId = '', limit = 20) => api.get('/api/matches/recent', { params: { competition_id: competitionId, limit } })
export const getMatch = (id: string) => api.get(`/api/matches/${id}`)
export const getH2H = (team1: string, team2: string) => api.get(`/api/matches/h2h/${team1}/${team2}`)

export const getNews = (type = '', competitionId = '', limit = 50) => api.get('/api/news', { params: { news_type: type, competition_id: competitionId, limit } })
export const getRecentNews = (limit = 20) => api.get('/api/news', { params: { limit } })
export const getNewsById = (id: string) => api.get(`/api/news/${id}`)

export const predictMatch = (matchId: string) => api.post(`/api/predict/${matchId}`)
export const analyzeMatch = (matchId: string) => api.post(`/api/analysis/${matchId}`)
export const getRecentPredictions = (limit = 20) => api.get('/api/predictions/recent', { params: { limit } })
export const getRecentAnalyses = (limit = 20) => api.get('/api/analysis/recent', { params: { limit } })

export const getCompetitions = () => api.get('/api/competitions')

export default api