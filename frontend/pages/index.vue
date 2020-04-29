<template>
  <div>
    <div id="vexflow"></div>
    <div class="mt-64 flex items-center justify-center">
      <note class="text-6xl" :note="note" />
    </div>
  </div>
</template>
<script>
import { mapState, mapActions } from 'vuex';
import renderStaff from '~/utils/vexflow';
import Note from '~/components/Note';

export default {
  components: {
    Note,
  },
  data() {
    return {
      message: '',
    };
  },
  computed: {
    ...mapState('note', {
      note: (state) => state.data,
    }),
  },
  mounted() {
    const { system, vf, score } = renderStaff('vexflow');

    system
      .addStave({
        voices: [score.voice(score.notes('c#5/q, b4, a4, g#4'))],
      })
      .addClef('treble')
      .addTimeSignature('4/4');

    vf.draw();
  },
  methods: {
    ...mapActions(['send']),
  },
};
</script>
