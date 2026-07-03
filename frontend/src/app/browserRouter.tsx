import {
  createBrowserRouter,
  redirect,
  type LoaderFunctionArgs,
  type RouteObject,
} from 'react-router';
import { QueryClient } from '@tanstack/react-query';

import { Root } from '@/layouts';
import { Home, MarketsList } from '@/pages';

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
  (_queryClient: QueryClient) =>
  async ({ request }: LoaderFunctionArgs) => {
    const url = new URL(request.url);
    if (url.pathname === '/') {
      url.pathname = '/home';
      return redirect(url.toString());
    }

    return null;
  };

export type AOAMRouteObject = RouteObject & {
  children?: AOAMRouteObject[];
  label?: string;
};

/**
 * @note possibilities for implementing protected/public routes
 * - https://github.com/remix-run/react-router/issues/10637#issuecomment-1802180978
 * - https://medium.com/@umaishassan/private-protected-and-public-routes-in-react-router-v6-e8fb623aa81
 */
export const routerConfig: AOAMRouteObject[] = [
  {
    path: '/',
    element: <Root />,
    HydrateFallback: () => null,
    loader: rootLoader(queryClient),
    children: [
      {
        path: 'home',
        label: navItemsLabels.HOME,
        element: <Home />,
      },
      {
        path: 'markets',
        label: navItemsLabels.MARKETS,
        element: <MarketsList />,
      },
    ],
  },
];

const browserRouter = createBrowserRouter(routerConfig);

export default browserRouter;
