<template>
    <svg aria-hidden="true" class="svg-icon">
      <use :xlink:href="`#icon-${iconName}`" />
    </svg>
  </template>
  
  <script lang="ts">
  import { defineComponent } from 'vue';
  
  export default defineComponent({
    name: 'SvgIcon',
    props: {
      iconName: {
        type: String,
        required: true,
      },
    },
  });
  </script>
  
  <style scoped>
  .svg-icon {
    width: 1em;
    height: 1em;
    fill: currentColor;
  }
  </style>