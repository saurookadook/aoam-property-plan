FROM node:22-bullseye AS frontend-dev-base
ARG NODE_ENV=development
ENV NODE_ENV=$NODE_ENV
ENV PNPM_VERSION=11.8.0
ENV pnpm='corepack pnpm'
EXPOSE 5173
WORKDIR /opt/aoam-property-plan/frontend/
COPY ./frontend/src /opt/aoam-property-plan/frontend/src
COPY ./frontend/index.html \
    ./frontend/package.json \
    ./frontend/pnpm-lock.yaml \
    ./frontend/pnpm-workspace.yaml \
    ./frontend/postcss.config.js \
    ./frontend/tsconfig.app.json \
    ./frontend/tsconfig.common.json \
    ./frontend/tsconfig.json \
    ./frontend/tsconfig.node.json \
    ./frontend/tsconfig.test.json \
    /opt/aoam-property-plan/frontend/
RUN corepack enable
RUN corepack use pnpm

FROM frontend-dev-base AS frontend-dev-build
RUN $pnpm install --frozen-lockfile
RUN $pnpm build

FROM frontend-dev-build AS frontend-dev
ENTRYPOINT [ "corepack", "pnpm" ]
CMD [ "dev" ]

FROM frontend-dev-build AS frontend-test
COPY ./frontend/vitest.setup.ts \
    ./frontend/vitest.shims.d.ts \
    /opt/aoam-property-plan/frontend/
ENTRYPOINT [ "corepack", "pnpm" ]
CMD [ "test" ]
