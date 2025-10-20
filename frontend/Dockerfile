# Use lightweight Nginx image
FROM nginx:alpine

# Set working directory inside container
WORKDIR /usr/share/nginx/html

# Remove default nginx static files
RUN rm -rf ./*

# Copy your static site files into the container
COPY . .

# Expose port 80 for HTTP
EXPOSE 80

# Simple healthcheck (optional)
HEALTHCHECK CMD wget -qO- http://localhost/ || exit 1

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
