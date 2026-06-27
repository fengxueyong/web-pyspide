<template>
  <div class="detail-card" @click="openLink">
    <div class="card-indicator" :class="statusClass"></div>
    <div class="card-body">
      <div class="card-row">
        <span class="type-tag" :class="'type-' + typeKey">
          {{ typeLabel }}
        </span>
        <span class="status-tag" :class="statusClass">{{ statusCode }}</span>
        <span class="card-depth">深度 {{ depth }}</span>
        <span class="card-size">{{ displaySize }}</span>
      </div>
      <div class="card-url">
        <span class="url-text">{{ resourceUrl }}</span>
        <component :is="Icons.externalLink" :size="11" class="external-icon" />
      </div>
      <div class="card-meta">
        <span>{{ contentType || typeKey || '-' }}</span>
        <span>{{ displayTime }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Icons } from './Icons'

const props = defineProps({
  resource: { type: Object, required: true },
})

const resourceUrl = computed(() => props.resource.res_link || props.resource.url || '')
const typeKey = computed(() => props.resource.res_type || props.resource.type || '')
const statusCode = computed(() => props.resource.status || props.resource.res_status || 200)
const depth = computed(() => props.resource.depth || 1)
const contentType = computed(() => props.resource.contentType || props.resource.res_type || '')

const typeLabel = computed(() => {
  const map = { image: '图片', video: '视频', doc: '文档' }
  return map[typeKey.value] || typeKey.value || '未知'
})

const statusClass = computed(() => {
  const s = statusCode.value
  if (s >= 400) return 'status-error'
  if (s >= 300) return 'status-warn'
  return 'status-ok'
})

const displaySize = computed(() => {
  const bytes = props.resource.res_size
  if (!bytes && bytes !== 0) return ''
  if (bytes === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  let size = bytes
  while (size >= 1024 && i < units.length - 1) {
    size /= 1024
    i++
  }
  return size.toFixed(i > 0 ? 1 : 0) + ' ' + units[i]
})

const displayTime = computed(() => {
  const t = props.resource.create_time || props.resource.timestamp
  if (!t) return ''
  const d = new Date(t)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
})

function openLink() {
  if (resourceUrl.value) {
    window.open(resourceUrl.value, '_blank', 'noopener,noreferrer')
  }
}
</script>

<style scoped>
.detail-card {
  display: flex;
  gap: 12px;
  padding: 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--card);
  cursor: pointer;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.detail-card:hover {
  border-color: var(--primary);
  box-shadow: 0 1px 4px rgba(99, 102, 241, 0.08);
}
.card-indicator {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  margin-top: 4px;
  flex-shrink: 0;
}
.card-indicator.status-ok { background: var(--primary); }
.card-indicator.status-warn { background: #eab308; }
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
.type-tag.type-image { color: #7c3aed; background: #f5f3ff; border-color: #ddd6fe; }
.type-tag.type-video { color: #db2777; background: #fdf2f8; border-color: #fbcfe8; }
.type-tag.type-doc { color: #ea580c; background: #fff7ed; border-color: #fed7aa; }
.type-tag.type-text\/article { color: #2563eb; background: #eff6ff; border-color: #bfdbfe; }

.status-tag {
  padding: 2px 6px;
  border-radius: var(--radius);
  font-size: 11px;
}
.status-tag.status-ok { color: var(--primary); background: rgba(99, 102, 241, 0.1); }
.status-tag.status-warn { color: #ca8a04; background: rgba(234, 179, 8, 0.1); }
.status-tag.status-error { color: var(--destructive); background: rgba(239, 68, 68, 0.1); }

.card-depth { font-size: 11px; color: var(--muted-foreground); }
.card-size { font-size: 11px; color: var(--muted-foreground); margin-left: auto; }

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
.detail-card:hover .external-icon { opacity: 0.6; }
.detail-card:hover .external-icon:hover { opacity: 1; color: var(--primary); }

.card-meta {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: var(--muted-foreground);
}
</style>
