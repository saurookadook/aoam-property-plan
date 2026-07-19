import classNames from 'classnames';
import DOMPurify from 'dompurify';
import { Card, CardContent, Typography } from '@mui/material';

import { isNonEmptyString } from '@/common/utils';
import './styles.scss';

export function ListingDescriptionCard({
  className,
  description,
  ...props
}: {
  className?: string;
  description?: string;
}) {
  return (
    <Card
      className={classNames('listing-overview-data__data-item', className)}
      {...props}
    >
      <CardContent>
        <Typography
          className="listing-overview-data__data-item__details-wrapper"
          variant="body2"
        >
          <Typography
            className="listing-overview-data__data-item__description"
            component="span"
            dangerouslySetInnerHTML={{
              __html: isNonEmptyString(description)
                ? DOMPurify.sanitize(description)
                : 'No description 🤷‍♂️',
            }}
          />
        </Typography>
      </CardContent>
    </Card>
  );
}
