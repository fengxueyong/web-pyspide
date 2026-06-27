<template>
  <div class="query-tab">
    <!-- Query form -->
    <div class="query-form">
      <!-- Target URL -->
      <div class="form-field">
        <label class="field-label">目标 URL</label>
        <div class="custom-select">
          <select v-model="pendingTargetUrl" class="native-select">
            <option value="">全部</option>
            <option v-for="u in targetUrlOptions" :key="u" :value="u">{{ u }}</option>
          </select>
          <component :is="Icons.chevronDown" :size="13" class="chevron" />
        </div>
      </div>

      <!-- Time range -->
      <div class="form-field">
        <label class="field-label">抓取时间</label>
        <div class="time-range">
          <input v-model="pendingTimeStart" type="datetime-local" class="time-input" />
          <span class="time-sep">—</span>
          <input v-model="pendingTimeEnd" type="datetime-local" class="time-input" />
        </div>
      </div>

      <!-- Actions -->
      <div class="form-actions">
        <button class="btn-query" @click="doQuery">
          <component :is="Icons.search" :size="12" />
          查询
        </button>
        <button class="btn-reset" @click="doReset">重置</button>
      </div>
    </div>

    <!-- Results -->
    <template v-if="hasQueried">
      <FilterBar
        v-model="filterType"
        :is-filtered="isFiltered"
        :view-mode="viewMode"
        :result-count="displayed.length"
        :total-count="filtered.length"
        @update:view-mode="viewMode = $event"
        @clear="clearFilters"
      />

      <div class="content-area">
        <EmptyState
          v-if="filtered.length === 0"
          :icon="Icons.search"
          title="无匹配结果"
          sub="尝试调整查询或筛选条件"
        />

        <div v-else-if="viewMode === 'detail'" class="detail-list">
          <DetailCard v-for="r in displayed" :key="r.id || r.res_link || r.url" :resource="r" />
          <ScrollAnchor :has-more="hasMore" @load-more="loadMore" />
        </div>

        <ThumbnailGrid v-else :items="displayed" :has-more="hasMore" @load-more="loadMore" />
      </div>
    </template>

    <!-- Initial state -->
    <div v-else class="initial-state">
      <EmptyState
        :icon="Icons.database"
        :title="resources.length === 0 ? '暂无资源数据' : '设置条件后点击查询'"
        :sub="resources.length === 0 ? '先在左侧配置并运行抓取任务' : ''"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Icons } from './Icons'
import FilterBar from './FilterBar.vue'
import DetailCard from './DetailCard.vue'
import ThumbnailGrid from './ThumbnailGrid.vue'
import EmptyState from './EmptyState.vue'
import ScrollAnchor from './ScrollAnchor.vue'

const props = defineProps({
  resources: { type: Array, default: () => [] },
})

const PAGE_SIZE = 24

// Query form
const pendingTargetUrl = ref('')
const pendingTimeStart = ref('')
const pendingTimeEnd = ref('')
const hasQueried = ref(false)
const rawResults = ref([])

// Filter & view
const filterType = ref('all')
const viewMode = ref('detail')
const displayCount = ref(PAGE_SIZE)

const targetUrlOptions = computed(() => {
  const origins = new Set()
  props.resources.forEach(r => {
    const url = r.res_link || r.url
    if (url) {
      try { origins.add(new URL(url).origin) } catch {}
    }
  })
  return Array.from(origins)
})

const filtered = computed(() => {
  return rawResults.value.filter(r => {
    const type = r.res_type || r.type
    return filterType.value === 'all' || type === filterType.value
  })
})

const displayed = computed(() => filtered.value.slice(0, displayCount.value))
const hasMore = computed(() => displayCount.value < filtered.value.length)
const isFiltered = computed(() => filterType.value !== 'all')

watch(filterType, () => { displayCount.value = PAGE_SIZE })
watch(() => props.resources.length, () => {
  displayCount.value = PAGE_SIZE
})

function clearFilters() {
  filterType.value = 'all'
}

function doQuery() {
  const timeStart = pendingTimeStart.value ? new Date(pendingTimeStart.value).getTime() : 0
  const timeEnd = pendingTimeEnd.value ? new Date(pendingTimeEnd.value).getTime() : Infinity
  const results = props.resources.filter(r => {
    const t = new Date(r.create_time || r.timestamp).getTime()
    const matchTime = t >= timeStart && t <= timeEnd
    const url = r.res_link || r.url
    const matchTarget = !pendingTargetUrl.value || (url && url.startsWith(pendingTargetUrl.value))
    return matchTime && matchTarget
  })
  rawResults.value = results
  hasQueried.value = true
  displayCount.value = PAGE_SIZE
}

function doReset() {
  pendingTargetUrl.value = ''
  pendingTimeStart.value = ''
  pendingTimeEnd.value = ''
  rawResults.value = []
  hasQueried.value = false
  filterType.value = 'all'
}

function loadMore() {
  if (hasMore.value) displayCount.value += PAGE_SIZE
}
</script>

<style scoped>
.query-tab {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 16px;
}

/* Query form */
.query-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--card);
  flex-shrink: 0;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 12px;
  color: var(--muted-foreground);
  letter-spacing: 0.05em;
}

.custom-select {
  position: relative;
}

.native-select {
  width: 100%;
  padding: 8px 28px 8px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--input-background);
  color: var(--foreground);
  font-size: 12px;
  font-family: inherit;
  outline: none;
  cursor: pointer;
  transition: border-color 0.15s;
  -webkit-appearance: none;
  appearance: none;
}

.native-select:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1);
}

.custom-select .chevron {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  color: var(--muted-foreground);
}

.time-range {
  display: flex;
  align-items: center;
  gap: 8px;
}

.time-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--input-background);
  color: var(--foreground);
  font-size: 12px;
  font-family: inherit;
  outline: none;
  transition: border-color 0.15s;
}

.time-input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1);
}

.time-sep {
  color: var(--muted-foreground);
  font-size: 12px;
}

.form-actions {
  display: flex;
  gap: 8px;
}

.btn-query {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px;
  border: none;
  border-radius: var(--radius);
  background: var(--primary);
  color: var(--primary-foreground);
  font-size: 12px;
  font-family: inherit;
  letter-spacing: 0.05em;
  transition: opacity 0.15s;
  cursor: pointer;
}

.btn-query:hover {
  opacity: 0.9;
}

.btn-reset {
  padding: 8px 16px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--secondary);
  color: var(--muted-foreground);
  font-size: 12px;
  font-family: inherit;
  transition: all 0.15s;
  cursor: pointer;
}

.btn-reset:hover {
  color: var(--foreground);
}

/* Content */
.content-area {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

.detail-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.initial-state {
  flex: 1;
  display: flex;
  min-height: 0;
}
</style>
