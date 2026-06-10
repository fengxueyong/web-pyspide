<template>
  <Teleport to="body">
    <div v-if="visible" class="modal-overlay" @click.self="$emit('close')">
      <div class="modal-body">
        <button class="modal-close" @click="$emit('close')">&times;</button>

        <div v-if="resource" class="preview-content">
          <template v-if="resource.res_type === 'pic'">
            <img :src="resource.res_link" class="preview-img" alt="preview" @error="onMediaError" />
          </template>

          <template v-else-if="resource.res_type === 'video'">
            <video controls autoplay class="preview-video" :src="resource.res_link">
              您的浏览器不支持视频播放
            </video>
          </template>

          <template v-else-if="resource.res_type === 'audio'">
            <div class="audio-wrapper">
              <div class="audio-icon">
                <svg viewBox="0 0 24 24" width="64" height="64" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M9 18V5l12-2v13" />
                  <circle cx="6" cy="18" r="3" />
                  <circle cx="18" cy="16" r="3" />
                </svg>
              </div>
              <audio controls autoplay :src="resource.res_link" class="preview-audio">
                您的浏览器不支持音频播放
              </audio>
            </div>
          </template>

          <template v-else>
            <div class="preview-info">
              <div class="info-row">
                <span class="info-label">链接：</span>
                <a :href="resource.res_link" target="_blank" class="info-value link">{{ resource.res_link }}</a>
              </div>
              <div class="info-row">
                <span class="info-label">类型：</span>
                <span class="info-value">{{ typeLabels[resource.res_type] || resource.res_type }}</span>
              </div>
              <div class="info-row" v-if="resource.res_size">
                <span class="info-label">大小：</span>
                <span class="info-value">{{ formatSize(resource.res_size) }}</span>
              </div>
              <div class="info-row" v-if="resource.create_time">
                <span class="info-label">抓取时间：</span>
                <span class="info-value">{{ formatTime(resource.create_time) }}</span>
              </div>
            </div>
          </template>

          <div class="preview-link-bar">
            <a :href="resource.res_link" target="_blank" class="open-link">在新窗口打开 &rarr;</a>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  visible: { type: Boolean, default: false },
  resource: { type: Object, default: null },
})

defineEmits(['close'])

const typeLabels = {
  'text/article': '文本/文章',
  pic: '图片',
  doc: '文档',
  audio: '音频',
  video: '视频',
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

function onMediaError(e) {
  e.target.style.display = 'none'
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.modal-body {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
  background: #fff;
  border-radius: 12px;
  overflow: auto;
  padding: 24px;
}

.modal-close {
  position: absolute;
  top: 8px;
  right: 12px;
  font-size: 28px;
  color: #6b7280;
  background: none;
  border: none;
  cursor: pointer;
  line-height: 1;
  z-index: 1;
}

.modal-close:hover {
  color: #111827;
}

.preview-img {
  max-width: 100%;
  max-height: 70vh;
  display: block;
  margin: 0 auto;
}

.preview-video {
  max-width: 100%;
  max-height: 70vh;
}

.audio-wrapper {
  text-align: center;
  padding: 40px 20px;
}

.audio-icon {
  color: #3b82f6;
  margin-bottom: 24px;
}

.preview-audio {
  width: 100%;
  max-width: 400px;
}

.preview-info {
  min-width: 400px;
  padding: 16px 0;
}

.info-row {
  padding: 8px 0;
  display: flex;
  gap: 8px;
  font-size: 14px;
}

.info-label {
  color: #6b7280;
  white-space: nowrap;
}

.info-value {
  color: #1f2937;
  word-break: break-all;
}

.info-value.link {
  color: #3b82f6;
}

.preview-link-bar {
  margin-top: 16px;
  text-align: center;
}

.open-link {
  font-size: 14px;
  color: #3b82f6;
  text-decoration: none;
}

.open-link:hover {
  text-decoration: underline;
}
</style>
