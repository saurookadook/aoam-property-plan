import { useCallback, useMemo, useState } from 'react';
import { Alert, Snackbar, type AlertColor } from '@mui/material';

/** react-query's own `status` union, which is what every caller has to hand. */
export type ToastStatus = 'error' | 'pending' | 'success';

const DEFAULT_FALLBACK_ERROR_MESSAGE = 'An unknown error occurred.';

/**
 * @note `alertSeverity` is optional and **derived from `status`** when omitted.
 * Callers used to pass `alertSeverity={status}`, which typechecks only because
 * strict mode is off: `status` can be `'pending'`, and `'pending'` is not an MUI
 * `AlertColor`. Deriving it removes the mismatch rather than widening the prop
 * to accept a value `Alert` cannot render.
 */
export function Toast({
  alertSeverity,
  autoHideDuration,
  error,
  fallbackErrorMessage = DEFAULT_FALLBACK_ERROR_MESSAGE,
  status,
}: {
  alertSeverity?: AlertColor;
  autoHideDuration?: number;
  error: Error | null;
  /**
   * What to say when the query failed without an `Error` to quote. Passed in
   * rather than hardcoded, since every page reuses this component and only the
   * page knows what it was fetching.
   */
  fallbackErrorMessage?: string;
  status: ToastStatus;
}) {
  const [snackbarOpen, setSnackbarOpen] = useState(true);

  const handleSnackbarClose = useCallback(() => {
    setSnackbarOpen(false);
  }, [setSnackbarOpen]);

  const autoHideDurationMemo = useMemo(() => {
    if (autoHideDuration != null) return autoHideDuration;
    return status === 'error' ? 6000 : 2000;
  }, [autoHideDuration, status]);

  const resolvedSeverity = useMemo<AlertColor>(() => {
    if (alertSeverity != null) return alertSeverity;
    return status === 'success' ? 'success' : 'error';
  }, [alertSeverity, status]);

  const alertText = useMemo(() => {
    if (status === 'success') {
      return 'Operation completed successfully!';
    }

    return error != null ? String(error) : fallbackErrorMessage;
  }, [error, fallbackErrorMessage, status]);

  if (status === 'pending') {
    return null;
  }

  return (
    <Snackbar
      autoHideDuration={autoHideDurationMemo}
      open={snackbarOpen}
      onClose={handleSnackbarClose}
    >
      <Alert
        onClose={handleSnackbarClose}
        severity={resolvedSeverity}
        sx={{ width: '100%' }}
        variant="filled"
      >
        {alertText}
      </Alert>
    </Snackbar>
  );
}
