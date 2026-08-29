import type { EndpointConfig } from '@/types';

export const DEFAULT_ENTITY_ID_PATH_PARAM = 'entityId';

/**
 * The single route-path builder for both mock servers.
 *
 * There used to be two: this one hardcoded `:entityId`, while
 * `buildMirageStorybookRoutePath` honoured `config.entityIdPathParam`. The same
 * config therefore produced different paths - and different `request.params`
 * keys - depending on which server was running, so a fixture that resolved under
 * Storybook resolved to the `list` fallback under vitest.
 */
export function buildRoutePath(config: EndpointConfig): string {
  if (config.fullPath != null) {
    return config.fullPath;
  }

  const segments: string[] = [config.entityType ?? ''];

  if (config.type === 'overview' || config.type === 'sub-resource') {
    segments.push(`:${resolveEntityIdPathParam(config)}`);
  }

  if (config.subPath != null) {
    segments.push(...config.subPath);
  }

  return segments.filter((pathComponent) => !!pathComponent).join('/');
}

export function resolveEntityIdPathParam(config: EndpointConfig): string {
  return config.entityIdPathParam ?? DEFAULT_ENTITY_ID_PATH_PARAM;
}
