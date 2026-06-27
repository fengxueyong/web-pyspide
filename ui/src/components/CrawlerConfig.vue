<template>
  <div class="crawler-config">
    <!-- Header -->
    <div class="section-header">
      <span class="pulse-dot"></span>
      <span class="section-title">爬虫配置</span>
    </div>

    <!-- URL input -->
    <div class="field">
      <label class="field-label">
        目标 URL
        <span class="field-hint">（每行一个，支持长 URL 自动换行）</span>
      </label>
      <textarea
        v-model="url"
        class="url-input"
        placeholder="https://example.com"
        rows="5"
        :disabled="isRunning"
      ></textarea>
    </div>

    <!-- Resource type & Depth -->
    <div class="grid-2col">
      <div class="field">
        <label class="field-label">资源类型</label>
        <div class="custom-select" ref="typeSelectRef">
          <button class="select-trigger" :disabled="isRunning" @click="typeOpen = !typeOpen">
            <span class="select-icon"><component :is="selectedType.icon" :size="13" /></span>
            <span class="select-value">{{ selectedType.label }}</span>
            <component :is="Icons.chevronDown" :size="13" class="chevron" :class="{ rotated: typeOpen }" />
          </button>
          <div v-if="typeOpen" class="select-dropdown">
            <button
              v-for="opt in typeOptions"
              :key="opt.value"
              class="select-option"
              :class="{ active: resourceType === opt.value }"
              @click="selectType(opt.value)"
            >
              <span class="select-icon"><component :is="opt.icon" :size="13" /></span>
              {{ opt.label }}
            </button>
          </div>
        </div>
      </div>
      <div class="field">
        <label class="field-label">抓取深度</label>
        <div class="custom-select">
          <select v-model="depth" class="native-select" :disabled="isRunning">
            <option :value="1">深度 1</option>
            <option :value="2">深度 2</option>
            <option :value="3">深度 3</option>
          </select>
          <component :is="Icons.chevronDown" :size="13" class="chevron" />
        </div>
      </div>
    </div>

    <!-- Proxy settings -->
    <div class="proxy-section">
      <div class="proxy-header">
        <div class="proxy-header-left">
          <component :is="Icons.shield" :size="13" />
          <span class="field-label">代理设置</span>
        </div>
        <button
          class="toggle-btn"
          :class="{ active: useProxy }"
          :disabled="isRunning"
          @click="useProxy = !useProxy"
        >
          <component :is="useProxy ? Icons.wifi : Icons.wifiOff" :size="11" />
          {{ useProxy ? '已启用' : '已禁用' }}
        </button>
      </div>
      <div v-if="useProxy" class="proxy-fields">
        <div class="flex-row">
          <input v-model="proxyHost" class="proxy-input flex-1" placeholder="代理地址" :disabled="isRunning" />
          <input v-model="proxyPort" class="proxy-input port" placeholder="端口" :disabled="isRunning" />
        </div>
        <div class="flex-row">
          <div class="input-with-icon flex-1">
            <component :is="Icons.user" :size="11" />
            <input v-model="proxyUser" class="proxy-input" placeholder="用户名（可选）" :disabled="isRunning" />
          </div>
          <div class="input-with-icon flex-1">
            <component :is="Icons.lock" :size="11" />
            <input v-model="proxyPass" class="proxy-input" type="password" placeholder="密码（可选）" :disabled="isRunning" />
          </div>
        </div>
      </div>
    </div>

    <!-- Start / Stop button -->
    <button
      class="action-btn"
      :class="{ running: isRunning }"
      @click="isRunning ? stopCrawl() : startCrawl()"
    >
      <component :is="isRunning ? Icons.square : Icons.play" :size="14" />
      {{ isRunning ? '停止抓取' : '开始抓取' }}
    </button>

    <!-- Real-time log -->
    <div class="log-section">
      <div class="log-header">
        <span class="field-label">实时日志</span>
        <span class="log-count">{{ logs.length }} 条</span>
      </div>
      <div ref="logRef" class="log-output">
        <div v-if="logs.length === 0" class="log-empty">暂无抓取记录</div>
        <div v-for="(log, i) in logs" :key="i" class="log-entry">
          <span class="log-time">{{ log.time }}</span>
          <span class="log-level" :class="'level-' + log.level">{{ levelLabel(log.level) }}</span>
          <span class="log-msg">{{ log.msg }}</span>
        </div>
        <div v-if="isRunning" class="log-cursor">
          <span class="log-time">{{ currentTime }}</span>
          <span class="log-level level-info">信息</span>
          <span class="log-msg cursor-blink">_</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { Icons } from './Icons'
import { startCrawl as apiStartCrawl } from '../api'
import { useWebSocket } from '../composables/useWebSocket'

const emit = defineEmits(['crawl-started', 'resources-update'])

const { connected, messages, lastMessage, connect } = useWebSocket()

