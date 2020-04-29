import Vue from 'vue';
import { ADD_NODE } from '~/store/mutations-types';
Vue.directive('focus', {
  bind(el, binding, vnode) {
    console.log(el, binding, vnode);

    const store = vnode.context.$store;
    store.commit(`navigate/${ADD_NODE}`, el);
  },
});
