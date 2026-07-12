import type { EndpointConfig } from '@/types';

export function buildRoutePath(config: EndpointConfig): string {
  const resolvedTypeComponent = (function () {
    switch (config.type) {
      case 'overview':
        return ':entityId';
      case 'list':
      default:
        return '';
    }
  })();

  return [
    config.entityType, // force formatting
    resolvedTypeComponent,
  ]
    .filter((pathComponent) => !!pathComponent)
    .join('/');
}
