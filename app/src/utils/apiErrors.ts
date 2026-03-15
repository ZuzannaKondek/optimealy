/**
 * Extract a readable message from API errors (e.g. axios).
 * Handles detail as string or object with message.
 */
export function getApiErrorMessage(error: any): string {
  const detail = error?.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (detail && typeof detail === 'object' && typeof detail.message === 'string')
    return detail.message;
  if (error?.message) return error.message;
  return 'Coś poszło nie tak. Spróbuj ponownie.';
}
