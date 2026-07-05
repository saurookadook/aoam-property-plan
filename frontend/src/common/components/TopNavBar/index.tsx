import { Link as RouterLink } from 'react-router';
import { SunIcon, MoonIcon } from 'lucide-react';
import { useTheme } from 'next-themes';
import { Button, Heading, Spacer } from '@chakra-ui/react';

import { FlexRow } from '@/layouts';
import { useAppStore } from '@/store';
import { NavDrawer } from '../NavDrawer';

import './styles.scss';

export function TopNavBar() {
  const { appState } = useAppStore();
  const { theme, setTheme } = useTheme();

  return (
    <nav className="top-nav-bar">
      <FlexRow className="top-nav-bar__inner-wrapper">
        <NavDrawer />

        <RouterLink to="/">
          <Heading>{`💸 AOAM Property Plan 💸`}</Heading>
        </RouterLink>

        <Spacer />

        <Button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
          {theme === 'light' ? <SunIcon /> : <MoonIcon />}
        </Button>
      </FlexRow>
    </nav>
  );
}
