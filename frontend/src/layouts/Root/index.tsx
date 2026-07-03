import { Outlet } from 'react-router';

import { TopNavBar } from '@/common/components';
import { FlexColumn } from '@/layouts';

import './styles.scss';

export function Root() {
  return (
    <div id="root-layout">
      <TopNavBar />

      <FlexColumn className="card">
        <Outlet />
      </FlexColumn>
    </div>
  );
}
