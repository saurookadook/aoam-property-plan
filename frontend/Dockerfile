FROM node:22-bullseye AS frontend-dev-base
ARG NODE_ENV=development
ENV NODE_ENV=$NODE_ENV
ENV PNPM_VERSION=11.9.0
ENV pnpm='corepack pnpm'
EXPOSE 5173
WORKDIR /opt/aoam-property-plan/frontend/
COPY ./frontend/package.json \
    ./frontend/pnpm-lock.yaml \
    ./frontend/pnpm-workspace.yaml \
    ./
RUN corepack enable
RUN corepack prepare pnpm@${PNPM_VERSION} --activate
RUN $pnpm install --frozen-lockfile


FROM frontend-dev-base AS frontend-dev-build
WORKDIR /opt/aoam-property-plan/frontend/
COPY ./frontend/src ./src
COPY ./frontend/index.html \
    ./frontend/globals.d.ts \
    ./frontend/postcss.config.js \
    ./frontend/tsconfig.app.json \
    ./frontend/tsconfig.common.json \
    ./frontend/tsconfig.json \
    ./frontend/tsconfig.node.json \
    ./frontend/tsconfig.strict.json \
    ./frontend/tsconfig.test.json \
    ./
RUN $pnpm build


FROM frontend-dev-build AS frontend-dev
ENTRYPOINT [ "corepack", "pnpm" ]
CMD [ "dev" ]


FROM frontend-dev-build AS frontend-test
WORKDIR /opt/aoam-property-plan/frontend/
COPY ./frontend/__mocks__ ./__mocks__
COPY ./frontend/vitest.setup.ts \
    ./frontend/vitest.shims.d.ts \
    ./
ENTRYPOINT [ "corepack", "pnpm" ]
CMD [ "test" ]
