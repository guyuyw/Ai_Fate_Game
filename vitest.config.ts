import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    include: ['packages/engine/tests/**/*.test.ts'],
    environment: 'node',
    coverage: {
      provider: 'v8',
      include: ['packages/engine/src/**/*.ts'],
      exclude: ['packages/engine/src/index.ts'],
      reporter: ['text', 'json-summary']
    }
  }
});
