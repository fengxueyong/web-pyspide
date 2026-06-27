<template>
  <div class="thumb-grid-wrapper">
    <div class="thumb-grid">
      <ThumbnailCard v-for="r in items" :key="r.id || r.res_link || r.url" :resource="r" />
    </div>
    <ScrollAnchor :has-more="hasMore" @load-more="$emit('load-more')" />
  </div>
</template>

<script setup>
import ThumbnailCard from './ThumbnailCard.vue'
import ScrollAnchor from './ScrollAnchor.vue'

defineProps({
  items: { type: Array, default: () => [] },
  hasMore: { type: Boolean, default: false },
})

defineEmits(['load-more'])
</script>

<style scoped>
.thumb-grid-wrapper {
  display: flex;
  flex-direction: column;
}
.thumb-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
</style>
