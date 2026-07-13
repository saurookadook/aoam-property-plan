import { colors as muiColors, createTheme } from '@mui/material';

/**
 * For more on Themes, @see {@link https://mui.com/material-ui/customization/theming/ | MUI Theming}
 */
export const muiTheme = createTheme({
  cssVariables: {
    colorSchemeSelector: 'class',
  },
  colorSchemes: {
    light: true,
    dark: true,
  },
  palette: {
    mode: 'dark',
    primary: {
      light: muiColors.cyan[100],
      main: muiColors.cyan[300],
      dark: muiColors.cyan[500],
    },
    secondary: {
      light: muiColors.cyan[500],
      main: muiColors.cyan[700],
      dark: muiColors.cyan[900],
    },
  },
});
