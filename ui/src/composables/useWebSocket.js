import { ref, onUnmounted } from 'vue'

export function useWebSocket() {
  let ws = null
  const connected = ref(false)
  const messages = ref([])

  function connect(taskId) {
    if (ws) disconnect()
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = location.host
    ws = new WebSocket(`${protocol}//${host}/api/crawl/ws/${taskId}`)

    ws.onopen = () => {
      connected.value = true
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        messages.value.push(data)
      } catch {
        messages.value.push({ text: event.data })
      }
    }

    ws.onclose = () => {
      connected.value = false
      ws = null
    }

    ws.onerror = () => {
      connected.value = false
    }
  }

  function disconnect() {
    if (ws) {
      ws.close()
      ws = null
    }
    connected.value = false
  }

  onUnmounted(() => {
    disconnect()
  })

  return { connected, messages, connect, disconnect }
}
