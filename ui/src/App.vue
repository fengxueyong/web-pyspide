<template>
  <div ref="containerRef" class="app-root">
    <!-- Left: config panel -->
    <div
      class="left-panel"
      :style="{ width: collapsed ? 0 : leftWidth + 'px' }"
    >
      <div class="left-panel-inner" :style="{ width: leftWidth + 'px' }">
        <CrawlerConfig
          @crawl-started="onCrawlStarted"
          @resources-update="onResourcesUpdate"
        />
      </div>
    </div>

    <!-- Drag handle + collapse toggle -->
    <div class="divider">
      <div v-if="!collapsed" class="drag-handle" @mousedown="onMouseDown"></div>
      <button class="collapse-btn" @click="collapsed = !collapsed" :title="collapsed ? '展开配置面板' : '收起配置面板'">
        <component :is="Icons.panelLeftOpen" v-if="collapsed" :size="12" />
        <component :is="Icons.panelLeftClose" v-else :size="12" />
      </button>
    </div>

    <!-- Right: resource viewer -->
    <div class="right-panel">
      <ResourceViewer :resources="resources" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Icons } from './components/Icons'
import CrawlerConfig from './components/CrawlerConfig.vue'
import ResourceViewer from './components/ResourceViewer.vue'

const MIN_LEFT = 260
const MAX_LEFT = 600
const DEFAULT_LEFT = 380

const resources = ref([])
const leftWidth = ref(DEFAULT_LEFT)
const collapsed = ref(false)

const dragging = ref(false)
const startX = ref(0)
const startWidth = ref(0)

function onMouseDown(e) {
  if (collapsed.value) return
  dragging.value = true
  startX.value = e.clientX
  startWidth.value = leftWidth.value
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
}

function onMouseMove(e) {
  if (!dragging.value) return
  const delta = e.clientX - startX.value
  const next = Math.min(MAX_LEFT, Math.max(MIN_LEFT, startWidth.value + delta))
  leftWidth.value = next
}

function onMouseUp() {
  if (!dragging.value) return
  dragging.value = false
  document.body.style.cursor = ''
  document.body.style.userSelect = ''
}

function onCrawlStarted(taskId) {
  resources.value = []
}

function onResourcesUpdate(list) {
  resources.value = list
}

onMounted(() => {
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', onMouseUp)
})

onUnmounted(() => {
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mouseup', onMouseUp)
})
</script>

<style scoped>
.app-root {
  width: 100%;
  height: 100vh;
  display: flex;
  overflow: hidden;
  background: var(--background);
  color: var(--foreground);
}

.left-panel {
  display: flex;
  flex-shrink: 0;
  overflow: hidden;
  border-right: 1px solid var(--border);
  transition: width 0.2s;
}

.left-panel-inner {
  flex-shrink: 0;
  height: 100%;
  overflow-y: auto;
  padding: 20px;
}

.left-panel-inner::-webkit-scrollbar {
  width: 3px;
}

.divider {
  position: relative;
  display: flex;
  align-items: center;
  flex-shrink: 0;
  user-select: none;
}

.drag-handle {
  position: absolute;
  inset: 0 -1px;
  width: 4px;
  cursor: col-resize;
  z-index: 10;
  transition: background 0.15s;
}

.drag-handle:hover,
.drag-handle:active {
  background: rgba(99, 102, 241, 0.2);
}

.collapse-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 48px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 0 var(--radius) var(--radius) 0;
  color: var(--muted-foreground);
  z-index: 20;
  transition: color 0.15s, border-color 0.15s, background 0.15s;
  position: relative;
  left: -1px;
}

.collapse-btn:hover {
  color: var(--primary);
  border-color: var(--primary);
}

.right-panel {
  flex: 1;
  min-width: 0;
  padding: 20px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
</style>
