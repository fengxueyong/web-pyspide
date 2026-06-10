import axios from 'axios'

const http = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

http.interceptors.response.use(
  (res) => {
    const body = res.data
    if (body.code !== 0) {
      return Promise.reject(new Error(body.message || '请求失败'))
    }
    return body.data
  },
  (err) => {
    return Promise.reject(err)
  }
)

export function startCrawl({ website, res_type, depth, link_follow, save_method }) {
  return http.post('/crawl', { website, res_type, depth, link_follow, save_method })
}

export function fetchResources({ page = 1, page_size = 20, website = '', res_type = 'all', min_time, max_time } = {}) {
  const params = { page, page_size, website, res_type }
  if (min_time) params.min_time = min_time
  if (max_time) params.max_time = max_time
  return http.get('/resources', { params })
}

export function getResourceDetail(resourceId) {
  return http.get(`/resources/${resourceId}`)
}

export function fetchWebsites() {
  return http.get('/tasks/websites')
}

export default http
