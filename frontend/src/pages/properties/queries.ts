import { queryOptions, useMutation, useQueryClient } from '@tanstack/react-query';

import type {
  PropertyAnalysisData,
  PropertyAnalyzeRequest,
  PropertyCompsData,
  PropertyCreateRequest,
  PropertyEntity,
} from '@/types';
import { API_SERVER_DOMAIN } from '@/constants';
import { HOUR_STALE_TIME } from '@/common/hooks/useExchangeRateQuery';
import { fetchy, unwrapEnvelope } from '@/utils';

/** Step 10's shorter stale time for data that changes with every AirROI ingest. */
export const THIRTY_MIN_STALE_TIME = 1000 * 60 * 30;

export const propertiesListQuery = queryOptions({
  queryKey: ['propertiesList'],
  queryFn: async () => {
    const propertiesList = await fetchy
      .get(`${API_SERVER_DOMAIN}/api/properties`) // force formatting
      .then(unwrapEnvelope<PropertyEntity[]>);

    return { propertiesList };
  },
  staleTime: HOUR_STALE_TIME,
});

export const propertyQuery = (propertyId: string) =>
  queryOptions({
    queryKey: ['property', propertyId],
    queryFn: async () => {
      const property = await fetchy
        .get(`${API_SERVER_DOMAIN}/api/properties/${propertyId}`) // force formatting
        .then(unwrapEnvelope<PropertyEntity>);

      return { property };
    },
    staleTime: HOUR_STALE_TIME,
  });

/**
 * Latest persisted analysis with **no AirROI call** - see chunk 3's
 * `GET /{id}/report`. `data` is `null` for a never-analysed property, which
 * `unwrapEnvelope` passes through as a normal success rather than an error.
 */
export const propertyReportQuery = (propertyId: string) =>
  queryOptions({
    queryKey: ['propertyReport', propertyId],
    queryFn: async () => {
      const report = await fetchy
        .get(`${API_SERVER_DOMAIN}/api/properties/${propertyId}/report`) // force formatting
        .then(unwrapEnvelope<PropertyAnalysisData | null>);

      return { report };
    },
    staleTime: HOUR_STALE_TIME,
  });

export const propertyCachedCompsQuery = (propertyId: string) =>
  queryOptions({
    queryKey: ['propertyComps', 'cached', propertyId],
    queryFn: async () => {
      const comps = await fetchy
        .get(`${API_SERVER_DOMAIN}/api/properties/${propertyId}/comps/cached`) // force formatting
        .then(unwrapEnvelope<PropertyCompsData>);

      return { comps };
    },
    staleTime: THIRTY_MIN_STALE_TIME,
  });

/**
 * The first `useMutation` in the repo. `retry: false` because `POST /analyze`
 * inserts a **new row on every call** - `create_or_update` with no `id` always
 * inserts - so a retried request is a second AirROI spend and a second report
 * row, not an idempotent no-op.
 */
export function useCreatePropertyMutation() {
  return useMutation({
    mutationKey: ['createProperty'],
    mutationFn: async (body: PropertyCreateRequest) =>
      fetchy
        .post(`${API_SERVER_DOMAIN}/api/properties`, { bodyJson: body })
        .then(unwrapEnvelope<PropertyEntity>),
    retry: false,
  });
}

/**
 * Same double-spend hazard as property creation - see the note above. The
 * caller is responsible for disabling its submit button while `isPending`.
 */
export function useAnalyzePropertyMutation(propertyId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationKey: ['analyzeProperty', propertyId],
    mutationFn: async (overrides: PropertyAnalyzeRequest) =>
      fetchy
        .post(`${API_SERVER_DOMAIN}/api/properties/${propertyId}/analyze`, {
          bodyJson: overrides,
        })
        .then(unwrapEnvelope<PropertyAnalysisData>),
    retry: false,
    onSuccess: (analysisData) => {
      queryClient.setQueryData(propertyReportQuery(propertyId).queryKey, {
        report: analysisData,
      });
    },
  });
}

/**
 * "Refresh comps" - a fresh, uncached `GET /comps` that spends an AirROI call,
 * as opposed to `propertyCachedCompsQuery`'s free re-read. Modelled as a
 * mutation rather than a refetched query because it is a deliberate,
 * cost-bearing user action, not something react-query should ever retry or
 * refire on its own (focus refetch, mount, and so on).
 */
export function useRefreshCompsMutation(propertyId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationKey: ['refreshComps', propertyId],
    mutationFn: async () =>
      fetchy
        .get(`${API_SERVER_DOMAIN}/api/properties/${propertyId}/comps`)
        .then(unwrapEnvelope<PropertyCompsData>),
    retry: false,
    onSuccess: (comps) => {
      queryClient.setQueryData(propertyCachedCompsQuery(propertyId).queryKey, {
        comps,
      });
    },
  });
}
