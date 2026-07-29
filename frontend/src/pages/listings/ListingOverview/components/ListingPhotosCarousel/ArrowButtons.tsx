import type { ComponentPropsWithRef } from 'react';
import classNames from 'classnames';
import { Button } from '@mui/material';
import { CircleChevronLeft, CircleChevronRight } from 'lucide-react';

type ArrowButtonProps = ComponentPropsWithRef<typeof Button> & {
  children?: React.ReactNode;
  className?: string;
  disabled?: boolean;
};

export const PrevButton = ({
  children,
  className,
  disabled,
  ...props
}: ArrowButtonProps) => {
  return (
    <Button
      {...props}
      className={classNames(
        'embla__prev',
        className,
        disabled && 'embla__button--disabled',
      )}
      disabled={disabled}
      type="button"
      aria-label="Scroll to previous"
    >
      <CircleChevronLeft />
      {children}
    </Button>
  );
};

export const NextButton = ({
  children,
  className,
  disabled,
  ...props
}: ArrowButtonProps) => {
  return (
    <Button
      {...props}
      className={classNames(
        'embla__next',
        className,
        disabled && 'embla__button--disabled',
      )}
      disabled={disabled}
      type="button"
      aria-label="Scroll to next"
    >
      <CircleChevronRight />
      {children}
    </Button>
  );
};