// Form state
const url = ref('')
const resourceType = ref('all')
const depth = ref(1)
const useProxy = ref(false)
const proxyHost = ref('127.0.0.1')
const proxyPort = ref('7890')
const proxyUser = ref('')
const proxyPass = ref('')
const isRunning = ref(false)
const typeOpen = ref(false)
const typeSelectRef = ref(null)

const typeOptions = [
  { value: 'all', label: '全部类型', icon: Icons.layers },
  { value: 'image', label: '图片', icon: Icons.image },
  { value: 'video', label: '视频', icon: Icons.video },
  { value: 'doc', label: '文档', icon: Icons.download },
]

const selectedType = computed(() => typeOptions.find(o => o.value === resourceType.value) || typeOptions[0])

const logs = ref([])
const logRef = ref(null)
const crawledResources = ref([])

// Current time for cursor blink
const currentTime = ref('')
let timeTimer = null

// Auto-scroll logs
watch(logs, () => {
  nextTick(() => {
    if (logRef.value) {
      logRef.value.scrollTop = logRef.value.scrollHeight
    }
  })
}, { deep: true })

// Watch WebSocket messages
watch(lastMessage, (msg) => {
  if (!msg) return
  if (msg.event === 'resource_found') {
    const resource = msg.data
    addLog('success', resource.res_link)
    crawledResources.value.push(resource)
    emit('resources-update', [...crawledResources.value])
  } else if (msg.event === 'error') {
    addLog('error', typeof msg.data === 'string' ? msg.data : JSON.stringify(msg.data))
  } else if (msg.event === 'info') {
    addLog('info', typeof msg.data === 'string' ? msg.data : JSON.stringify(msg.data))
  } else if (msg.event === 'complete' || msg.event === 'task_finished') {
    addLog('success', '抓取完成')
    isRunning.value = false
  }
})

