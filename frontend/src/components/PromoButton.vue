<template>
  <button class="promo-btn" tabindex="0">
    <SvgIcon :iconName="iconName" class="action-icon" />
    <span>{{ text }}</span>
  </button>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import SvgIcon from './SvgIcon.vue';

export default defineComponent({
  name: 'PromoButton',
  components: {
    SvgIcon,
  },
  props: {
    iconName: {
      type: String,
      required: true,
    },
    altText: {
      type: String,
      required: true,
    },
    text: {
      type: String,
      required: true,
    },
  },
});
</script>

<style scoped>
.promo-btn {
  border-radius: 12px;
  background-color: rgb(45, 80, 9);
  box-shadow: 0 4px 4px rgba(0, 0, 0, 0.25);
  display: flex;
  width: 100%;
  align-items: center;
  gap: 8px;
  justify-content: center;
  padding: 16px 24px;
  border: none;
  color: rgb(255, 255, 255);
  font-size: 16px;
  font-weight: 600;
  text-transform: uppercase;
  cursor: pointer;
}

.promo-btn:hover {
  opacity: 0.9;
}

.promo-btn:focus {
  outline: 2px solid rgb(255, 255, 255);
  outline-offset: 2px;
}
</style>