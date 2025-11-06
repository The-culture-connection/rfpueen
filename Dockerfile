# Use nginx to serve static files
FROM nginx:alpine

# Copy all HTML files to nginx html directory
COPY *.html /usr/share/nginx/html/
COPY dashboard /usr/share/nginx/html/dashboard
COPY explore /usr/share/nginx/html/explore
COPY login /usr/share/nginx/html/login
COPY sign-up /usr/share/nginx/html/sign-up
COPY registration1 /usr/share/nginx/html/registration1
COPY registration2 /usr/share/nginx/html/registration2
COPY registration3 /usr/share/nginx/html/registration3
COPY registration4 /usr/share/nginx/html/registration4
COPY registration5 /usr/share/nginx/html/registration5

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
