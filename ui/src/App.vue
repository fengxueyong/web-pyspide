<template>
  <div class="app-root">
    <PageHeader @crawl-started="onCrawlStarted" />
    <main class="main-content">
      <ResourceList ref="resourceListRef" />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import PageHeader from './components/PageHeader.vue'
import ResourceList from './components/ResourceList.vue'

const resourceListRef = ref(null)

function onCrawlStarted(website) {
  resourceListRef.value?.setWebsite(website)
  resourceListRef.value?.refreshWebsites()
}
</script>

<style scoped>
.app-root {
  min-height: 100vh;
  background: #f3f4f6;
}

.main-content {
  padding-bottom: 40px;
}
</style>
