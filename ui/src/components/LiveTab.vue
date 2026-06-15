<template>
  <div class="live-tab">
    <!-- Filter / view controls -->
    <div class="toolbar">
      <div class="toolbar-row">
        <button class="filter-toggle" :class="{ open: filterOpen }" @click="filterOpen = !filterOpen">
          <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>
          筛选
        </button>
        <div class="view-toggle">
          <button class="view-btn" :class="{ active: viewMode === 'detail' }" @click="viewMode = 'detail'" title="列表视图">
            <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
          </button>
          <button class="view-btn" :class="{ active: viewMode === 'thumbnail' }" @click="viewMode = 'thumbnail'" title="缩略图视图">
            <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
          </button>
        </div>
      </div>

      <!-- Filter panel -->
      <div v-if="filterOpen" class="filter-panel">
        <div class="filter-group">
          <span class="filter-label">类型</span>
          <div class="filter-chips">
            <button
              v-for="opt in typeOptions"
              :key="opt.value"
              class="chip"
              :class="{ active: filterType === opt.value }"
              @click="filterType = opt.value"
            >{{ opt.label }}</button>
          </div>
        </div>
      </div>

      <div class="toolbar-info">
        <span class="result-count">显示 {{ displayed.length }} / {{ filtered.length }} 条</span>
        <button v-if="isFiltered" class="clear-btn" @click="clearFilters">
          <svg viewBox="0 0 24 24" width="10" height="10" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          清除筛选
        </button>
      </div>
    </div>

    <!-- Content -->
    <div class="content-area" ref="scrollRef">
      <!-- Empty state: no resources -->
      <div v-if="resources.length === 0" class="empty-state">
        <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="1.5" class="empty-icon"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>
        <span class="empty-title">等待抓取任务...</span>
        <span class="empty-sub">配置左侧参数后点击「开始抓取」</span>
      </div>

      <!-- Empty state: filtered out -->
      <div v-else-if="filtered.length === 0" class="empty-state">
        <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="1.5" class="empty-icon"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <span class="empty-title">无匹配结果</span>
      </div>

      <!-- Detail view -->
      <div v-else-if="viewMode === 'detail'" class="detail-list">
        <div v-for="r in displayed" :key="r.id || r.res_link" class="detail-card" @click="openLink(r.res_link || r.url)">
          <div class="card-indicator" :class="statusClass(r)"></div>
          <div class="card-body">
            <div class="card-row">
              <span class="type-tag" :class="'type-' + (r.res_type || r.type)">
                {{ typeLabel(r.res_type || r.type) }}
              </span>
              <span class="status-tag" :class="statusClass(r)">{{ r.status || r.res_status || 200 }}</span>
              <span class="card-depth">深度 {{ r.depth || 1 }}</span>
              <span class="card-size">{{ formatSize(r.res_size) }}</span>
            </div>
            <div class="card-url">
              <span class="url-text">{{ r.res_link || r.url }}</span>
              <svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2" class="external-icon"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
            </div>
            <div class="card-meta">
              <span>{{ r.contentType || r.res_type || '-' }}</span>
              <span>{{ formatTime(r.create_time || r.timestamp) }}</span>
            </div>
          </div>
        </div>

        <!-- Scroll sentinel -->
        <div ref="sentinelRef" class="sentinel">
          <span v-if="hasMore" class="load-more">加载更多...</span>
        </div>
      </div>

      <!-- Thumbnail view -->
      <div v-else class="thumb-grid">
        <div v-for="r in displayed" :key="r.id || r.res_link" class="thumb-card" @click="openLink(r.res_link || r.url)">
          <div class="thumb-preview">
            <img
              v-if="r.res_type === 'image'"
              :src="r.res_link"
              :alt="r.res_link"
              class="thumb-img"
              @error="onImgError"
            />
            <div v-else class="thumb-placeholder">
              <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"/><line x1="7" y1="2" x2="7" y2="22"/><line x1="17" y1="2" x2="17" y2="22"/><line x1="2" y1="12" x2="22" y2="12"/><line x1="2" y1="7" x2="7" y2="7"/><line x1="2" y1="17" x2="7" y2="17"/><line x1="17" y1="7" x2="22" y2="7"/><line x1="17" y1="17" x2="22" y2="17"/></svg>
              <span>{{ typeLabel(r.res_type || r.type) }}</span>
            </div>
            <span class="thumb-status" :class="statusClass(r)">{{ r.status || r.res_status || 200 }}</span>
          </div>
          <div class="thumb-info">
            <div class="thumb-type-row">
              <span class="type-tag-sm" :class="'type-' + (r.res_type || r.type)">{{ typeLabel(r.res_type || r.type) }}</span>
              <span class="thumb-size">{{ formatSize(r.res_size) }}</span>
            </div>
            <span class="thumb-name">{{ (r.res_link || r.url || '').split('/').pop() }}</span>
            <span class="thumb-url">{{ r.res_link || r.url }}</span>
          </div>
        </div>

        <!-- Scroll sentinel -->
        <div ref="sentinelRef" class="sentinel">
          <span v-if="hasMore" class="load-more">加载更多...</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'

