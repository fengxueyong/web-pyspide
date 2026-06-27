<template>
  <div class="filter-bar">
    <div class="toolbar-row">
      <button
        class="filter-toggle"
        :class="{ open: filterOpen || isFiltered }"
        @click="filterOpen = !filterOpen"
      >
        <component :is="Icons.filter" :size="12" />
        筛选
      </button>
      <div class="view-toggle">
        <button
          class="view-btn"
          :class="{ active: viewMode === 'detail' }"
          @click="$emit('update:viewMode', 'detail')"
          title="列表视图"
        >
          <component :is="Icons.list" :size="12" />
        </button>
        <button
          class="view-btn"
          :class="{ active: viewMode === 'thumbnail' }"
          @click="$emit('update:viewMode', 'thumbnail')"
          title="缩略图视图"
        >
          <component :is="Icons.grid" :size="12" />
        </button>
      </div>
    </div>

    <div v-if="filterOpen" class="filter-panel">
      <div class="filter-group">
        <span class="filter-label">类型</span>
        <div class="filter-chips">
          <button
            v-for="opt in options"
            :key="opt.value"
            class="chip"
            :class="{ active: modelValue === opt.value }"
            @click="$emit('update:modelValue', opt.value)"
          >{{ opt.label }}</button>
        </div>
      </div>
    </div>

    <div class="toolbar-info">
      <span class="result-count">显示 {{ resultCount }} / {{ totalCount }} 条</span>
      <button v-if="isFiltered" class="clear-btn" @click="$emit('clear')">
        <component :is="Icons.x" :size="10" />
        清除筛选
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Icons } from './Icons'

defineProps({
  modelValue: { type: String, default: 'all' },
  isFiltered: { type: Boolean, default: false },
  viewMode: { type: String, default: 'detail' },
  resultCount: { type: Number, default: 0 },
  totalCount: { type: Number, default: 0 },
  options: { type: Array, default: () => [
    { value: 'all', label: '全部' },
    { value: 'image', label: '图片' },
    { value: 'video', label: '视频' },
    { value: 'doc', label: '文档' },
  ]},
})

defineEmits(['update:modelValue', 'update:viewMode', 'clear'])

const filterOpen = ref(false)
</script>

<style scoped>
.filter-bar {
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
  cursor: pointer;
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
  cursor: pointer;
}
.view-btn:hover { color: var(--foreground); }
.view-btn.active {
  background: var(--primary);
  color: var(--primary-foreground);
}

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
  flex-wrap: wrap;
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
  cursor: pointer;
}
.chip:hover { color: var(--foreground); }
.chip.active {
  background: var(--primary);
  color: var(--primary-foreground);
  border-color: var(--primary);
}
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
  cursor: pointer;
  transition: color 0.15s;
}
.clear-btn:hover { color: var(--primary); }
</style>
