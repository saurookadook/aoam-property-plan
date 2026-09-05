import React from 'react';

import { AnchorLink, type AnchorLinkProps } from '@/common/components/AnchorLink';

export type ExternalLinkProps = Omit<AnchorLinkProps, 'href'> & { href: string };

export const ExternalLink = React.forwardRef<HTMLAnchorElement, ExternalLinkProps>(
  function ExternalLink({ children, ...props }, ref) {
    return (
      <AnchorLink ref={ref} target="_blank" rel="noopener noreferrer" {...props}>
        {children}
      </AnchorLink>
    );
  },
);