const props = defineProps({
  resources: { type: Array, default: () => [] },
})

const PAGE_SIZE = 24

const viewMode = ref('detail')
const filterOpen = ref(false)
const filterType = ref('all')
const searchQuery = ref('')
const displayCount = ref(PAGE_SIZE)

const scrollRef = ref(null)
const sentinelRef = ref(null)
let observer = null

const typeOptions = [
  { value: 'all', label: '全部' },
  { value: 'image', label: '图片' },
  { value: 'video', label: '视频' },
  { value: 'doc', label: '文档' },
]

const filtered = computed(() => {
  return props.resources.filter(r => {
    const type = r.res_type || r.type
    const matchType = filterType.value === 'all' || type === filterType.value
    return matchType
  })
})

const displayed = computed(() => filtered.value.slice(0, displayCount.value))
const hasMore = computed(() => displayCount.value < filtered.value.length)
const isFiltered = computed(() => filterType.value !== 'all')

watch([filterType, searchQuery], () => {
  displayCount.value = PAGE_SIZE
})

function clearFilters() {
  filterType.value = 'all'
  searchQuery.value = ''
}

function typeLabel(type) {
  const map = { image: '图片', video: '视频', doc: '文档', 'text/article': '文章' }
  return map[type] || type || '未知'
}

function statusClass(r) {
  const status = r.status || r.res_status || 200
  if (status >= 400) return 'status-error'
  if (status >= 300) return 'status-warn'
  return 'status-ok'
}

function formatSize(bytes) {
  if (!bytes || bytes === 0) return ''
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  let size = bytes
  while (size >= 1024 && i < units.length - 1) {
    size /= 1024
    i++
  }
  return size.toFixed(i > 0 ? 1 : 0) + ' ' + units[i]
}

function formatTime(t) {
  if (!t) return ''
  const d = new Date(t)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function onImgError(e) {
  e.target.style.display = 'none'
}

function openLink(url) {
  if (url) window.open(url, '_blank')
}

function setupObserver() {
  observer = new IntersectionObserver(
    (entries) => {
      if (entries[0]?.isIntersecting && hasMore.value) {
        displayCount.value += PAGE_SIZE
      }
    },
    { threshold: 0.1 }
  )

  nextTick(() => {
    if (sentinelRef.value) {
      observer.observe(sentinelRef.value)
    }
  })
}

watch(() => props.resources.length, () => {
  nextTick(() => {
    if (observer && sentinelRef.value) {
      observer.unobserve(sentinelRef.value)
      observer.observe(sentinelRef.value)
    }
  })
})

onMounted(() => {
  nextTick(setupObserver)
})

onUnmounted(() => {
  if (observer) observer.disconnect()
})
</script>

<style scoped>
.live-tab {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 12px;
}

/* Toolbar */
.toolbar {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex-shrink: 0;
}

.toolbar-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.filter-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--input-background);
  color: var(--muted-foreground);
  font-size: 12px;
  font-family: inherit;
  transition: all 0.15s;
}

.filter-toggle:hover {
  border-color: var(--primary);
  color: var(--foreground);
}

.filter-toggle.open {
  background: var(--primary);
  color: var(--primary-foreground);
  border-color: var(--primary);
}

/* View toggle */
.view-toggle {
  display: flex;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
}

.view-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6px 10px;
  border: none;
  background: var(--input-background);
  color: var(--muted-foreground);
  transition: all 0.15s;
}

.view-btn:hover {
  color: var(--foreground);
}

.view-btn.active {
  background: var(--primary);
  color: var(--primary-foreground);
}

/* Filter panel */
.filter-panel {
  padding: 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--card);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-label {
  font-size: 11px;
  color: var(--muted-foreground);
  letter-spacing: 0.05em;
}

.filter-chips {
  display: flex;
  gap: 4px;
}

.chip {
  padding: 4px 10px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--secondary);
  color: var(--muted-foreground);
  font-size: 12px;
  font-family: inherit;
  transition: all 0.15s;
}

.chip:hover {
  color: var(--foreground);
}

.chip.active {
  background: var(--primary);
  color: var(--primary-foreground);
  border-color: var(--primary);
}

/* Info */
.toolbar-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.result-count {
  font-size: 12px;
  color: var(--muted-foreground);
}

.clear-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border: none;
  background: transparent;
  color: var(--muted-foreground);
  font-size: 12px;
  font-family: inherit;
  transition: color 0.15s;
}

.clear-btn:hover {
  color: var(--primary);
}

