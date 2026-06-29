import { createBrowserRouter, redirect, type RouteObject } from 'react-router';

import { Root } from '@/layouts';
import { Home } from '@/pages';

export const navItemsLabels = {
  HOME: 'Home',
  MARKETS: 'Markets',
  LISTINGS: 'Listings',
  // ACCOUNT: 'Account',
};

/**
 * @note possibilities for implementing protected/public routes
 * - https://github.com/remix-run/react-router/issues/10637#issuecomment-1802180978
 * - https://medium.com/@umaishassan/private-protected-and-public-routes-in-react-router-v6-e8fb623aa81
 */
export const routerConfig: RouteObject[] = [
  {
    path: '/',
    element: <Root />,
    HydrateFallback: () => null,
    loader: async ({ request }) => {
      if (window != null && window.location?.pathname === '/') {
        const homeUrl = new URL(request.url);
        homeUrl.pathname = '/home';

        return window.location.assign(homeUrl.toString());
      }
      return;
    },
    children: [
      {
        path: 'home',
        // @ts-expect-error: I hope this is just temporarily missing
        label: navItemsLabels.HOME,
        element: <Home />,
      },
    ],
  },
];

const browserRouter = createBrowserRouter(routerConfig);

export default browserRouter;
