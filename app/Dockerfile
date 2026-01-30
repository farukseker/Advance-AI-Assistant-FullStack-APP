FROM oven/bun:latest AS build

WORKDIR /app
COPY package.json bun.lock ./
RUN bun install

COPY . .
RUN bun run build


FROM nginx:alpine

# Remove default nginx config
RUN rm -f /etc/nginx/conf.d/default.conf

# Copy custom nginx config
# COPY app/nginx.conf /etc/nginx/conf.d/default.conf

# Copy built app
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]