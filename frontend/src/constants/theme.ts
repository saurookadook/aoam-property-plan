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
