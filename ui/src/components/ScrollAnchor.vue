<template>
  <div ref="anchorRef" class="scroll-anchor">
    <span v-if="hasMore" class="load-more">加载更多...</span>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'

const props = defineProps({
  hasMore: { type: Boolean, default: false },
})

const emit = defineEmits(['load-more'])

const anchorRef = ref(null)
let observer = null

function setupObserver() {
  if (observer) observer.disconnect()
  observer = new IntersectionObserver(
    (entries) => {
      if (entries[0]?.isIntersecting && props.hasMore) {
        emit('load-more')
      }
    },
    { threshold: 0.1 }
  )
  nextTick(() => {
    if (anchorRef.value) observer.observe(anchorRef.value)
  })
}

watch(() => props.hasMore, () => {
  nextTick(() => {
    if (observer && anchorRef.value) {
      observer.unobserve(anchorRef.value)
      observer.observe(anchorRef.value)
    }
  })
})

onMounted(setupObserver)
onUnmounted(() => { if (observer) observer.disconnect() })
</script>

<style scoped>
.scroll-anchor {
  padding: 16px 0;
  text-align: center;
}
.load-more {
  font-size: 12px;
  color: var(--muted-foreground);
  animation: pulse-text 1.5s infinite;
}
@keyframes pulse-text {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 1; }
}
</style>
