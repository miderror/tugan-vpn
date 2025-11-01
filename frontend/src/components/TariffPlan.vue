<template>
  <div
    :class="['plan-card', { selected: isSelected, bestseller: isBestseller }]"
    @click="selectPlan"
  >
    <div class="plan-details">
      <div class="plan-duration">{{ duration }}</div>
      <div class="plan-price">{{ pricePerDay }}₽ / день</div>
      <div class="plan-total-wrapper">
        <div class="plan-total">Общая сумма {{ total }}₽</div>
        <div v-if="originalPrice" class="original-price">
          {{ originalPrice }}₽
          <SvgIcon :iconName="'strike-line'" class="strike-line" />
        </div>
      </div>
    </div>
    <SvgIcon
      :iconName="isSelected ? 'tariff-selected-icon' : 'tariff-unselected-icon'"
      class="selection-icon"
    />
    <div v-if="isBestseller" class="bestseller-badge">Бестселлер</div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import SvgIcon from "./SvgIcon.vue";

export default defineComponent({
  name: "TariffPlan",
  components: {
    SvgIcon,
  },
  props: {
    duration: {
      type: String,
      required: true,
    },
    pricePerDay: {
      type: Number,
      required: true,
    },
    total: {
      type: Number,
      required: true,
    },
    originalPrice: {
      type: Number,
      default: undefined,
    },
    isBestseller: {
      type: Boolean,
      default: false,
    },
    isSelected: {
      type: Boolean,
      default: false,
    },
  },
  emits: ["select-plan"],
  methods: {
    selectPlan() {
      this.$emit("select-plan");
    },
  },
});
</script>

<style scoped>
.plan-card {
  border-radius: 12px;
  background-color: #fff;
  display: flex;
  margin-top: 16px;
  min-height: 80px;
  align-items: center;
  gap: 16px;
  overflow: visible;
  line-height: 1.2;
  padding: 12px 16px;
  border: 1px solid #eaeaea;
  cursor: pointer;
  position: relative;
}

.plan-card.selected {
  border: 2px solid #121212;
}

.plan-details {
  display: flex;
  min-width: 240px;
  flex-direction: column;
  justify-content: center;
  flex: 1;
}

.plan-duration {
  font-size: 14px;
  font-weight: 600;
}

.plan-price {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
  font-style: normal;
  font-weight: 600;
  font-size: 20px;
  margin-top: 4px;
  line-height: 20px;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.plan-total {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
  font-style: normal;
  font-weight: 600;
  font-size: 14px;
  color: #8d8c8f;
  margin-top: 4px;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.plan-total-wrapper {
  display: flex;
  align-items: center;
  margin-top: 4px;
  position: relative;
}

.original-price {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
  font-style: normal;
  color: #ff0000;
  font-weight: 400;
  font-size: 10px;
  position: relative;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.strike-line {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  pointer-events: none;
}

.selection-icon {
  width: 24px;
  height: 24px;
  color: #8d8c8f;
  align-self: flex-start;
  padding-top: 4px;
}

.bestseller-badge {
  position: absolute;
  top: 0px;
  right: 16px;
  border-radius: 39px;
  background-color: #2d5009;
  font-size: 12px;
  color: #fff;
  font-weight: 500;
  white-space: nowrap;
  padding: 6px 8px;
  z-index: 1;
  transform: translateY(-50%);
}
</style>
