import Vex from '~/plugins/vexflow.client';
export default (id) => {
  const vf = new Vex.Flow.Factory({
    renderer: {
      elementId: id,
      width: 500,
      height: 200,
    },
  });

  const score = vf.EasyScore();
  const system = vf.System();

  return { system, vf, score };
};
