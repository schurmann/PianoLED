<template>
  <div class="bg-gray-100 font-sans w-full m-0">
    <div class="bg-white shadow">
      <div class="container mx-auto px-4">
        <div class="flex items-center py-4">
          <div>
            <nuxt-link
              to="/"
              class="text-gray-800 text-sm font-semibold hover:text-purple-600 mb-1"
            >
              <img src="~assets/guitar.svg" width="40" />
            </nuxt-link>
          </div>

          <div class="hidden sm:flex sm:items-center ml-5">
            <nuxt-link
              v-for="link in links"
              :key="link.href"
              :to="link.href"
              class="text-gray-800 text-sm font-semibold hover:text-purple-600 mr-4"
            >
              {{ link.name }}</nuxt-link
            >
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script lang="ts">
export default {
  props: {
    links: {
      type: Array,
      default() {
        return [];
      },
    },
  },
};
</script>
<style scoped lang="scss"></style>
