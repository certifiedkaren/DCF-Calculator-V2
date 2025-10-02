<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div>
    <nav class="text-white">
      <RouterLink to="/">DCF</RouterLink> |
      <RouterLink to="/earnings">Earnings</RouterLink>
    </nav>

    <RouterView />
  </div>
</template>
