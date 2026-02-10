import resolve from '@rollup/plugin-node-resolve';
import typescript from '@rollup/plugin-typescript';
import { terser } from 'rollup-plugin-terser';

export default {
  input: 'src/smart-climate-card.ts',
  output: {
    file: 'dist/smart-climate-card.js',
    format: 'iife',
    name: 'SmartClimateCard',
    sourcemap: false,
  },
  plugins: [
    resolve({
      browser: true,
      dedupe: ['lit'],
    }),
    typescript({
      tsconfig: './tsconfig.json',
    }),
    terser({
      output: {
        comments: false,
      },
    }),
  ],
};
