<template>
  <div class="resource-viewer">
    <!-- Header with stats -->
    <div class="viewer-header">
      <div class="header-left">
        <span class="pulse-dot"></span>
        <span class="section-title">资源查看</span>
      </div>
      <div class="header-stats">
        <span class="stat-item">
          <component :is="Icons.database" :size="11" />
          {{ resources.length }} 条
        </span>
        <span class="stat-item stat-ok">
          <component :is="Icons.checkCircle" :size="11" />
          {{ stats.ok }} 成功
        </span>
        <span class="stat-item stat-err">
          <component :is="Icons.alertCircle" :size="11" />
          {{ stats.err }} 失败
        </span>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button class="tab-btn" :class="{ active: activeTab === 'live' }" @click="activeTab = 'live'">
        <component :is="Icons.activity" :size="12" />
        实时抓取
        <span v-if="resources.length > 0" class="tab-badge">{{ resources.length }}</span>
      </button>
      <button class="tab-btn" :class="{ active: activeTab === 'query' }" @click="switchToQuery">
        <component :is="Icons.search" :size="12" />
        资源查询
      </button>
    </div>

    <!-- Tab content -->
    <div class="tab-content">
      <LiveTab
        v-if="activeTab === 'live'"
        :resources="resources"
      />
      <QueryTab
        v-else
        :resources="resources"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Icons } from './Icons'
import LiveTab from './LiveTab.vue'
import QueryTab from './QueryTab.vue'

const props = defineProps({
  resources: { type: Array, default: () => [] },
})

const activeTab = ref('live')

const stats = computed(() => ({
  total: props.resources.length,
  ok: props.resources.filter(r => (r.status || r.res_status || 200) < 400).length,
  err: props.resources.filter(r => (r.status || r.res_status || 200) >= 400).length,
}))

function switchToQuery() {
  activeTab.value = 'query'
}
</script>

<style scoped>
.resource-viewer {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 0;
}

.viewer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--primary);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.section-title {
  color: var(--primary);
  letter-spacing: 0.1em;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.header-stats {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: var(--muted-foreground);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-ok { color: var(--primary); }
.stat-err { color: var(--destructive); }

/* Tabs */
.tabs {
  display: flex;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border: none;
  border-bottom: 2px solid transparent;
  background: transparent;
  color: var(--muted-foreground);
  font-size: 12px;
  font-family: inherit;
  transition: all 0.15s;
  cursor: pointer;
}

.tab-btn:hover {
  color: var(--foreground);
  border-bottom-color: var(--border);
}

.tab-btn.active {
  color: var(--primary);
  border-bottom-color: var(--primary);
}

.tab-badge {
  padding: 1px 6px;
  background: rgba(99, 102, 241, 0.12);
  color: var(--primary);
  border-radius: 8px;
  font-size: 11px;
}

.tab-content {
  flex: 1;
  min-height: 0;
  padding-top: 16px;
}
</style>
