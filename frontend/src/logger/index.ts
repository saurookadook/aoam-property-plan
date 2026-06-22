import log, { type LogLevel } from 'loglevel';

type LogLevelName = keyof LogLevel;

type LogLevelsByNumber = {
  [n: number]: LogLevelName;
};

const logLevelsByNumber: LogLevelsByNumber = (function () {
  const result: LogLevelsByNumber = {};

  for (const logLevelEntry of Object.entries(log.levels as LogLevel)) {
    const [levelName, levelValue] = logLevelEntry as [LogLevelName, number];

    result[levelValue] = levelName;
  }

  return result;
})();

function getLevelName(levelValue: number): LogLevelName {
  return logLevelsByNumber[levelValue] ?? 'SILENT';
}

const originalFactory = log.methodFactory;

log.methodFactory = function (methodName, logLevel, loggerName = 'root') {
  const rawMethod = originalFactory(methodName, logLevel, loggerName);

  const levelName = getLevelName(logLevel);

  return function (...args) {
    const [message, ...rest] = args;
    rawMethod(
      `[${loggerName.toString()} - ${levelName.toString()}] : ${message}`,
      ...rest,
    );
  };
};

// TODO: maybe remove this? it's not working like expected
const ENV_LOG_LEVEL: string = (function () {
  if (typeof process === 'undefined') {
    return 'debug';
  }

  return (process.env.LOG_LEVEL || '').toLowerCase();
})();

log.rebuild();
log.setDefaultLevel(
  ENV_LOG_LEVEL.toUpperCase() in log.levels
    ? (ENV_LOG_LEVEL as log.LogLevelDesc)
    : 'silent',
);

export { log };
