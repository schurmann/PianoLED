<template>
  <p>
    {{ note }}
  </p>
</template>
<script>
export default {
  name: 'Note',
  props: {
    note: {
      type: String,
      required: true,
    },
  },
};
</script>
<style lang="scss"></style>
