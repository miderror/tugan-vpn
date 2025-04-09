<template>
  <div class="referral-link-section">
    <label for="referralLink" class="referral-link-label">Ваша реферальная ссылка</label>
    <div class="referral-link-input">
      <input
        type="text"
        id="referralLink"
        class="referral-link-text"
        :value="referralLink"
        readonly
      />
      <button @click="shareLink" class="action-button">
        <SvgIcon :iconName="'share-icon'" class="action-icon" />
      </button>
      <button @click="copyLink" class="action-button">
        <SvgIcon :iconName="'copy-icon'" class="action-icon" />
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { useTwaSdk } from '@/composables/useTwaSdk';
import { useNotification } from '@/composables/useNotification';
import SvgIcon from '@/components/SvgIcon.vue';

export default defineComponent({
  name: 'ReferralLink',
  components: {
    SvgIcon,
  },
  props: {
    referralLink: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const { copyToClipboard, shareMessage, hapticFeedback } = useTwaSdk();
    const { notify } = useNotification();

    const copyLink = () => {
      hapticFeedback('success');
      copyToClipboard(props.referralLink);
      notify({ message: 'Скопировано', type: 'info' });
    };

    const shareLink = () => {
      hapticFeedback('success');
      shareMessage(props.referralLink);
    };

    return { copyLink, shareLink };
  },
});
</script>

<style scoped>
.referral-link-label {
  color: #121212;
  font-weight: 500;
  margin-bottom: 8px;
  display: block;
}

.referral-link-input {
  display: flex;
  align-items: center;
  background-color: #fff;
  border: 1px solid #eaeaea;
  border-radius: 6px;
  padding: 8px 12px;
}

.referral-link-text {
  flex: 1;
  border: none;
  outline: none;
  background: none;
  color: #979aa0;
}

.action-button {
  background: none;
  border: none;
  padding: 0;
  margin-left: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-icon {
  width: 24px;
  height: 24px;
  color: #898989;
}
</style>