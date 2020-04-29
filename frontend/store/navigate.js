import {
  PUSH_ROUTE,
  ADD_NODE,
  NEXT_NODE,
  PREVIOUS_NODE,
  CLICK_NODE,
} from './mutations-types';

const FOCUS_CLASS = 'bg-blue-100';
const removeFocusFromNode = (el) => {
  if (el !== undefined) el.classList.remove(FOCUS_CLASS);
};

const focusNode = (el) => {
  if (el !== undefined) {
    el.classList.add(FOCUS_CLASS);
    el.focus();
  }
};

const updateNodeIndex = (type, index, length) => {
  if (type === 'INC') {
    index++;
    if (index === length) {
      index = 0;
    }
  } else if (type === 'DEC') {
    index--;
    if (index === -1) {
      index = length - 1;
    }
  }
  return index;
};

export const state = () => ({
  nodes: [],
  currentNodeIndex: 0,
  previousNodeIndex: undefined,
  data: '',
});

export const mutations = {
  [ADD_NODE](state, node) {
    state.nodes.push(node);
  },
  [PREVIOUS_NODE](state) {
    removeFocusFromNode(state.nodes[state.previousNodeIndex]);
    focusNode(state.nodes[state.currentNodeIndex]);
    state.previousNodeIndex = state.currentNodeIndex;
    state.currentNodeIndex = updateNodeIndex(
      'DEC',
      state.currentNodeIndex,
      state.nodes.length
    );
  },
  [NEXT_NODE](state) {
    removeFocusFromNode(state.nodes[state.previousNodeIndex]);
    focusNode(state.nodes[state.currentNodeIndex]);
    state.previousNodeIndex = state.currentNodeIndex;
    state.currentNodeIndex = updateNodeIndex(
      'INC',
      state.currentNodeIndex,
      state.nodes.length
    );
  },
  [CLICK_NODE](state) {
    state.nodes[state.currentNodeIndex].dispatchEvent(new MouseEvent('click'));
  },
  [PUSH_ROUTE](state, { route }) {
    console.log(this.$router.push(route));
  },
};

export const actions = {
  onNavigate({ commit }, { data }) {
    commit(data.mutation, data.data);
  },
  onNextTab(_, message) {
    console.log(message);
  },
};
