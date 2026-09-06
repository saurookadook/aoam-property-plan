import { useMemo } from 'react';
import { useLoaderData, type LoaderFunctionArgs } from 'react-router';
import { QueryClient, useSuspenseQuery } from '@tanstack/react-query';
import { Typography } from '@mui/material';

import { LoadingState, Toast } from '@/common/components';
import { useExchangeRateQuery } from '@/common/hooks/useExchangeRateQuery';
import { dataConfidence } from '@/common/utils/dataConfidence';
import { reportToScenarioOverrides } from '@/common/utils/propertyAnalysis';
import type { CurrencyRate } from '@/common/utils/currency';
import { FlexColumn } from '@/layouts';
import {
  propertyCachedCompsQuery,
  propertyQuery,
  propertyReportQuery,
} from '../queries';
import {
  AssumptionsPanel,
  DataConfidenceBanner,
  ExpenseBreakdownCard,
  MetricGrid,
  PropertyCompsTable,
  PropertyHeaderCard,
  RevenueComparisonRow,
  SeasonalityChart,
  SensitivityTable,
} from './components';
import { DEFAULT_SCENARIO_OVERRIDES } from './constants';
import { reportCurrencyRate } from './utils';

import './styles.scss';

export const propertyOverviewLoader =
  (_queryClient: QueryClient) =>
  async ({ params }: LoaderFunctionArgs) => {
    if (!params.propertyId) {
      throw new Error("No 'propertyId' param provided!");
    }

    // `POST /analyze` is never in a loader - react-router data mode would
    // re-run it on every navigation. Only `GET`s belong here.
    await Promise.all([
      _queryClient.ensureQueryData(propertyQuery(params.propertyId)),
      _queryClient.ensureQueryData(propertyReportQuery(params.propertyId)),
      _queryClient.ensureQueryData(propertyCachedCompsQuery(params.propertyId)),
    ]);

    return { propertyId: params.propertyId };
  };

export function PropertyOverview() {
  const { propertyId } = useLoaderData() as Awaited<
    ReturnType<ReturnType<typeof propertyOverviewLoader>>
  >;

  const {
    data: propertyData,
    error: propertyError,
    isFetching: isPropertyFetching,
    status: propertyStatus,
  } = useSuspenseQuery(propertyQuery(propertyId));
  const { data: reportData } = useSuspenseQuery(propertyReportQuery(propertyId));
  const { data: compsData } = useSuspenseQuery(propertyCachedCompsQuery(propertyId));
  const { data: exchangeRateData } = useExchangeRateQuery();

  const property = propertyData?.property;
  const analysis = reportData?.report ?? null;
  const comps = compsData?.comps ?? [];

  const liveRate: CurrencyRate | null = useMemo(() => {
    return exchangeRateData?.exchangeRate == null
      ? null
      : {
          rate: exchangeRateData.exchangeRate.cop_per_usd,
          rateAsOf: exchangeRateData.exchangeRate.record_date,
          rateSource: 'live',
        };
  }, [exchangeRateData]);

  // "The rate that produced a number is the rate that converts it": a report's
  // own rate wins absolutely once one exists; only a never-analysed property
  // falls back to today's live rate.
  const { confidence, displayRate, reportRate } = useMemo(() => {
    if (analysis == null) {
      return {
        confidence: dataConfidence(null, null).level,
        displayRate: liveRate,
        reportRate: null,
      };
    }

    const reportRate = reportCurrencyRate(analysis.report);
    const confidenceLevel = dataConfidence(
      analysis.report.annual_revenue_source,
      analysis.report.comp_count,
    ).level;
    return { confidence: confidenceLevel, displayRate: reportRate, reportRate };
  }, [analysis, liveRate]);

  return (
    <FlexColumn id="property-overview" className="property-overview">
      {isPropertyFetching ? (
        <div className="loading-state__wrapper">
          <LoadingState />
        </div>
      ) : property == null ? (
        <Typography variant="body1">Property not found.</Typography>
      ) : (
        <FlexColumn className="property-overview__wrapper">
          <PropertyHeaderCard property={property} rate={displayRate} />

          {analysis == null ? (
            <FlexColumn className="property-overview__unanalysed">
              <Typography variant="body1">
                This property has not been analysed yet.
              </Typography>

              <AssumptionsPanel
                initialOverrides={{
                  ...DEFAULT_SCENARIO_OVERRIDES,
                  purchase_price_cop: property.purchase_price_cop ?? undefined,
                }}
                propertyId={propertyId}
                submitLabel="Analyse"
              />
            </FlexColumn>
          ) : (
            <FlexColumn className="property-overview__analysis">
              <DataConfidenceBanner
                compCount={analysis.report.comp_count}
                source={analysis.report.annual_revenue_source}
              />

              <MetricGrid analysis={analysis} confidence={confidence} />

              <RevenueComparisonRow report={analysis.report} />

              <ExpenseBreakdownCard expenses={analysis.expenses} rate={reportRate} />

              <SensitivityTable cells={analysis.sensitivity} rate={reportRate} />

              <SeasonalityChart
                distribution={analysis.report.monthly_revenue_distribution}
              />

              <AssumptionsPanel
                initialOverrides={reportToScenarioOverrides(analysis.report)}
                propertyId={propertyId}
                submitLabel="Re-analyse"
              />

              <PropertyCompsTable
                comps={comps}
                propertyId={propertyId}
                rate={displayRate}
              />
            </FlexColumn>
          )}
        </FlexColumn>
      )}

      {!isPropertyFetching && propertyError != null && (
        <Toast
          error={propertyError}
          fallbackErrorMessage="An unknown error occurred while fetching this property."
          status={propertyStatus}
        />
      )}
    </FlexColumn>
  );
}
