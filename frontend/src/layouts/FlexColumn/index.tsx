import * as React from 'react';
import classNames from 'classnames';

import './styles.scss';

export type FlexColumnProps = React.PropsWithChildren<React.HTMLProps<HTMLDivElement>>;

export function FlexColumn({ children, className, ...props }: FlexColumnProps) {
  return (
    <div className={classNames('flex-column', className)} {...props}>
      {children}
    </div>
  );
}
