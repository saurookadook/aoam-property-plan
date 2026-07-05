import { useMemo } from 'react';
import { Link as RouterLink } from 'react-router';
import { MenuIcon, X as X_Icon } from 'lucide-react';
import { Box, Drawer, useDisclosure } from '@chakra-ui/react';

import {
  navItemsLabels,
  routerConfig,
  type AOAMRouteObject,
} from '@/app/browserRouter';

import './styles.scss'

export function NavDrawer() {
  const { open: isOpen, onOpen, onClose } = useDisclosure();

  const labelsValues = Object.values(navItemsLabels);
  const navItems = useMemo(() => {
    return (
      routerConfig[0].children?.filter((config) =>
        shouldRenderNavItem(config, labelsValues),
      ) ?? []
    );
  }, [labelsValues]);

  return (
    <Drawer.Root // force formatting
      open={isOpen}
      placement="start"
      size="md"
    >
      <Drawer.Backdrop />
      <Drawer.Trigger aria-label="Main navigation button" onClick={onOpen}>
        <MenuIcon />
      </Drawer.Trigger>
      <Drawer.Positioner>
        <Drawer.Content>
          <Drawer.CloseTrigger onClick={onClose}>
            <X_Icon />
          </Drawer.CloseTrigger>

          <Drawer.Header>
            <Drawer.Title>{`💸 🤑 💸 Main Navigation 💸 🤑 💸`}</Drawer.Title>
          </Drawer.Header>

          <Drawer.Body>
            <Box
              as="nav" // force formatting
              className="nav-drawer__nav"
              display="flex"
            >
              <ul>
                {navItems.map((config) => {
                  return (
                    <li key={`nav-drawer-item-${config.path}`}>
                      <RouterLink to={config.path as string}>{config.label}</RouterLink>
                    </li>
                  );
                })}
              </ul>
            </Box>
          </Drawer.Body>
        </Drawer.Content>
      </Drawer.Positioner>
    </Drawer.Root>
  );
}

function shouldRenderNavItem(
  config: AOAMRouteObject,
  labelsValues: string[],
): config is AOAMRouteObject {
  return (
    typeof config.path === 'string' &&
    'label' in config &&
    typeof config.label === 'string' &&
    labelsValues.includes(config.label)
  );
}
