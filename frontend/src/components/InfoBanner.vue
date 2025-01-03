<template>
  <div class="info-banner">
    <SvgIcon :iconName="'info-icon'" class="info-icon" />
    <p class="info-text">
      {{ text }}
    </p>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import SvgIcon from './SvgIcon.vue';

export default defineComponent({
  name: 'InfoBanner',
  components: {
    SvgIcon,
  },
  props: {
    text: {
      type: String,
      required: true,
    },
  },
});
</script>

<style scoped>
.info-banner {
  border-radius: 12px;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px;
  border: 1px solid #c1c1c1;
  margin-top: 40px;
}

.info-icon {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
  color: #c1c1c1;
}

.info-text {
  color: #898989;
  font-size: 15px;
  line-height: 18px;
  margin: 0;
  flex: 1;
}
</style>