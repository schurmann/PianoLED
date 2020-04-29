import { ON_NOTE } from './mutations-types';
export const state = () => ({
  data: '',
});

export const mutations = {
  [ON_NOTE](state, response) {
    state.data = response.data;
  },
};

export const actions = {
  onNote({ commit, state }, response) {
    commit(ON_NOTE, response);
  },
};
