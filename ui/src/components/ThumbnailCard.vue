<template>
  <div class="thumb-card" @click="openLink">
    <div class="thumb-preview">
      <img
        v-if="isImage"
        :src="imageUrl"
        :alt="resourceUrl"
        class="thumb-img"
        @error="onImgError"
      />
      <div v-else class="thumb-placeholder">
        <component :is="typeIcon" :size="24" />
        <span>{{ typeLabel }}</span>
      </div>
      <span class="thumb-status" :class="statusClass">{{ statusCode }}</span>
      <div class="thumb-overlay">
        <component :is="Icons.externalLink" :size="18" />
      </div>
    </div>
    <div class="thumb-info">
      <div class="thumb-type-row">
        <span class="type-tag-sm" :class="'type-' + typeKey">{{ typeLabel }}</span>
        <span class="thumb-size">{{ displaySize }}</span>
      </div>
      <span class="thumb-name">{{ fileName }}</span>
      <span class="thumb-url">{{ resourceUrl }}</span>
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
const isImage = computed(() => typeKey.value === 'image')

const typeLabel = computed(() => {
  const map = { image: '图片', video: '视频', doc: '文档', 'text/article': '文章' }
  return map[typeKey.value] || typeKey.value || '未知'
})

const typeIcon = computed(() => {
  const map = { image: Icons.image, video: Icons.video, doc: Icons.download }
  return map[typeKey.value] || Icons.layers
})

const statusClass = computed(() => {
  const s = statusCode.value
  if (s >= 400) return 'status-error'
  if (s >= 300) return 'status-warn'
  return 'status-ok'
})

const imageUrl = computed(() => {
  if (!resourceUrl.value) return ''
  return `/api/crawl/proxy-image?url=${encodeURIComponent(resourceUrl.value)}`
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

const fileName = computed(() => {
  return (resourceUrl.value || '').split('/').pop() || ''
})

function onImgError(e) {
  e.target.style.display = 'none'
}

function openLink() {
  if (resourceUrl.value) {
    window.open(resourceUrl.value, '_blank', 'noopener,noreferrer')
  }
}
</script>

<style scoped>
.thumb-card {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  background: var(--card);
  cursor: pointer;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.thumb-card:hover {
  border-color: var(--primary);
  box-shadow: 0 1px 4px rgba(99, 102, 241, 0.08);
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
.thumb-card:hover .thumb-img { transform: scale(1.05); }
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
  z-index: 2;
}
.thumb-status.status-ok { background: rgba(99, 102, 241, 0.85); color: white; }
.thumb-status.status-warn { background: rgba(234, 179, 8, 0.85); color: white; }
.thumb-status.status-error { background: rgba(239, 68, 68, 0.85); color: white; }

.thumb-overlay {
  position: absolute;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
  color: white;
  z-index: 1;
}
.thumb-card:hover .thumb-overlay { opacity: 1; }

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
.type-tag-sm.type-image { color: #7c3aed; background: #f5f3ff; border-color: #ddd6fe; }
.type-tag-sm.type-video { color: #db2777; background: #fdf2f8; border-color: #fbcfe8; }
.type-tag-sm.type-doc { color: #ea580c; background: #fff7ed; border-color: #fed7aa; }
.type-tag-sm.type-text\/article { color: #2563eb; background: #eff6ff; border-color: #bfdbfe; }
.thumb-size { font-size: 11px; color: var(--muted-foreground); }
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
</style>
