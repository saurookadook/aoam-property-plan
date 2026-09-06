import {
  createBrowserRouter,
  redirect,
  type LoaderFunctionArgs,
  type RouteObject,
} from 'react-router';
import { QueryClient } from '@tanstack/react-query';

import { Root } from '@/layouts';
import {
  Home,
  ListingOverview,
  MarketOverview,
  MarketsList,
  PropertiesList,
  PropertyCreate,
  PropertyOverview,
  listingOverviewLoader,
  marketOverviewLoader,
  marketsListLoader,
  propertiesListLoader,
  propertyOverviewLoader,
} from '@/pages';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 15, // 15 minutes
    },
  },
});

export const navItemsLabels = {
  HOME: '🏡 Home',
  MARKETS: '💰 Markets',
  PROPERTIES: '🏠 Properties',
  LISTINGS: 'Listings',
  LISTINGS_FINANCIAL_REPORTS: '📈 Listings Financial Reports 📈',
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
        loader: marketsListLoader(queryClient),
      },
      {
        path: 'markets/:marketId',
        element: <MarketOverview />,
        loader: marketOverviewLoader(queryClient),
      },
      {
        path: 'listings/:listingId',
        element: <ListingOverview />,
        loader: listingOverviewLoader(queryClient),
      },
      {
        path: 'properties',
        label: navItemsLabels.PROPERTIES,
        element: <PropertiesList />,
        loader: propertiesListLoader(queryClient),
      },
      {
        path: 'properties/new',
        element: <PropertyCreate />,
      },
      {
        path: 'properties/:propertyId',
        element: <PropertyOverview />,
        loader: propertyOverviewLoader(queryClient),
      },
    ],
  },
];

const browserRouter = createBrowserRouter(routerConfig);

export default browserRouter;
