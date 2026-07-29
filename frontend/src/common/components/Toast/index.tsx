import { useCallback, useMemo, useState } from 'react';
import { Alert, Snackbar } from '@mui/material';

export function Toast({
  alertSeverity = 'error',
  autoHideDuration,
  error,
  status,
}: {
  alertSeverity?: 'error' | 'success';
  autoHideDuration?: number;
  error: Error | null;
  status: 'error' | 'pending' | 'success';
}) {
  const [snackbarOpen, setSnackbarOpen] = useState(status === 'error');

  const handleSnackbarClose = useCallback(() => {
    setSnackbarOpen(false);
  }, [setSnackbarOpen]);

  const autoHideDurationMemo = useMemo(() => {
    if (autoHideDuration != null) return autoHideDuration;
    return status === 'error' ? 6000 : 2000;
  }, [autoHideDuration, status]);

  const alertText = useMemo(() => {
    if (status === 'success') {
      return 'Operation completed successfully!';
    }

    return error != null
      ? String(error)
      : 'An unknown error occurred while fetching market overview data.';
  }, [error, status]);

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
        severity={alertSeverity}
        sx={{ width: '100%' }}
        variant="filled"
      >
        {alertText}
      </Alert>
    </Snackbar>
  );
}
