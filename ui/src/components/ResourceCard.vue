<template>
  <div
    class="resource-card"
    :class="{ 'list-mode': listMode }"
    @click="$emit('preview', resource)"
  >
    <div class="card-thumb">
      <template v-if="resource.res_type === 'pic'">
        <img :src="resource.res_link" :alt="resource.res_link" @error="onImgError" />
      </template>
      <template v-else-if="resource.res_type === 'video'">
        <div class="thumb-placeholder video-placeholder">
          <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="5 3 19 12 5 21 5 3" />
          </svg>
        </div>
      </template>
      <template v-else-if="resource.res_type === 'audio'">
        <div class="thumb-placeholder audio-placeholder">
          <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 18V5l12-2v13" />
            <circle cx="6" cy="18" r="3" />
            <circle cx="18" cy="16" r="3" />
          </svg>
        </div>
      </template>
      <template v-else-if="resource.res_type === 'doc'">
        <div class="thumb-placeholder doc-placeholder">
          <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="16" y1="13" x2="8" y2="13" />
            <line x1="16" y1="17" x2="8" y2="17" />
          </svg>
        </div>
      </template>
      <template v-else>
        <div class="thumb-placeholder text-placeholder">
          <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
          </svg>
        </div>
      </template>
    </div>
    <div class="card-info">
      <div class="card-link" :title="resource.res_link">{{ resource.res_link }}</div>
      <div class="card-meta">
        <span class="meta-type">{{ typeLabels[resource.res_type] || resource.res_type }}</span>
        <span class="meta-size">{{ formatSize(resource.res_size) }}</span>
        <span class="meta-time">{{ formatTime(resource.create_time) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  resource: { type: Object, required: true },
  listMode: { type: Boolean, default: false },
})

defineEmits(['preview'])

const typeLabels = {
  'text/article': '文章',
  pic: '图片',
  doc: '文档',
  audio: '音频',
  video: '视频',
}

function onImgError(e) {
  e.target.style.display = 'none'
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
</script>

<style scoped>
.resource-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: box-shadow 0.2s;
  background: #fff;
}

.resource-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.card-thumb {
  width: 100%;
  height: 160px;
  overflow: hidden;
  background: #f3f4f6;
}

.card-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumb-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
}

.video-placeholder { background: #1e1b4b; color: #a78bfa; }
.audio-placeholder { background: #064e3b; color: #34d399; }
.doc-placeholder { background: #1c1917; color: #fbbf24; }
.text-placeholder { background: #172554; color: #60a5fa; }

.card-info {
  padding: 10px 12px;
}

.card-link {
  font-size: 13px;
  color: #1f2937;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 6px;
}

.card-meta {
  display: flex;
  gap: 10px;
  font-size: 12px;
  color: #9ca3af;
}

.meta-type {
  color: #3b82f6;
}

/* list mode */
.list-mode {
  display: flex;
  flex-direction: row;
  border-radius: 6px;
}

.list-mode .card-thumb {
  width: 120px;
  min-width: 120px;
  height: 80px;
}

.list-mode .card-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
</style>
