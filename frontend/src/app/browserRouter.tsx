import {
  createBrowserRouter,
  redirect,
  type LoaderFunctionArgs,
  type RouteObject,
} from 'react-router';
import { QueryClient } from '@tanstack/react-query';

import { Root } from '@/layouts';
import { Home } from '@/pages';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 10, // 10 seconds
    },
  },
});

export const navItemsLabels = {
  HOME: 'Home',
  MARKETS: 'Markets',
  LISTINGS: 'Listings',
  // ACCOUNT: 'Account',
};

export const rootLoader =
  (queryClient: QueryClient) =>
  async ({ request }: LoaderFunctionArgs) => {
    if (window != null && window.location?.pathname === '/') {
      const homeUrl = new URL(request.url);
      homeUrl.pathname = '/home';

      window.location.assign(homeUrl.toString());
      return;
    }

    return;
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
    loader: rootLoader(queryClient),
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
