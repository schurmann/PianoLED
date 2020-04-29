<template>
  <div class="flex justify-center">
    <client-only>
      <pdf
        :src="getPdf($route.query.url)"
        :page="page"
        @numpages="numberPages = $event"
        :scale="1"
      >
        <template slot="loading">
          loading content here...
        </template>
      </pdf>
    </client-only>
  </div>
</template>
<script>
import pdf from 'pdfvuer';
export default {
  layout: 'pdf',
  components: {
    pdf,
  },
  middleware({ route, redirect }) {
    if (!route.query.url) {
      return redirect('/search');
    }
  },
  data() {
    return {
      page: 1,
      numberPages: 1,
    };
  },
  mounted() {
    if (this.$route.query.page) {
      this.page = this.$route.query.page;
    }
    window.addEventListener('keydown', (event) => {
      if (event.key === ' ') {
        this.$router.push({ path: 'search' });
      } else if (event.key === 'ArrowLeft') {
        if (this.page === 1) {
          return;
        }
        this.page--;
      } else if (event.key === 'ArrowRight') {
        if (this.page === this.numberPages) {
          return;
        }
        this.page++;
      }
    });
  },
  methods: {
    getPdf(path) {
      return `/api/pdf?path=${path}`;
    },
  },
};
</script>
