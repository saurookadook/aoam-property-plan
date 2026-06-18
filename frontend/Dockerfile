FROM node:22-bullseye AS client-dev-base
ARG NODE_ENV=development
ENV NODE_ENV=$NODE_ENV
ENV PNPM_VERSION=11.8.0
ENV pnpm='corepack pnpm'
EXPOSE 5173
WORKDIR /opt/aoam-property-plan/frontend/
COPY .env \
    .yarnrc.yml \
    package.json \
    pnpm-lock.yaml \
    /opt/aoam-property-plan/frontend/
COPY ./src /opt/aoam-property-plan/frontend/src
# COPY .env .env.test /opt/aoam-property-plan/frontend/client/
# COPY shared/ /opt/aoam-property-plan/frontend/shared/
# COPY .env .env.test /opt/aoam-property-plan/frontend/shared/
RUN corepack enable
RUN corepack use pnpm@$PNPM_VERSION

FROM client-dev-base AS client-dev-build
RUN $pnpm install --frozen-lockfile
RUN $pnpm build

FROM client-dev-build AS client-dev
ENTRYPOINT [ "corepack", "pnpm" ]
CMD [ "dev" ]

FROM client-dev-build AS client-test
COPY .env.test /opt/aoam-property-plan/frontend
ENTRYPOINT [ "corepack", "pnpm" ]
CMD [ "test" ]
