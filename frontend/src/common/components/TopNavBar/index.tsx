import { useState } from 'react';
import { Link as RouterLink } from 'react-router';
import { MenuIcon, SunIcon, MoonIcon } from 'lucide-react';
import { Box, Button, Typography, useColorScheme } from '@mui/material';

import { FlexRow, FlexSpacer } from '@/layouts';
import { useAppStore } from '@/store';
import { NavDrawer } from '../NavDrawer';

import './styles.scss';

export function TopNavBar() {
  const { appState } = useAppStore();
  const { mode, setMode } = useColorScheme();
  const [isNavDrawerOpen, setIsNavDrawerOpen] = useState(false);

  return (
    mode != null && (
      <Box component="nav" id="top-nav" className="top-nav-bar">
        <FlexRow className="top-nav-bar__inner-wrapper">
          <Button
            onClick={() => {
              setIsNavDrawerOpen(true);
            }}
          >
            <MenuIcon />
          </Button>

          <NavDrawer isOpen={isNavDrawerOpen} setIsOpen={setIsNavDrawerOpen} />

          <RouterLink to="/">
            <Typography
              className="top-nav-bar__title"
              variant="h1"
            >{`💸 AOAM Property Plan 💸`}</Typography>
          </RouterLink>

          <FlexSpacer />

          <Button
            onClick={() => {
              setMode(mode === 'light' ? 'dark' : 'light');
            }}
          >
            {mode === 'light' ? <SunIcon /> : <MoonIcon />}
          </Button>
        </FlexRow>
      </Box>
    )
  );
}
