import React, { useCallback, useMemo } from 'react';
import { Link as RouterLink } from 'react-router';
import { X as X_Icon } from 'lucide-react';
import { Box, Drawer, List, ListItem, ListItemText, Typography } from '@mui/material';

import {
  navItemsLabels,
  routerConfig,
  type AOAMRouteObject,
} from '@/app/browserRouter';

import './styles.scss';

export function NavDrawer({
  isOpen,
  setIsOpen,
}: {
  isOpen: boolean;
  setIsOpen: React.Dispatch<React.SetStateAction<boolean>>;
}) {
  const labelsValues = Object.values(navItemsLabels);
  const navItems = useMemo(() => {
    return (
      routerConfig[0].children?.filter((config) =>
        shouldRenderNavItem(config, labelsValues),
      ) ?? []
    );
  }, [labelsValues]);

  const handleClose = useCallback(() => {
    return setIsOpen(false);
  }, []);

  return (
    <Drawer
      className="nav-drawer"
      onClose={handleClose}
      open={isOpen}
      variant="temporary"
    >
      <Box role="presentation" onClick={handleClose}>
        <Typography
          className="nav-drawer__title"
          variant="h2"
        >{`💸 🤑 💸 Main Navigation 💸 🤑 💸`}</Typography>
        <List>
          {navItems.map((config) => {
            return (
              <ListItem key={`nav-drawer-item-${config.path}`}>
                <ListItemText>
                  <RouterLink to={config.path as string}>{config.label}</RouterLink>
                </ListItemText>
              </ListItem>
            );
          })}
        </List>
      </Box>
    </Drawer>
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
