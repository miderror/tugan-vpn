<template>
  <div class="referral-user-card">
    <div class="user-info">
      <div class="avatar-container">
        <SvgIcon
            v-if="!imageLoaded"
            :iconName="'user-default-icon'"
            class="user-default-icon"
        />
        <img
            v-show="avatarUrl && imageLoaded"
            :src="avatarUrl"
            alt="User avatar"
            class="user-avatar"
            @load="handleImageLoad"
        />
      </div>
      <div class="username">{{ user.username }}</div>
    </div>
    <div class="bonus-text">+100₽</div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import SvgIcon from './SvgIcon.vue';

export default defineComponent({
  name: 'ReferralUser',
  components: {
    SvgIcon,
  },
  props: {
    user: {
      type: Object,
      required: true,
    },
  },
  setup(props) {
    const imageLoaded = ref(false);
    const avatarUrl = ref('');

    onMounted(async () => {
      if (typeof props.user.avatar === 'function') {
        const url = await props.user.avatar();
        if (url) {
          avatarUrl.value = url;
        }
      }
    });

    const handleImageLoad = () => {
      imageLoaded.value = true;
    };

    return {
      imageLoaded,
      avatarUrl,
      handleImageLoad,
    };
  },
});
</script>

<style scoped>
.referral-user-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.user-info {
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 0;
}

.avatar-container {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 8px;
  flex-shrink: 0;
  background-color: #c1c1c1;
}

.user-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-default-icon {
  width: 50%;
  height: 50%;
  padding: 25%;
  object-fit: cover;
  color: white;
}

.username {
  color: #121212;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
  min-width: 0;
}

.bonus-text {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-style: normal;
  color: #121212;
  font-weight: 600;
  font-size: 16px;
  flex-shrink: 0;
  margin-left: 8px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>