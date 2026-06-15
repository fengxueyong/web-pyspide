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
          <svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>
          {{ resources.length }} 条
        </span>
        <span class="stat-item stat-ok">
          <svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
          {{ stats.ok }} 成功
        </span>
        <span class="stat-item stat-err">
          <svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
          {{ stats.err }} 失败
        </span>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button class="tab-btn" :class="{ active: activeTab === 'live' }" @click="activeTab = 'live'">
        <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
        实时抓取
        <span v-if="resources.length > 0" class="tab-badge">{{ resources.length }}</span>
      </button>
      <button class="tab-btn" :class="{ active: activeTab === 'query' }" @click="switchToQuery">
        <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
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
  background: rgba(22, 100, 48, 0.12);
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
