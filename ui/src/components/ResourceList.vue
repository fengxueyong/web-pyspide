<template>
  <section class="resource-section">
    <div class="filter-bar">
      <div class="filter-left">
        <select v-model="filters.website" class="input filter-select website-select">
          <option value="">--- 选择网址 ---</option>
          <option v-for="w in websites" :key="w" :value="w">{{ w }}</option>
        </select>
        <select v-model="filters.res_type" class="select filter-select">
          <option value="all">全部类型</option>
          <option value="text/article">文本/文章</option>
          <option value="image">图片</option>
          <option value="doc">文档</option>
          <option value="audio">音频</option>
          <option value="video">视频</option>
        </select>
        <input v-model="filters.min_time" type="datetime-local" class="input filter-date" placeholder="开始时间" />
        <input v-model="filters.max_time" type="datetime-local" class="input filter-date" placeholder="结束时间" />
        <button class="btn btn-query" @click="onFilterChange">查询</button>
      </div>
      <div class="filter-right">
        <button class="btn-icon" :class="{ active: !gridMode }" @click="gridMode = false" title="列表视图">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="8" y1="6" x2="21" y2="6" /><line x1="8" y1="12" x2="21" y2="12" /><line x1="8" y1="18" x2="21" y2="18" /><line x1="3" y1="6" x2="3.01" y2="6" /><line x1="3" y1="12" x2="3.01" y2="12" /><line x1="3" y1="18" x2="3.01" y2="18" />
          </svg>
        </button>
        <button class="btn-icon" :class="{ active: gridMode }" @click="gridMode = true" title="缩略图视图">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" /><rect x="3" y="14" width="7" height="7" /><rect x="14" y="14" width="7" height="7" />
          </svg>
        </button>
      </div>
    </div>

    <div class="resource-grid" :class="{ 'list-layout': !gridMode }" ref="scrollContainer">
      <ResourceCard
        v-for="item in items"
        :key="item.id"
        :resource="item"
        :list-mode="!gridMode"
        @preview="onPreview"
      />
    </div>

    <div v-if="loading" class="load-status">加载中...</div>
    <div v-else-if="!hasMore && items.length > 0" class="load-status end">已加载全部</div>
    <div v-else-if="!loading && items.length === 0" class="load-status empty">暂无数据</div>

    <PreviewModal :visible="previewVisible" :resource="previewResource" @close="previewVisible = false" />
  </section>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { fetchResources, fetchWebsites } from '../api'
import ResourceCard from './ResourceCard.vue'
import PreviewModal from './PreviewModal.vue'

const scrollContainer = ref(null)
const items = ref([])
const loading = ref(false)
const hasMore = ref(true)
const page = ref(1)
const page_size = 20
const gridMode = ref(true)

const previewVisible = ref(false)
const previewResource = ref(null)

const websites = ref([])

const filters = ref({
  website: '',
  res_type: 'all',
  min_time: '',
  max_time: '',
})

function onFilterChange() {
  items.value = []
  page.value = 1
  hasMore.value = true
  loadMore()
}

async function loadMore() {
  if (loading.value || !hasMore.value) return
  if (!filters.value.website) {
    loading.value = false
    return
  }
  loading.value = true
  try {
    const data = await fetchResources({
      page: page.value,
      page_size,
      website: filters.value.website,
      res_type: filters.value.res_type || 'all',
      min_time: filters.value.min_time ? new Date(filters.value.min_time).toISOString() : undefined,
      max_time: filters.value.max_time ? new Date(filters.value.max_time).toISOString() : undefined,
    })
    const newItems = data.items || []
    items.value.push(...newItems)
    hasMore.value = items.value.length < (data.totalCount || 0)
    page.value++
  } catch (e) {
    console.error('查询资源失败:', e)
  } finally {
    loading.value = false
  }
}

function setWebsite(website) {
  filters.value.website = website
  onFilterChange()
}

defineExpose({ setWebsite, refreshWebsites })

function onPreview(resource) {
  previewResource.value = resource
  previewVisible.value = true
}

let observer = null

function setupObserver() {
  observer = new IntersectionObserver(
    (entries) => {
      if (entries[0].isIntersecting) {
        loadMore()
      }
    },
    { rootMargin: '200px' }
  )

  nextTick(() => {
    const sentinel = document.createElement('div')
    sentinel.className = 'scroll-sentinel'
    scrollContainer.value?.after(sentinel)
    observer.observe(sentinel)
  })
}

async function loadWebsites() {
  try {
    websites.value = await fetchWebsites()
  } catch {
    // silent
  }
}

function refreshWebsites() {
  loadWebsites()
}

onMounted(() => {
  loadWebsites()
  loadMore()
  setupObserver()
})

onUnmounted(() => {
  if (observer) observer.disconnect()
})
</script>

<style scoped>
.resource-section {
  padding-top: 160px;
  max-width: 1200px;
  margin: 0 auto;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f9fafb;
  border-radius: 8px;
  margin-bottom: 16px;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-left {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}

.filter-input {
  width: 200px;
}

.website-select {
  width: 260px;
}

.filter-select {
  width: 130px;
}

.filter-date {
  width: 190px;
}

.filter-right {
  display: flex;
  gap: 4px;
}

.btn-query {
  height: 34px;
  padding: 0 16px;
  background: #3b82f6;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
}

.btn-query:hover {
  background: #2563eb;
}

.btn-icon {
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
  color: #6b7280;
  transition: all 0.2s;
}

.btn-icon.active {
  background: #3b82f6;
  color: #fff;
  border-color: #3b82f6;
}

.resource-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
  padding: 0 16px;
}

.resource-grid.list-layout {
  grid-template-columns: 1fr;
}

.load-status {
  text-align: center;
  padding: 32px 16px;
  color: #9ca3af;
  font-size: 14px;
}

.load-status.end {
  color: #6b7280;
}

.scroll-sentinel {
  height: 1px;
}

.input, .select {
  height: 34px;
  padding: 0 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s;
}

.input:focus, .select:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15);
}
</style>
