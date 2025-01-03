<template>
  <div class="stats-box">
    <div class="stats-label">{{ label }}</div>
    <div class="stats-value">{{ value }}</div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'StatsBox',
  props: {
    label: {
      type: String,
      required: true,
    },
    value: {
      type: [String, Number],
      required: true,
    },
  },
});
</script>

<style scoped>
.stats-box {
  border-radius: 12px;
  background-color: rgb(255, 255, 255);
  flex: 1;
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  justify-content: space-between;
  text-align: left;
  min-width: 0;
  height: 100%;
}

.stats-label {
  color: rgb(18, 18, 18);
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: pre-line;
}

.stats-value {
  color: rgb(141, 140, 143);
  font-weight: 400;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>