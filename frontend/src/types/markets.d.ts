import type { BaseEntity } from './entity';

export type MarketEntity = BaseEntity & {
  country: string;
  district?: string;
  locality: string;
  region: string;
};
