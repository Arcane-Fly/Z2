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
RUN corepack enable && corepack prepare yarn@4.3.1 --activate
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
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]