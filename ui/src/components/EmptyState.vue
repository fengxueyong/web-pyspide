<template>
  <div class="empty-state">
    <div class="empty-icon" v-if="icon">
      <component :is="icon" />
    </div>
    <span class="empty-title">{{ title }}</span>
    <span v-if="sub" class="empty-sub">{{ sub }}</span>
  </div>
</template>

<script setup>
defineProps({
  icon: { type: [Object, Function], default: null },
  title: { type: String, default: '' },
  sub: { type: String, default: '' },
})
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 64px 16px;
  color: var(--muted-foreground);
}
.empty-icon {
  opacity: 0.3;
  margin-bottom: 4px;
  display: flex;
}
.empty-title {
  font-size: 14px;
}
.empty-sub {
  font-size: 12px;
  opacity: 0.6;
}
</style>