function formatTime() {
  const d = new Date()
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}:${String(d.getSeconds()).padStart(2, '0')}`
}

function levelLabel(level) {
  const map = { success: '成功', error: '错误', warn: '警告', info: '信息' }
  return map[level] || level
}

function addLog(level, msg) {
  logs.value.push({ time: formatTime(), level, msg })
  if (logs.value.length > 300) logs.value.shift()
}

function selectType(val) {
  resourceType.value = val
  typeOpen.value = false
}

// Close dropdown on outside click
function onDocumentClick(e) {
  if (typeSelectRef.value && !typeSelectRef.value.contains(e.target)) {
    typeOpen.value = false
  }
}

async function startCrawl() {
  const urls = url.value.trim().split('\n').map(u => u.trim()).filter(Boolean)
  if (!urls.length) {
    addLog('warn', '请先输入目标 URL')
    return
  }

  isRunning.value = true
  logs.value = []
  crawledResources.value = []
  emit('resources-update', [])
  addLog('info', '初始化爬虫引擎...')
  addLog('info', `目标 URL（${urls.length} 个）：`)
  urls.forEach((u, i) => addLog('info', `  [${i + 1}] ${u}`))
  addLog('info', `资源类型：${selectedType.value.label} | 深度：${depth.value}`)
  if (useProxy.value) {
    addLog('info', `代理：${proxyHost.value}:${proxyPort.value}${proxyUser.value ? `（用户：${proxyUser.value}）` : ''}`)
  }

  try {
    const data = await apiStartCrawl({
      website: urls[0],
      res_type: resourceType.value,
      depth: depth.value,
      link_follow: depth.value > 1 ? 1 : 0,
      save_method: 'download',
      proxy_id: useProxy.value ? -1 : -1,
    })

    addLog('success', '▶ 开始抓取任务')
    connect(data.task_id)
    emit('crawl-started', urls[0])
  } catch (err) {
    addLog('error', '启动失败：' + err.message)
    isRunning.value = false
  }
}

function stopCrawl() {
  isRunning.value = false
  addLog('warn', '■ 任务已手动停止')
}

// Update current time every second for the cursor
function startTimeTimer() {
  currentTime.value = formatTime()
  timeTimer = setInterval(() => {
    currentTime.value = formatTime()
  }, 1000)
}

onMounted(() => {
  document.addEventListener('click', onDocumentClick)
  startTimeTimer()
})

onUnmounted(() => {
  document.removeEventListener('click', onDocumentClick)
  if (timeTimer) clearInterval(timeTimer)
})
</script>

<style scoped>
.crawler-config {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
}

/* Section header */
.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
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

/* Field */
.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 12px;
  color: var(--muted-foreground);
  letter-spacing: 0.05em;
  display: flex;
  align-items: center;
  gap: 4px;
}

.field-hint {
  opacity: 0.6;
  font-weight: 400;
}

/* URL Textarea */
.url-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--input-background);
  color: var(--foreground);
  font-size: 12px;
  font-family: inherit;
  outline: none;
  resize: vertical;
  line-height: 1.6;
  transition: border-color 0.15s, box-shadow 0.15s;
  word-break: break-all;
  overflow-wrap: break-word;
  white-space: pre-wrap;
}

.url-input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1);
}

.url-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Grid */
.grid-2col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

/* Custom select */
.custom-select {
  position: relative;
}

.select-trigger {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--input-background);
  color: var(--foreground);
  font-size: 12px;
  font-family: inherit;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.select-trigger:hover:not(:disabled) {
  border-color: var(--primary);
}

.select-trigger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.select-icon {
  display: flex;
  color: var(--primary);
  flex-shrink: 0;
}

.select-value {
  flex: 1;
  text-align: left;
}

.chevron {
  color: var(--muted-foreground);
  flex-shrink: 0;
  transition: transform 0.2s;
}

.chevron.rotated {
  transform: rotate(180deg);
}

.select-dropdown {
  position: absolute;
  z-index: 50;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: var(--popover);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.select-option {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  text-align: left;
  font-size: 12px;
  color: var(--popover-foreground);
  background: transparent;
  border: none;
  font-family: inherit;
  transition: background 0.1s;
}

.select-option:hover {
  background: var(--secondary);
}

.select-option.active {
  color: var(--primary);
  background: rgba(99, 102, 241, 0.08);
}

.native-select {
  width: 100%;
  padding: 8px 28px 8px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--input-background);
  color: var(--foreground);
  font-size: 12px;
  font-family: inherit;
  outline: none;
  cursor: pointer;
  transition: border-color 0.15s;
  -webkit-appearance: none;
  appearance: none;
}

.native-select:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1);
}

.native-select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.custom-select .chevron {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
}

/* Proxy section */
.proxy-section {
  padding: 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--input-background);
}

.proxy-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.proxy-header-left {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--muted-foreground);
}

.toggle-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: var(--radius);
  border: none;
  font-size: 12px;
  font-family: inherit;
  background: var(--secondary);
  color: var(--muted-foreground);
  transition: all 0.15s;
}

.toggle-btn.active {
  background: var(--primary);
  color: var(--primary-foreground);
}

.toggle-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.proxy-fields {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
}

.flex-row {
  display: flex;
  gap: 8px;
}

.flex-1 {
  flex: 1;
}

.proxy-input {
  width: 100%;
  padding: 6px 10px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--card);
  color: var(--foreground);
  font-size: 12px;
  font-family: inherit;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.proxy-input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1);
}

.proxy-input:disabled {
  opacity: 0.5;
}

.proxy-input.port {
  width: 80px;
  flex: none;
}

.input-with-icon {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--card);
  color: var(--muted-foreground);
  transition: border-color 0.15s, box-shadow 0.15s;
}

.input-with-icon:focus-within {
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1);
}

.input-with-icon .proxy-input {
  padding: 0;
  border: none;
  background: transparent;
}

/* Action button */
.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px;
  border: none;
  border-radius: var(--radius);
  font-size: 13px;
  font-family: inherit;
  letter-spacing: 0.05em;
  font-weight: 600;
  transition: all 0.15s;
  background: var(--primary);
  color: var(--primary-foreground);
}

.action-btn:hover {
  opacity: 0.9;
}

.action-btn.running {
  background: transparent;
  border: 1px solid var(--destructive);
  color: var(--destructive);
}

.action-btn.running:hover {
  background: var(--destructive);
  color: var(--destructive-foreground);
}

/* Log section */
.log-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  min-height: 0;
}

.log-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.log-count {
  font-size: 12px;
  color: var(--muted-foreground);
}

.log-output {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 12px;
  font-size: 12px;
  line-height: 1.8;
}

.log-empty {
  color: var(--muted-foreground);
  text-align: center;
  padding: 24px 0;
}

.log-entry {
  display: flex;
  gap: 8px;
  align-items: baseline;
}

.log-time {
  color: var(--muted-foreground);
  flex-shrink: 0;
  min-width: 65px;
  font-variant-numeric: tabular-nums;
}

.log-level {
  flex-shrink: 0;
  min-width: 32px;
  font-size: 11px;
  padding: 0 4px;
  border-radius: 3px;
  text-align: center;
  font-weight: 500;
}

.level-success {
  color: #059669;
  background: rgba(5, 150, 105, 0.1);
}

.level-error {
  color: var(--destructive);
  background: rgba(239, 68, 68, 0.1);
}

.level-warn {
  color: #ca8a04;
  background: rgba(234, 179, 8, 0.1);
}

.level-info {
  color: var(--muted-foreground);
  background: rgba(100, 116, 139, 0.1);
}

.log-msg {
  color: var(--foreground);
  opacity: 0.85;
  word-break: break-all;
}

.log-cursor {
  display: flex;
  gap: 8px;
  margin-top: 2px;
  align-items: baseline;
}

.cursor-blink {
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}
</style>
