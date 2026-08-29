import { Outlet } from 'react-router';

import { TopNavBar } from '@/common/components';
import { FlexColumn } from '@/layouts';
import { CurrencyProvider } from '@/providers';

import './styles.scss';

/**
 * @note `CurrencyProvider` is mounted here rather than in `main.tsx` so that the
 * currency toggle in `TopNavBar` and every page under `Outlet` share one
 * preference, and so router-based tests get the context without each having to
 * wrap it themselves.
 */
export function Root() {
  return (
    <CurrencyProvider>
      <div id="root-layout">
        <TopNavBar />

        <FlexColumn className="card">
          <Outlet />
        </FlexColumn>
      </div>
    </CurrencyProvider>
  );
}
