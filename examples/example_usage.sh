#!/bin/bash
# Example usage of Graphiti CLI

echo "=== Graphiti CLI Examples ==="
echo

# 1. Basic search
echo "1. Basic search for 'authentication':"
graphiti search "authentication" --max-results 5

echo -e "\n2. Temporal search - changes in last 7 days:"
graphiti search "system updates" \
  --created-after "$(date -d '7 days ago' -Iseconds)" \
  --order newest

echo -e "\n3. Entity-specific search:"
graphiti search "payment" \
  --entity-types Component \
  --entity-types Pattern

echo -e "\n4. Edge type filtering:"
graphiti search "UserService" \
  --edge-types DEPENDS_ON \
  --edge-types IMPLEMENTS_PATTERN

echo -e "\n5. Advanced search with reranking:"
graphiti search "design patterns" \
  --method hybrid \
  --reranker cross_encoder

echo -e "\n6. Graph statistics:"
graphiti maintenance stats

echo -e "\n7. Add an episode:"
graphiti episodes add "Example Note" \
  "This is a test episode demonstrating the CLI" \
  --source text

echo -e "\n8. Get recent episodes:"
graphiti episodes get --last-n 5 --output pretty

# Parallel search example
echo -e "\n9. Parallel search example:"
echo "Running 3 searches in parallel..."
{
  graphiti search "authentication" &
  graphiti search "database" &
  graphiti search "api" &
  wait
} | jq -s 'add | length' | xargs -I {} echo "Total results from parallel searches: {}"