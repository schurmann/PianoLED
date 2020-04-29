import Vue from 'vue';
import {
  SET_SERIES,
  SOCKET_ONOPEN,
  SOCKET_RECONNECT_ERROR,
  SOCKET_RECONNECT,
  SOCKET_ONMESSAGE,
  SOCKET_ONERROR,
  SOCKET_ONCLOSE,
} from './mutations-types';

export const state = () => ({
  socket: {
    isConnected: false,
    response: '',
    reconnectError: false,
  },
  series: [],
});

export const mutations = {
  [SOCKET_ONOPEN](state, event) {
    Vue.prototype.$socket = event.currentTarget;
    state.socket.isConnected = true;
  },
  [SOCKET_ONCLOSE](state, event) {
    state.socket.isConnected = false;
  },
  [SOCKET_ONERROR](state, event) {
    console.error(state, event);
  },
  // default handler called for all methods
  [SOCKET_ONMESSAGE](state, message) {
    state.socket.response = message;
  },
  // mutations for reconnect methods
  [SOCKET_RECONNECT](state, count) {
    console.info(state, count);
  },
  [SOCKET_RECONNECT_ERROR](state) {
    state.socket.reconnectError = true;
  },
  [SET_SERIES](state, series) {
    state.series = series;
  },
};

export const actions = {
  async getSeries({ commit, state }) {
    if (!state.series.length) {
      const resp = await this.$axios.$get('/ninsheet/ajax/allseries');
      commit(SET_SERIES, resp);
    }
  },
  send(context, message) {
    Vue.prototype.$socket.send(message);
  },
};
