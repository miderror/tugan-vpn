<template>
  <div class="stepper-container">
    <div v-for="(step, index) in steps" :key="index" class="stepper-item">
      <div
        :class="[
          'stepper-circle',
          { active: step.active, completed: step.completed },
        ]"
      >
        <SvgIcon
          v-if="step.completed"
          :iconName="'checkmark-icon'"
          class="stepper-icon"
        />
        <span v-else>{{ index + 1 }}</span>
      </div>
      <div
        v-if="index < steps.length - 1"
        class="stepper-divider"
      >
        <div
          :class="[
            'divider-line',
            { active: index + 1 === activeStep },
          ]"
          :style="{ height: dividerHeights[index] + 'px' }"
        ></div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import type { PropType } from 'vue';
import SvgIcon from './SvgIcon.vue';

export default defineComponent({
  name: 'Stepper',
  components: {
    SvgIcon,
  },
  props: {
    steps: {
      type: Array as PropType<{ active: boolean; completed: boolean }[]>,
      required: true,
    },
    dividerHeights: {
      type: Array as PropType<number[]>,
      required: true,
    },
    activeStep: {
      type: Number,
      required: true,
    },
  },
});
</script>

<style scoped>
.stepper-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stepper-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stepper-circle {
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #b9b9b9;
  color: #fff;
  font-weight: 500;
}

.stepper-circle.active {
  background-color: #121212;
}

.stepper-circle.completed {
  background-color: #b9b9b9;
}

.stepper-icon {
  width: 100%;
  height: 100%;
}

.stepper-divider {
  display: flex;
  justify-content: center;
  width: 2px;
  margin: 8px 0;
}

.divider-line {
  width: 2px;
  background: repeating-linear-gradient(
    to bottom,
    #b9b9b9,
    #b9b9b9 4px,
    transparent 4px,
    transparent 8px
  );
  transition: height 0.3s ease, background 0.3s ease;
}

.divider-line.active {
  background: repeating-linear-gradient(
    to bottom,
    #121212,
    #121212 4px,
    transparent 4px,
    transparent 8px
  );
}
</style>