import { createSystem, defaultConfig, defineConfig } from '@chakra-ui/react';

export const config = defineConfig({
  theme: {
    tokens: {
      colors: {},
    },
  },
});

export const stylingSystem = createSystem(defaultConfig, config);
