export const isNonEmptyString = (maybeString: unknown): maybeString is string =>
  typeof maybeString === 'string' && maybeString !== '';

export const isInvalidKey = (key: unknown) => typeof key !== 'string' || key === '';

export const isObject = (val: unknown) =>
  typeof val === 'object' && val != null && !Array.isArray(val);
