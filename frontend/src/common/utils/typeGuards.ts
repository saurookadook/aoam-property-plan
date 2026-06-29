export const isInvalidKey = (key: unknown) => typeof key !== 'string' || key === '';

export const isObject = (val: unknown) =>
  typeof val === 'object' && val != null && !Array.isArray(val);
