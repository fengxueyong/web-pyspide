<template>
  <div class="live-tab">
    <FilterBar
      v-model="filterType"
      :is-filtered="isFiltered"
      :view-mode="viewMode"
      :result-count="displayed.length"
      :total-count="filtered.length"
      @update:view-mode="viewMode = $event"
      @clear="clearFilters"
    />

    <div class="content-area" ref="scrollRef">
      <!-- Empty state: no resources -->
      <EmptyState
        v-if="resources.length === 0"
        :icon="Icons.database"
        title="等待抓取任务..."
        sub="配置左侧参数后点击「开始抓取」"
      />

      <!-- Empty state: filtered out -->
      <EmptyState
        v-else-if="filtered.length === 0"
        :icon="Icons.search"
        title="无匹配结果"
      />

      <!-- Detail view -->
      <div v-else-if="viewMode === 'detail'" class="detail-list">
        <DetailCard v-for="r in displayed" :key="r.id || r.res_link || r.url" :resource="r" />
        <ScrollAnchor :has-more="hasMore" @load-more="loadMore" />
      </div>

      <!-- Thumbnail view -->
      <ThumbnailGrid v-else :items="displayed" :has-more="hasMore" @load-more="loadMore" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
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

const viewMode = ref('detail')
const filterType = ref('all')
const displayCount = ref(PAGE_SIZE)

const filtered = computed(() => {
  return props.resources.filter(r => {
    const type = r.res_type || r.type
    return filterType.value === 'all' || type === filterType.value
  })
})

const displayed = computed(() => filtered.value.slice(0, displayCount.value))
const hasMore = computed(() => displayCount.value < filtered.value.length)
const isFiltered = computed(() => filterType.value !== 'all')

watch(filterType, () => { displayCount.value = PAGE_SIZE })

function clearFilters() {
  filterType.value = 'all'
}

function loadMore() {
  if (hasMore.value) displayCount.value += PAGE_SIZE
}
</script>

<style scoped>
.live-tab {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 12px;
}

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
</style>
