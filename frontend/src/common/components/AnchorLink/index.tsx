import React from 'react';

import type { ReactAnchorProps } from '@/types/main';

type AnchorLinkProps = ReactAnchorProps & { href?: string };

export const AnchorLink = React.forwardRef<HTMLAnchorElement, AnchorLinkProps>(
  function AnchorLink({ children, href, ...props }, ref) {
    if (!href) {
      href = window.location.pathname;
    }

    return (
      <a href={href} ref={ref} {...props}>
        {children}
      </a>
    );
  },
);
