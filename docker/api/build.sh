#!/bin/bash
set -e

IMAGE_NAME="web-collector"
VERSION=${1:-latest}

echo "================================================"
echo "  构建镜像: ${IMAGE_NAME}:${VERSION}"
echo "================================================"

cd "$(dirname "$0")/../.."

docker build \
  -t "${IMAGE_NAME}:${VERSION}" \
  -f docker/api/Dockerfile \
  .

echo ""
echo "构建完成: ${IMAGE_NAME}:${VERSION}"
echo ""
echo "启动全套服务:"
echo "  cd docker"
echo "  docker compose up -d"
echo ""
echo "访问前端:"
echo "  http://<host>:8080"
echo ""
echo "访问 API 文档:"
echo "  http://<host>:8000/docs"