/* Content */
.content-area {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

/* Empty state */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 64px 16px;
  color: var(--muted-foreground);
}

.empty-icon {
  opacity: 0.3;
  margin-bottom: 4px;
}

.empty-title {
  font-size: 14px;
}

.empty-sub {
  font-size: 12px;
  opacity: 0.6;
}

/* Detail list */
.detail-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-card {
  display: flex;
  gap: 12px;
  padding: 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--card);
  cursor: pointer;
  transition: border-color 0.15s;
}

.detail-card:hover {
  border-color: var(--primary);
}

.card-indicator {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  margin-top: 4px;
  flex-shrink: 0;
}

.card-indicator.status-ok { background: var(--primary); }
.card-indicator.status-warn { background: #b8860b; }
.card-indicator.status-error { background: var(--destructive); }

.card-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.card-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.type-tag {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: var(--radius);
  font-size: 11px;
  border: 1px solid;
}

.type-tag.type-image {
  color: #7c3aed;
  background: #f5f3ff;
  border-color: #ddd6fe;
}

.type-tag.type-video {
  color: #db2777;
  background: #fdf2f8;
  border-color: #fbcfe8;
}

.type-tag.type-doc {
  color: #ea580c;
  background: #fff7ed;
  border-color: #fed7aa;
}

.type-tag.type-text\/article {
  color: #2563eb;
  background: #eff6ff;
  border-color: #bfdbfe;
}

.status-tag {
  padding: 2px 6px;
  border-radius: var(--radius);
  font-size: 11px;
}

.status-tag.status-ok {
  color: var(--primary);
  background: rgba(22, 100, 48, 0.1);
}

.status-tag.status-warn {
  color: #b8860b;
  background: rgba(184, 134, 11, 0.1);
}

.status-tag.status-error {
  color: var(--destructive);
  background: rgba(192, 37, 26, 0.1);
}

.card-depth {
  font-size: 11px;
  color: var(--muted-foreground);
}

.card-size {
  font-size: 11px;
  color: var(--muted-foreground);
  margin-left: auto;
}

.card-url {
  display: flex;
  align-items: center;
  gap: 6px;
}

.url-text {
  font-size: 12px;
  color: var(--foreground);
  opacity: 0.85;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  min-width: 0;
}

.external-icon {
  color: var(--muted-foreground);
  opacity: 0;
  flex-shrink: 0;
  transition: opacity 0.15s;
}

.detail-card:hover .external-icon {
  opacity: 0.6;
}

.detail-card:hover .external-icon:hover {
  opacity: 1;
  color: var(--primary);
}

.card-meta {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: var(--muted-foreground);
}

/* Thumbnail grid */
.thumb-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.thumb-card {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  background: var(--card);
  cursor: pointer;
  transition: border-color 0.15s;
}

.thumb-card:hover {
  border-color: var(--primary);
}

.thumb-preview {
  position: relative;
  aspect-ratio: 16 / 10;
  background: var(--secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.thumb-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.thumb-card:hover .thumb-img {
  transform: scale(1.05);
}

.thumb-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: var(--muted-foreground);
  opacity: 0.4;
  font-size: 12px;
}

.thumb-status {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 2px 6px;
  border-radius: var(--radius);
  font-size: 11px;
}

.thumb-status.status-ok {
  background: rgba(22, 100, 48, 0.8);
  color: white;
}

.thumb-status.status-warn {
  background: rgba(184, 134, 11, 0.8);
  color: white;
}

.thumb-status.status-error {
  background: rgba(192, 37, 26, 0.8);
  color: white;
}

.thumb-info {
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.thumb-type-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.type-tag-sm {
  padding: 1px 6px;
  border-radius: var(--radius);
  font-size: 10px;
  border: 1px solid;
}

.type-tag-sm.type-image {
  color: #7c3aed;
  background: #f5f3ff;
  border-color: #ddd6fe;
}

.type-tag-sm.type-video {
  color: #db2777;
  background: #fdf2f8;
  border-color: #fbcfe8;
}

.type-tag-sm.type-doc {
  color: #ea580c;
  background: #fff7ed;
  border-color: #fed7aa;
}

.type-tag-sm.type-text\/article {
  color: #2563eb;
  background: #eff6ff;
  border-color: #bfdbfe;
}

.thumb-size {
  font-size: 11px;
  color: var(--muted-foreground);
}

.thumb-name {
  font-size: 12px;
  color: var(--foreground);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.thumb-url {
  font-size: 11px;
  color: var(--muted-foreground);
  opacity: 0.6;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Sentinel */
.sentinel {
  padding: 16px 0;
  text-align: center;
}

.load-more {
  font-size: 12px;
  color: var(--muted-foreground);
  animation: pulse-text 1.5s infinite;
}

@keyframes pulse-text {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 1; }
}
</style>
