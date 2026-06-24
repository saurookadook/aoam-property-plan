import * as React from 'react';
import classNames from 'classnames';

import type { ReactDivProps } from '@/types/main';

import './styles.scss';

export const LoadingState = React.forwardRef<HTMLDivElement, ReactDivProps>(
  function LoadingState(
    {
      children, // force formatting
      className,
      ...props
    },
    ref,
  ) {
    return (
      <div
        aria-label={props['aria-label'] ?? 'Loading...'}
        className={classNames('loading-spinner', className)} // force formatting
        ref={ref}
        {...props}
      >
        {children}
      </div>
    );
  },
);
