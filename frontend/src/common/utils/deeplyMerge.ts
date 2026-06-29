import type { KeyedObject } from '@/types';

import { isObject } from './typeGuards';

export function deeplyMerge<T extends KeyedObject = KeyedObject>(
  target: KeyedObject,
  source: T,
): T {
  if (!isObject(target)) {
    throw new TypeError("[deeplyMerge] : argument 'target' must be an object!");
  }
  if (!isObject(source)) {
    throw new TypeError("[deeplyMerge] : argument 'source' must be an object!");
  }

  for (const [sourceKey, sourceValue] of Object.entries(source)) {
    target[sourceKey] = handleAssignment({
      assignmentTarget: target[sourceKey],
      targetValue: sourceValue,
    });
  }

  return target as T;
}

function handleAssignment({
  assignmentTarget,
  targetValue,
}: {
  assignmentTarget: KeyedObject;
  targetValue: any;
}) {
  return isObject(targetValue) // force formatting
    ? deeplyMerge(assignmentTarget || {}, targetValue)
    : targetValue;
}
