export const API_SERVER_DOMAIN = (function () {
  console.log({
    name: 'pre API_SERVER_DOMAIN build',
    VITE_API_SERVER_DOMAIN: import.meta.env.VITE_API_SERVER_DOMAIN,
  });

  if (import.meta.env.VITE_API_SERVER_DOMAIN != null) {
    return import.meta.env.VITE_API_SERVER_DOMAIN;
  }

  if (window.location.hostname.indexOf('aoam-frontend-app-production') >= 0) {
    // TODO: tmp fix for `VITE_` variables not being exposed for some reason
    return 'https://aoam-property-plan-production.up.railway.app';
  }

  return window.location.origin;
})();

console.log({
  name: 'post API_SERVER_DOMAIN build',
  API_SERVER_DOMAIN,
  VITE_API_SERVER_DOMAIN: import.meta.env.VITE_API_SERVER_DOMAIN,
});

export * from './endpointConfigs';
export * from './property';
export * from './theme';
