<template>
  <header class="page-header">
    <div class="header-main">
      <div class="input-group">
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
        <div class="proxy-row">
          <select v-model="proxyId" class="select">
            <option :value="-1">不使用代理</option>
            <option v-for="p in proxyList" :key="p.id" :value="p.id">
              {{ p.name }}
            </option>
          </select>
          <button class="btn btn-setting" @click="showSettings = true">配置</button>
        </div>
      </div>
      <button class="btn btn-start" :disabled="loading" @click="handleStart">
        {{ loading ? '抓取中...' : '开始抓取' }}
      </button>
    </div>

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

    <div v-if="messages.length > 0" class="progress-feed">
      <div
        v-for="(msg, idx) in messages"
        :key="idx"
        class="progress-item"
      >
        {{ msg.event === 'resource_found' ? msg.data.res_link : msg.event }}
      </div>
    </div>
  </header>

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
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  padding: 16px 24px 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
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

.label {
  font-size: 13px;
  color: #374151;
  font-weight: 500;
}

.url-input {
  width: 420px;
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

.proxy-row {
  display: flex;
  gap: 6px;
}

.proxy-row .select {
  width: 110px;
}

.btn {
  height: 36px;
  padding: 0 14px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
}

.btn-start {
  background: #3b82f6;
  color: #fff;
}

.btn-start:hover:not(:disabled) {
  background: #2563eb;
}

.btn-start:disabled {
  background: #93c5fd;
  cursor: not-allowed;
}

.btn-setting {
  background: #e5e7eb;
  color: #374151;
}

.btn-setting:hover {
  background: #d1d5db;
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
  margin-top: 10px;
  max-height: 120px;
  overflow-y: auto;
  background: #f9fafb;
  border-radius: 6px;
  padding: 8px 12px;
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
