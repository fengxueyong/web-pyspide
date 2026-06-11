<template>
  <header class="page-header">
    <div class="header-main">
      <div class="input-group input-group-url">
        <label class="label">抓取链接</label>
        <textarea
          v-model="url"
          class="input url-input"
          placeholder="请输入网址链接..."
          rows="4"
          @keydown.enter.prevent="handleStart"
        ></textarea>
      </div>
      <div class="input-group">
        <label class="label">资源类型</label>
        <select v-model="resType" class="select">
          <option v-for="opt in typeOptions" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </option>
        </select>
      </div>
      <div class="input-group">
        <label class="label">代理配置</label>
        <select v-model="proxyId" class="select">
          <option :value="-1">不使用代理</option>
          <option v-for="p in proxyList" :key="p.id" :value="p.id">
            {{ p.name }}
          </option>
        </select>
      </div>
      <button class="btn btn-start" :disabled="loading" @click="handleStart">
        {{ loading ? '抓取中...' : '开始抓取' }}
      </button>
    </div>

    <button class="btn-setting" @click="showSettings = true">配置</button>

    <div class="header-hidden">
      <div class="hidden-item">
        <label>抓取深度：</label>
        <select v-model="depth" class="select-sm">
          <option :value="1">1</option>
          <option :value="2">2</option>
          <option :value="3">3</option>
        </select>
      </div>
      <div class="hidden-item">
        <label>跟随链接：</label>
        <select v-model="linkFollow" class="select-sm">
          <option :value="0">否</option>
          <option :value="1">是</option>
        </select>
      </div>
      <div class="hidden-item">
        <label>保存方式：</label>
        <select v-model="saveMethod" class="select-sm">
          <option value="only_record">仅记录元数据</option>
          <option value="download">下载文件</option>
        </select>
      </div>
    </div>
  </header>

  <div class="progress-feed">
    <div v-if="messages.length === 0" class="progress-placeholder">暂无抓取记录</div>
    <div
      v-for="(msg, idx) in messages"
      :key="idx"
      class="progress-item"
    >
      {{ msg.event === 'resource_found' ? msg.data.res_link : msg.event }}
    </div>
  </div>

  <SettingsDialog
    :visible="showSettings"
    @close="onSettingsClose"
  />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { startCrawl, fetchProxies } from '../api'
import { useWebSocket } from '../composables/useWebSocket'
import SettingsDialog from './SettingsDialog.vue'

const emit = defineEmits(['crawl-started'])

const typeOptions = [
  { label: '全部', value: 'all' },
  { label: '文本/文章', value: 'text/article' },
  { label: '图片', value: 'image' },
  { label: '文档', value: 'doc' },
  { label: '音频', value: 'audio' },
  { label: '视频', value: 'video' },
]

const url = ref('')
const resType = ref('all')
const depth = ref(1)
const linkFollow = ref(0)
const saveMethod = ref('download')
const proxyId = ref(-1)
const proxyList = ref([])
const loading = ref(false)
const showSettings = ref(false)

const { connected, messages, connect } = useWebSocket()

async function loadProxies() {
  try {
    proxyList.value = await fetchProxies()
  } catch {
    proxyList.value = []
  }
}

function onSettingsClose() {
  showSettings.value = false
  loadProxies()
}

async function handleStart() {
  if (!url.value.trim()) return
  loading.value = true
  messages.value = []
  try {
    const data = await startCrawl({
      website: url.value.trim(),
      res_type: resType.value,
      depth: depth.value,
      link_follow: linkFollow.value,
      save_method: saveMethod.value,
      proxy_id: proxyId.value,
    })
    connect(data.task_id)
    emit('crawl-started', url.value.trim())
  } catch (err) {
    alert('启动抓取失败：' + err.message)
  } finally {
    loading.value = false
  }
}

onMounted(loadProxies)
</script>

<style scoped>
.page-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background-color: #eaf0f6;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120' viewBox='0 0 120 120'%3E%3Ccircle cx='60' cy='60' r='22' fill='none' stroke='rgba(80,140,200,0.08)' stroke-width='1.5'/%3E%3Ccircle cx='60' cy='60' r='14' fill='none' stroke='rgba(80,140,200,0.06)' stroke-width='1'/%3E%3Ccircle cx='60' cy='60' r='4' fill='rgba(80,140,200,0.05)'/%3E%3Cellipse cx='60' cy='35' rx='6' ry='12' fill='none' stroke='rgba(80,140,200,0.07)' stroke-width='0.8' transform='rotate(0 60 60)'/%3E%3Cellipse cx='60' cy='35' rx='6' ry='12' fill='none' stroke='rgba(80,140,200,0.07)' stroke-width='0.8' transform='rotate(45 60 60)'/%3E%3Cellipse cx='60' cy='35' rx='6' ry='12' fill='none' stroke='rgba(80,140,200,0.07)' stroke-width='0.8' transform='rotate(90 60 60)'/%3E%3Cellipse cx='60' cy='35' rx='6' ry='12' fill='none' stroke='rgba(80,140,200,0.07)' stroke-width='0.8' transform='rotate(135 60 60)'/%3E%3C/svg%3E");
  border-bottom: 1px solid #c8d6e5;
  padding: 16px 24px 12px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

.header-main {
  display: flex;
  align-items: flex-end;
  gap: 12px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.input-group-url {
  flex: 1;
  min-width: 0;
}

.label {
  font-size: 13px;
  color: #2c3e50;
  font-weight: 600;
}

.url-input {
  width: 100%;
  min-height: 42px;
  padding: 8px 12px;
  resize: vertical;
  font-family: inherit;
  line-height: 1.4;
  overflow: auto;
}

.input, .select {
  height: 36px;
  padding: 0 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

textarea.input {
  height: auto;
}

.input:focus, .select:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15);
}

.select {
  width: 140px;
}

.btn-start {
  height: 44px;
  padding: 0 32px;
  background: #dc2626;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
}

.btn-start:hover:not(:disabled) {
  background: #b91c1c;
}

.btn-start:disabled {
  background: #fca5a5;
  cursor: not-allowed;
}

.btn-setting {
  position: absolute;
  top: 12px;
  right: 24px;
  height: 32px;
  padding: 0 14px;
  background: rgba(80, 120, 180, 0.15);
  color: #2c3e50;
  border: 1px solid rgba(80, 120, 180, 0.3);
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
}

.btn-setting:hover {
  background: rgba(80, 120, 180, 0.25);
}

.header-hidden {
  display: none;
}

.hidden-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #6b7280;
}

.select-sm {
  height: 28px;
  padding: 0 8px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 13px;
  outline: none;
}

.progress-feed {
  height: 100px;
  overflow-y: auto;
  background: rgba(255, 255, 255, 0.85);
  padding: 8px 12px;
}

.progress-placeholder {
  font-size: 12px;
  color: #9ca3af;
  text-align: center;
  padding: 36px 0;
}

.progress-item {
  font-size: 12px;
  color: #6b7280;
  padding: 2px 0;
  border-bottom: 1px solid #f3f4f6;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.progress-item:last-child {
  border-bottom: none;
}
</style>
