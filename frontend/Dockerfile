FROM node:20-alpine AS build
WORKDIR /app

# Declare build arguments BEFORE they're needed
ARG VITE_API_BASE_URL
ARG VITE_WS_BASE_URL
ARG VITE_APP_NAME
ARG VITE_APP_VERSION
ARG NODE_ENV=production

# Install dependencies
COPY package.json yarn.lock .yarnrc.yml ./
RUN corepack enable && corepack prepare yarn@4.9.2 --activate
RUN yarn install --immutable

# Copy source and build with env vars available
COPY . .

# Pass build args as environment variables for Vite
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_WS_BASE_URL=$VITE_WS_BASE_URL
ENV VITE_APP_NAME=$VITE_APP_NAME
ENV VITE_APP_VERSION=$VITE_APP_VERSION
ENV NODE_ENV=$NODE_ENV

RUN yarn build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx template
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# Remove default nginx config to prevent conflicts
RUN rm -f /etc/nginx/conf.d/default.conf

# Railway compatibility - set default PORT
ENV PORT=8080

# Health check for Railway
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:${PORT}/ || exit 1

# nginx:alpine automatically processes templates with envsubst on startup
# The templates in /etc/nginx/templates/ are processed by docker-entrypoint.sh
# and output to /etc/nginx/conf.d/ before nginx starts
# Use the default entrypoint for proper template processing

EXPOSE ${PORT}
