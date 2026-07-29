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
        <div role="image" aria-label={alt}>
          Image failed to load
        </div>
      ) : (
        <img
          alt={alt}
          className={classNames(
            className, // force formatting
            isLoaded ? 'loaded' : 'hidden',
          )}
          loading="lazy"
          onError={() => setHasError(true)}
          onLoad={() => setIsLoaded(true)}
          srcSet={`${src} 1x`}
          src={src}
        />
      )}
    </div>
  );
}
