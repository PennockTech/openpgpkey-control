#!/bin/sh
set -eu

CADDYFILE=/etc/caddy/Caddyfile
: > "$CADDYFILE"

for dir in /srv/sites/*/; do
  [ -d "$dir" ] || continue
  domain=$(basename "$dir")
  cat >> "$CADDYFILE" <<EOF

http://openpgpkey.${domain} {
	root * ${dir}
	file_server
}
EOF
done

echo "Generated Caddyfile:"
cat "$CADDYFILE"

exec caddy run --config "$CADDYFILE" --adapter caddyfile
