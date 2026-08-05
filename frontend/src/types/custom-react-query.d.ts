export type AwaitedLoaderData<LoaderFn extends (...args: any) => any> = Awaited<
  ReturnType<ReturnType<LoaderFn>>
>;
