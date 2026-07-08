import {
  createSystem,
  defaultConfig,
  defineConfig,
  defineRecipe,
  defineSlotRecipe,
} from '@chakra-ui/react';
import {
  cardAnatomy,
  checkboxAnatomy,
  progressAnatomy,
  radioGroupAnatomy,
  sliderAnatomy,
  switchAnatomy,
  tabsAnatomy,
} from '@chakra-ui/react/anatomy';
import * as muiColors from '@mui/material/colors';
import { createTheme } from '@mui/material/styles';

/**
 * For more on Themes, @see {@link https://mui.com/material-ui/customization/theming/ | Theming}
 */
export const muiTheme = createTheme({
  colorSchemes: {
    dark: true,
  },
  palette: {
    primary: {
      main: muiColors.blueGrey[500],
    },
    secondary: {
      main: muiColors.cyan[500],
    },
  },
});

export const config = defineConfig({
  globalCss: {
    html: {
      colorPalette: 'teal',
    },
  },
  theme: {
    recipes: {
      button: defineRecipe({ defaultVariants: { colorPalette: 'teal' } }),
    },
    slotRecipes: {
      card: defineSlotRecipe({
        slots: cardAnatomy.keys(),
        defaultVariants: {
          colorPalette: 'teal',
        },
      }),
      checkbox: defineSlotRecipe({
        slots: checkboxAnatomy.keys(),
        defaultVariants: {
          colorPalette: 'teal',
        },
      }),
      progress: defineSlotRecipe({
        slots: progressAnatomy.keys(),
        defaultVariants: {
          colorPalette: 'teal',
        },
      }),
      radioGroup: defineSlotRecipe({
        slots: radioGroupAnatomy.keys(),
        defaultVariants: {
          colorPalette: 'teal',
        },
      }),
      slider: defineSlotRecipe({
        slots: sliderAnatomy.keys(),
        defaultVariants: {
          colorPalette: 'teal',
        },
      }),
      switch: defineSlotRecipe({
        slots: switchAnatomy.keys(),
        defaultVariants: {
          colorPalette: 'teal',
        },
      }),
      tabs: defineSlotRecipe({
        slots: tabsAnatomy.keys(),
        defaultVariants: {
          colorPalette: 'teal',
        },
      }),
    },
  },
});

export const stylingSystem = createSystem(defaultConfig, config);
