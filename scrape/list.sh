curl -v -X POST http://127.0.0.1:27123/search \
  -H "Authorization: Bearer 235ea7c19ae181c4bb55810b382f249fbf629f477e71a1d9034dd8118f56e3a8" \
  -H "Content-Type: application/vnd.olrapi.jsonlogic+json" \
  --data-raw '{
    "glob": ["*.md", {"var": "path"}]
  }'

curl -v -H "Authorization: Bearer 235ea7c19ae181c4bb55810b382f249fbf629f477e71a1d9034dd8118f56e3a8" http://127.0.0.1:27123/vault/

curl -v -H "Authorization: Bearer 235ea7c19ae181c4bb55810b382f249fbf629f477e71a1d9034dd8118f56e3a8" http://127.0.0.1:27123/vault/

curl --http1.1 -v -H "Authorization: Bearer 235ea7c19ae181c4bb55810b382f249fbf629f477e71a1d9034dd8118f56e3a8" -H "Accept: application/json" http://127.0.0.1:27123/vault/