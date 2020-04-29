<template>
  <div ref="select" class="mt-5">
    <client-only>
      <v-select
        ref="a"
        :options="series"
        :reduce="(serie) => serie.url"
        label="name"
        @input="selectChange"
      ></v-select>
    </client-only>
    <ul
      v-for="(value, key) in list"
      :key="key"
      class="py-3 text-md font-medium"
    >
      {{
        key
      }}
      <li
        v-for="(url, song) in value"
        :key="song"
        v-focus
        tabindex="0"
        class="flex justify-start cursor-pointer text-gray-700 hover:text-blue-400 hover:bg-blue-100 rounded-md px-2 py-2 my-2"
        @click="showPdf(url)"
      >
        <div class="flex-grow font-medium px-2" @click="showPdf(url)">
          {{ song }}
        </div>
      </li>
    </ul>
  </div>
</template>
<script>
import { mapState, mapActions } from 'vuex';

export default {
  name: 'Search',
  watchQuery(newQuery, oldQuery) {
    return newQuery.url;
  },
  data() {
    return { list: [] };
  },
  computed: { ...mapState(['series']) },
  mounted() {
    this.getSeries();
  },
  methods: {
    ...mapActions(['getSeries']),
    async selectChange(url) {
      this.pdfUrl = '';
      const games = await this.$axios.$get('/api/games', {
        params: {
          url,
        },
      });
      this.list = games;
    },
    showPdf(url) {
      this.$router.push({ path: 'sheet', query: { url } });
    },
  },
};
</script>
<style lang="scss">
@import 'vue-select/src/scss/vue-select.scss';
</style>
