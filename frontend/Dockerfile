# ---------- Stage 1: Build React App ----------
FROM node:18-alpine as build

WORKDIR /app

# Accept backend URL during build time
ARG REACT_APP_BACKEND_URL
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL

COPY package*.json ./
RUN npm install

COPY . .

# Build the React app with the backend URL baked in
RUN npm run build

# ---------- Stage 2: Serve using Nginx ----------
FROM nginx:alpine

# ✅ Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# ✅ Copy build output from the previous stage
COPY --from=build /app/build /usr/share/nginx/html

# ✅ Expose the web port
EXPOSE 80

# ✅ Run Nginx in foreground
CMD ["nginx", "-g", "daemon off;"]