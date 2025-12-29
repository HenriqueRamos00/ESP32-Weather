#!/bin/sh
set -e

# Default API URL if not provided
API_URL=${API_URL:-/api/v1}

# Generate runtime config
cat > /usr/share/nginx/html/config.js <<EOF
window.ENV = {
  API_URL: '${API_URL}'
};
EOF

echo "Runtime config generated with API_URL=${API_URL}"

# Start nginx
exec nginx -g 'daemon off;'