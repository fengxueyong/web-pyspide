<template>
  <Teleport to="body">
    <div v-if="visible" class="modal-overlay" @click.self="$emit('close')">
      <div class="modal-body">
        <button class="modal-close" @click="$emit('close')">&times;</button>
        <h2 class="modal-title">配置管理</h2>

        <section class="config-section">
          <h3 class="section-label">代理配置</h3>

          <div class="proxy-list">
            <div v-for="item in displayList" :key="item._key" class="proxy-row">
              <template v-if="item._editing">
                <input v-model="item._form.name" class="cell-input name" placeholder="名称" />
                <input v-model="item._form.proxy_http" class="cell-input addr" placeholder="HTTP 代理地址" />
                <input v-model="item._form.proxy_https" class="cell-input addr" placeholder="HTTPS 代理地址" />
                <input v-model="item._form.username" class="cell-input user" placeholder="用户名（可选）" />
                <input v-model="item._form.password" class="cell-input pass" type="password" placeholder="密码（可选）" />
                <div class="cell-actions">
                  <button class="btn-sm btn-save" @click="saveItem(item)">保存</button>
                  <button class="btn-sm btn-cancel" @click="cancelEdit(item)">取消</button>
                </div>
              </template>
              <template v-else>
                <span class="cell-name" :title="item.name">{{ item.name }}</span>
                <span class="cell-addr" :title="item.proxy_http || '-'">{{ item.proxy_http || '-' }}</span>
                <span class="cell-addr" :title="item.proxy_https || '-'">{{ item.proxy_https || '-' }}</span>
                <div class="cell-actions">
                  <button class="btn-sm btn-edit" @click="startEdit(item)">编辑</button>
                  <button class="btn-sm btn-del" @click="deleteItem(item)">删除</button>
                </div>
              </template>
            </div>
          </div>

          <button class="btn-add" @click="addNew">+ 新增代理配置</button>
        </section>

        <section class="config-section config-section-empty">
          <h3 class="section-label">其他配置</h3>
          <p class="empty-hint">暂无</p>
        </section>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, watch } from 'vue'
import { fetchProxies, createProxy, updateProxy, deleteProxy } from '../api'

const props = defineProps({
  visible: { type: Boolean, default: false },
})

const emit = defineEmits(['close'])

const proxyList = ref([])
const displayList = ref([])

let keyCounter = 0
function nextKey() {
  return ++keyCounter
}

function buildDisplayList(list) {
  return list.map((item) => ({
    ...item,
    _key: nextKey(),
    _editing: false,
    _form: { name: '', proxy_http: '', proxy_https: '', username: '', password: '' },
    _isNew: false,
  }))
}

async function loadData() {
  try {
    const list = await fetchProxies()
    proxyList.value = list
    // 保留正在编辑中的状态
    const editingKeys = new Set(displayList.value.filter((d) => d._editing).map((d) => d._key))
    displayList.value = buildDisplayList(list)
    // 如果是新增到一半的，保留新增行
  } catch {
    displayList.value = []
  }
}

function startEdit(item) {
  item._editing = true
  item._form = {
    name: item.name || '',
    proxy_http: item.proxy_http || '',
    proxy_https: item.proxy_https || '',
    username: item.username || '',
    password: '',
  }
}

function cancelEdit(item) {
  if (item._isNew) {
    displayList.value = displayList.value.filter((d) => d._key !== item._key)
  } else {
    item._editing = false
  }
}

async function saveItem(item) {
  const form = item._form
  if (!form.name.trim()) {
    alert('名称不能为空')
    return
  }
  if (!form.proxy_http && !form.proxy_https) {
    alert('至少配置 HTTP 或 HTTPS 代理地址')
    return
  }

  const data = {
    name: form.name.trim(),
    proxy_http: form.proxy_http || null,
    proxy_https: form.proxy_https || null,
    username: form.username || null,
    password: form.password || null,
  }

  try {
    if (item._isNew) {
      await createProxy(data)
    } else {
      await updateProxy(item.id, data)
    }
    await loadData()
  } catch (err) {
    alert('保存失败：' + err.message)
  }
}

async function deleteItem(item) {
  if (!confirm(`确认删除代理配置「${item.name}」？`)) return
  try {
    await deleteProxy(item.id)
    await loadData()
  } catch (err) {
    alert('删除失败：' + err.message)
  }
}

function addNew() {
  // 检查是否已有未保存的新增行
  if (displayList.value.some((d) => d._isNew)) return
  const newItem = {
    _key: nextKey(),
    _editing: true,
    _isNew: true,
    id: null,
    name: '',
    proxy_http: '',
    proxy_https: '',
    username: '',
    password: '',
    _form: { name: '', proxy_http: '', proxy_https: '', username: '', password: '' },
  }
  displayList.value.unshift(newItem)
}

watch(
  () => props.visible,
  (val) => {
    if (val) loadData()
  }
)
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
  width: 800px;
  max-width: 90vw;
  max-height: 85vh;
  background: #fff;
  border-radius: 12px;
  overflow-y: auto;
  padding: 28px 32px;
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

.modal-title {
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 24px;
}

.config-section {
  margin-bottom: 28px;
}

.config-section-empty .empty-hint {
  color: #9ca3af;
  font-size: 13px;
  margin: 8px 0 0;
}

.section-label {
  font-size: 13px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 12px;
  padding-bottom: 6px;
  border-bottom: 1px solid #e5e7eb;
}

.proxy-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.proxy-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 6px;
  background: #f9fafb;
}

.proxy-row:hover {
  background: #f3f4f6;
}

.cell-name {
  width: 100px;
  font-size: 14px;
  color: #1f2937;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex-shrink: 0;
}

.cell-addr {
  flex: 1;
  min-width: 0;
  font-size: 13px;
  color: #6b7280;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: monospace;
}

.cell-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.btn-sm {
  height: 26px;
  padding: 0 10px;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s;
}

.btn-edit {
  background: #e5e7eb;
  color: #374151;
}

.btn-edit:hover {
  background: #d1d5db;
}

.btn-del {
  background: #fee2e2;
  color: #dc2626;
}

.btn-del:hover {
  background: #fecaca;
}

.btn-save {
  background: #3b82f6;
  color: #fff;
}

.btn-save:hover {
  background: #2563eb;
}

.btn-cancel {
  background: #e5e7eb;
  color: #374151;
}

.btn-cancel:hover {
  background: #d1d5db;
}

.cell-input {
  height: 28px;
  padding: 0 8px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 13px;
  outline: none;
  transition: border-color 0.15s;
}

.cell-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15);
}

.cell-input.name {
  width: 90px;
  flex-shrink: 0;
}

.cell-input.addr {
  flex: 1;
  min-width: 0;
}

.cell-input.user {
  width: 100px;
  flex-shrink: 0;
}

.cell-input.pass {
  width: 100px;
  flex-shrink: 0;
}

.btn-add {
  margin-top: 10px;
  height: 32px;
  padding: 0 14px;
  background: none;
  border: 1px dashed #d1d5db;
  border-radius: 6px;
  font-size: 13px;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-add:hover {
  border-color: #3b82f6;
  color: #3b82f6;
  background: #eff6ff;
}
</style>
