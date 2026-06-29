import { Link } from 'react-router';

import { useAppStore } from '@/store';
import { navItemsLabels, routerConfig } from '@/app/browserRouter';

export function TopNavBar() {
  const { appState } = useAppStore();

  const labelsValues = Object.values(navItemsLabels);

  return (
    <nav className="top-nav-bar">
      <ul>
        {routerConfig[0].children?.map((config) => {
          if (
            typeof config.path !== 'string' ||
            // @ts-expect-error: I hope this is just temporarily missing
            !labelsValues.includes(config.label)
          ) {
            return null;
          }

          return (
            <li key={`top-nav-bar-item-${config.path}`}>
              <Link to={config.path}>
                {/* @ts-expect-error: I hope this is just temporarily missing */}
                {config.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
