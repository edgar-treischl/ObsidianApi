curl -v -X POST "http://127.0.0.1:27123/search/simple?query=contextLength" \
  -H "Authorization: Bearer 235ea7c19ae181c4bb55810b382f249fbf629f477e71a1d9034dd8118f56e3a8"


 docker compose exec obsidian sh -lc 'curl -s -v -H "Authorization: Bearer 235ea7c19ae181c4bb55810b382f249fbf629f477e71a1d9034dd8118f56e3a8" http://127.0.0.1:27123/vault/'