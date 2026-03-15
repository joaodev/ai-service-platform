#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1"
    exit 1
  fi
}

require_env() {
  local name="$1"
  if [[ -z "${!name:-}" ]]; then
    echo "Missing required environment variable: $name"
    exit 1
  fi
}

upsert_container_app() {
  local app_name="$1"
  local image="$2"
  local ingress_mode="$3"
  local target_port="$4"

  if az containerapp show --resource-group "$RESOURCE_GROUP" --name "$app_name" >/dev/null 2>&1; then
    echo "Updating Container App: $app_name"

    if [[ "$ingress_mode" == "external" ]]; then
      az containerapp update \
        --resource-group "$RESOURCE_GROUP" \
        --name "$app_name" \
        --image "$image" \
        --set-env-vars \
          DATABASE_URL="$DATABASE_URL" \
          REDIS_URL="$REDIS_URL" \
          CELERY_BROKER_URL="$CELERY_BROKER_URL" \
          CELERY_RESULT_BACKEND="$CELERY_RESULT_BACKEND" \
          OPENAI_API_KEY="$OPENAI_API_KEY" \
          AZURE_OPENAI_API_KEY="$OPENAI_API_KEY" \
          JWT_SECRET="$JWT_SECRET" \
          JWT_SECRET_KEY="$JWT_SECRET" \
        --output none
    else
      az containerapp update \
        --resource-group "$RESOURCE_GROUP" \
        --name "$app_name" \
        --image "$image" \
        --set-env-vars \
          DATABASE_URL="$DATABASE_URL" \
          REDIS_URL="$REDIS_URL" \
          CELERY_BROKER_URL="$CELERY_BROKER_URL" \
          CELERY_RESULT_BACKEND="$CELERY_RESULT_BACKEND" \
          OPENAI_API_KEY="$OPENAI_API_KEY" \
          AZURE_OPENAI_API_KEY="$OPENAI_API_KEY" \
          JWT_SECRET="$JWT_SECRET" \
          JWT_SECRET_KEY="$JWT_SECRET" \
        --output none
    fi
  else
    echo "Creating Container App: $app_name"

    if [[ "$ingress_mode" == "external" ]]; then
      az containerapp create \
        --resource-group "$RESOURCE_GROUP" \
        --name "$app_name" \
        --environment "$CONTAINERAPPS_ENV" \
        --image "$image" \
        --ingress external \
        --target-port "$target_port" \
        --min-replicas 1 \
        --max-replicas 5 \
        --env-vars \
          DATABASE_URL="$DATABASE_URL" \
          REDIS_URL="$REDIS_URL" \
          CELERY_BROKER_URL="$CELERY_BROKER_URL" \
          CELERY_RESULT_BACKEND="$CELERY_RESULT_BACKEND" \
          OPENAI_API_KEY="$OPENAI_API_KEY" \
          AZURE_OPENAI_API_KEY="$OPENAI_API_KEY" \
          JWT_SECRET="$JWT_SECRET" \
          JWT_SECRET_KEY="$JWT_SECRET" \
        --output none
    else
      az containerapp create \
        --resource-group "$RESOURCE_GROUP" \
        --name "$app_name" \
        --environment "$CONTAINERAPPS_ENV" \
        --image "$image" \
        --min-replicas 1 \
        --max-replicas 5 \
        --env-vars \
          DATABASE_URL="$DATABASE_URL" \
          REDIS_URL="$REDIS_URL" \
          CELERY_BROKER_URL="$CELERY_BROKER_URL" \
          CELERY_RESULT_BACKEND="$CELERY_RESULT_BACKEND" \
          OPENAI_API_KEY="$OPENAI_API_KEY" \
          AZURE_OPENAI_API_KEY="$OPENAI_API_KEY" \
          JWT_SECRET="$JWT_SECRET" \
          JWT_SECRET_KEY="$JWT_SECRET" \
        --output none
    fi
  fi
}

require_cmd az

require_env RESOURCE_GROUP
require_env LOCATION
require_env ACR_NAME
require_env CONTAINERAPPS_ENV
require_env API_APP_NAME
require_env WORKER_APP_NAME
require_env DATABASE_URL
require_env REDIS_URL
require_env OPENAI_API_KEY
require_env JWT_SECRET

CELERY_BROKER_URL="${CELERY_BROKER_URL:-$REDIS_URL}"
CELERY_RESULT_BACKEND="${CELERY_RESULT_BACKEND:-redis://$(echo "$REDIS_URL" | sed 's#redis://##' | sed 's#/0$##')/1}"

az account show >/dev/null 2>&1 || {
  echo "Azure login required. Run: az login"
  exit 1
}

echo "Ensuring resource group..."
az group create --name "$RESOURCE_GROUP" --location "$LOCATION" --output none

echo "Ensuring Azure Container Registry..."
if ! az acr show --name "$ACR_NAME" --resource-group "$RESOURCE_GROUP" >/dev/null 2>&1; then
  az acr create --name "$ACR_NAME" --resource-group "$RESOURCE_GROUP" --sku Basic --admin-enabled true --output none
fi

ACR_LOGIN_SERVER="$(az acr show --name "$ACR_NAME" --resource-group "$RESOURCE_GROUP" --query loginServer -o tsv)"
API_IMAGE="$ACR_LOGIN_SERVER/ai-platform-api:latest"
WORKER_IMAGE="$ACR_LOGIN_SERVER/ai-platform-worker:latest"

echo "Building and pushing API image to ACR..."
az acr build --registry "$ACR_NAME" --image "ai-platform-api:latest" --file Dockerfile . --output none

echo "Building and pushing Worker image to ACR..."
az acr build --registry "$ACR_NAME" --image "ai-platform-worker:latest" --file Dockerfile.worker . --output none

echo "Ensuring Container Apps environment..."
if ! az containerapp env show --name "$CONTAINERAPPS_ENV" --resource-group "$RESOURCE_GROUP" >/dev/null 2>&1; then
  az containerapp env create --name "$CONTAINERAPPS_ENV" --resource-group "$RESOURCE_GROUP" --location "$LOCATION" --output none
fi

echo "Deploying API Container App..."
upsert_container_app "$API_APP_NAME" "$API_IMAGE" "external" "8000"

echo "Deploying Worker Container App..."
upsert_container_app "$WORKER_APP_NAME" "$WORKER_IMAGE" "internal" "0"

API_URL="$(az containerapp show --resource-group "$RESOURCE_GROUP" --name "$API_APP_NAME" --query properties.configuration.ingress.fqdn -o tsv)"

echo ""
echo "Deployment completed."
echo "API endpoint: https://$API_URL"
echo "Worker app: $WORKER_APP_NAME"
