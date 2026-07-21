import { useState } from 'react';
import classNames from 'classnames';
import { Skeleton } from '@mui/material';

import './styles.scss';

export function SmartImage({
  alt,
  className,
  src,
}: {
  alt: string;
  className?: string;
  src: string;
}) {
  const [isLoaded, setIsLoaded] = useState<boolean>(false);
  const [hasError, setHasError] = useState<boolean>(false);

  return (
    <div className="smart-image">
      {!isLoaded && !hasError && <Skeleton variant="rectangular" />}

      {hasError ? (
        <div>ERROR</div>
      ) : (
        <img
          alt={alt}
          className={classNames(
            className, // force formatting
            isLoaded ? 'loaded' : 'hidden',
          )}
          loading="lazy"
          onError={() => setTimeout(() => setHasError(true), 5000)}
          onLoad={() => setIsLoaded(true)}
          srcSet={src}
          src={src}
        />
      )}
    </div>
  );
}
