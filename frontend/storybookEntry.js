const concurrently = require('concurrently');

const buildCommands = [
  {
    command: 'pnpm mock-server:build',
    name: 'Build Mock Server',
    prefixColor: 'blue',
  },
  {
    command: 'pnpm storybook:build',
    name: 'Build Storybook',
    prefixColor: 'green',
  },
];

const startCommands = [
  {
    command: 'pnpm mock-server:start',
    name: 'Start Mock Server',
    prefixColor: 'blue',
  },
  {
    command: 'pnpm storybook:start',
    name: 'Start Storybook',
    prefixColor: 'green',
  },
];

function logErrorAndExit(...args) {
  console.error(...args);
  process.exit(1);
}

const run = async () => {
  const { result: buildResult } = await concurrently(buildCommands, {
    killOthersOn: ['failure'],
  });

  const shouldStart = await buildResult.then(
    (commands) => {
      console.log('Build process completed successfully: ', commands);
      return commands.every((command) => command.exitCode === 0);
    },
    (failureArgs) => {
      logErrorAndExit('Build process failed: ', failureArgs);
    },
  );

  if (!shouldStart) {
    logErrorAndExit(
      'Encountered unexpected errors with build processes. Exiting without starting processes.',
    );
  }

  const { result: startResult } = await concurrently(startCommands, {
    killOthersOn: ['failure'],
  });

  startResult.then(
    () => {
      console.log('Both Mock Server and Storybook started successfully.');
    },
    (failureArgs) => {
      logErrorAndExit(
        'Both processes have been terminated but one of them failed with an error: ',
        failureArgs,
      );
    },
  );
};

run();
