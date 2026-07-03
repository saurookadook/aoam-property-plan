import { Link } from 'react-router';

import { useAppStore } from '@/store';
import {
  navItemsLabels,
  routerConfig,
  type AOAMRouteObject,
} from '@/app/browserRouter';

export function TopNavBar() {
  const { appState } = useAppStore();

  const labelsValues = Object.values(navItemsLabels);

  return (
    <nav className="top-nav-bar">
      <ul>
        {routerConfig[0].children?.map((config) => {
          if (shouldRenderNavItem(config, labelsValues)) {
            return (
              <li key={`top-nav-bar-item-${config.path}`}>
                <Link to={config.path as string}>{config.label}</Link>
              </li>
            );
          }

          return null;
        })}
      </ul>
    </nav>
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
