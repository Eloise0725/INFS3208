#!/bin/bash

# Quick reference for common GKE operations
# This is a cheat sheet - source it or copy commands as needed

PROJECT_ID="infs3208-magpie"
CLUSTER_NAME="msms-cluster"
REGION="australia-southeast2"
NAMESPACE="msms"
REGISTRY="australia-southeast2-docker.pkg.dev"

# =============================================================================
# CLUSTER OPERATIONS
# =============================================================================

# Connect to cluster
alias gke-connect="gcloud container clusters get-credentials ${CLUSTER_NAME} --region ${REGION} --project ${PROJECT_ID}"

# View cluster info
alias gke-info="gcloud container clusters describe ${CLUSTER_NAME} --region ${REGION} --project ${PROJECT_ID}"

# List all clusters
alias gke-list="gcloud container clusters list --project ${PROJECT_ID}"

# =============================================================================
# KUBECTL SHORTCUTS
# =============================================================================

# Namespace shortcuts
alias k="kubectl -n ${NAMESPACE}"
alias kgp="kubectl get pods -n ${NAMESPACE}"
alias kgs="kubectl get svc -n ${NAMESPACE}"
alias kgi="kubectl get ingress -n ${NAMESPACE}"
alias kgd="kubectl get deployment -n ${NAMESPACE}"

# Logs
alias klogs="kubectl logs -f -n ${NAMESPACE}"
alias klogs-web="kubectl logs -f deployment/msms-web -n ${NAMESPACE}"
alias klogs-db="kubectl logs -f deployment/postgres -n ${NAMESPACE}"

# Describe resources
alias kdesc="kubectl describe -n ${NAMESPACE}"

# Execute commands in pods
alias kexec="kubectl exec -it -n ${NAMESPACE}"

# =============================================================================
# DEPLOYMENT OPERATIONS
# =============================================================================

# Deploy all manifests
deploy_all() {
    kubectl apply -f k8s/namespace.yaml
    kubectl apply -f k8s/configmap.yaml
    kubectl apply -f k8s/secret.yaml
    kubectl apply -f k8s/postgres.yaml
    kubectl apply -f k8s/web.yaml
    kubectl apply -f k8s/ingress.yaml
    echo "✅ All manifests deployed"
}

# Delete all resources
delete_all() {
    kubectl delete -f k8s/web.yaml
    kubectl delete -f k8s/postgres.yaml
    kubectl delete -f k8s/ingress.yaml
    echo "⚠️  Resources deleted (keeping configmap, secrets, namespace)"
}

# Restart deployment
restart_web() {
    kubectl rollout restart deployment/msms-web -n ${NAMESPACE}
    kubectl rollout status deployment/msms-web -n ${NAMESPACE}
}

# =============================================================================
# IMAGE OPERATIONS
# =============================================================================

# Build and push image
build_and_push() {
    local TAG=${1:-latest}
    local IMAGE_PATH="${REGISTRY}/${PROJECT_ID}/msms/msms:${TAG}"

    echo "🔨 Building image..."
    docker build -t "${IMAGE_PATH}" .

    echo "📤 Pushing image..."
    docker push "${IMAGE_PATH}"

    echo "✅ Image built and pushed: ${IMAGE_PATH}"
}

# List images in Artifact Registry
list_images() {
    gcloud artifacts docker images list \
        "${REGISTRY}/${PROJECT_ID}/msms/msms" \
        --project "${PROJECT_ID}"
}

# =============================================================================
# DEBUG OPERATIONS
# =============================================================================

# Get all resources
get_all() {
    echo "=== PODS ==="
    kubectl get pods -n ${NAMESPACE}
    echo ""
    echo "=== SERVICES ==="
    kubectl get svc -n ${NAMESPACE}
    echo ""
    echo "=== DEPLOYMENTS ==="
    kubectl get deployments -n ${NAMESPACE}
    echo ""
    echo "=== INGRESS ==="
    kubectl get ingress -n ${NAMESPACE}
    echo ""
    echo "=== PVC ==="
    kubectl get pvc -n ${NAMESPACE}
}

# Get pod logs with errors
get_errors() {
    echo "=== WEB POD ERRORS ==="
    kubectl logs -n ${NAMESPACE} -l app=msms-web --tail=50 | grep -i error
    echo ""
    echo "=== POSTGRES POD ERRORS ==="
    kubectl logs -n ${NAMESPACE} -l app=postgres --tail=50 | grep -i error
}

# Shell into web pod
shell_web() {
    local POD=$(kubectl get pod -n ${NAMESPACE} -l app=msms-web -o jsonpath="{.items[0].metadata.name}")
    kubectl exec -it -n ${NAMESPACE} "${POD}" -- /bin/bash
}

# Shell into postgres pod
shell_db() {
    local POD=$(kubectl get pod -n ${NAMESPACE} -l app=postgres -o jsonpath="{.items[0].metadata.name}")
    kubectl exec -it -n ${NAMESPACE} "${POD}" -- /bin/bash
}

# Connect to postgres database
psql_connect() {
    local POD=$(kubectl get pod -n ${NAMESPACE} -l app=postgres -o jsonpath="{.items[0].metadata.name}")
    kubectl exec -it -n ${NAMESPACE} "${POD}" -- psql -U msms -d msms
}

# =============================================================================
# MONITORING
# =============================================================================

# Watch pods
watch_pods() {
    watch kubectl get pods -n ${NAMESPACE}
}

# Get resource usage
get_usage() {
    echo "=== POD RESOURCE USAGE ==="
    kubectl top pods -n ${NAMESPACE}
}

# Get events
get_events() {
    kubectl get events -n ${NAMESPACE} --sort-by='.lastTimestamp' | tail -20
}

# =============================================================================
# SECRETS MANAGEMENT
# =============================================================================

# Update Django secret
update_django_secret() {
    local SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    kubectl create secret generic msms-secrets \
        --from-literal=DJANGO_SECRET_KEY="${SECRET_KEY}" \
        --from-literal=DB_PASSWORD="$(kubectl get secret msms-secrets -n ${NAMESPACE} -o jsonpath='{.data.DB_PASSWORD}' | base64 -d)" \
        --namespace=${NAMESPACE} \
        --dry-run=client -o yaml | kubectl apply -f -
    echo "✅ Django secret key updated"
}

# Update DB password
update_db_password() {
    local DB_PASSWORD=$(openssl rand -base64 32)
    kubectl create secret generic msms-secrets \
        --from-literal=DJANGO_SECRET_KEY="$(kubectl get secret msms-secrets -n ${NAMESPACE} -o jsonpath='{.data.DJANGO_SECRET_KEY}' | base64 -d)" \
        --from-literal=DB_PASSWORD="${DB_PASSWORD}" \
        --namespace=${NAMESPACE} \
        --dry-run=client -o yaml | kubectl apply -f -
    echo "✅ DB password updated to: ${DB_PASSWORD}"
    echo "⚠️  You must restart postgres deployment and re-initialize the database!"
}

# =============================================================================
# HELP
# =============================================================================

show_help() {
    echo "📚 GKE Commands Cheat Sheet"
    echo ""
    echo "Cluster Operations:"
    echo "  gke-connect           - Connect to GKE cluster"
    echo "  gke-info              - View cluster information"
    echo "  gke-list              - List all clusters"
    echo ""
    echo "Kubectl Shortcuts:"
    echo "  kgp                   - Get pods"
    echo "  kgs                   - Get services"
    echo "  kgi                   - Get ingress"
    echo "  klogs-web             - Follow web logs"
    echo "  klogs-db              - Follow database logs"
    echo ""
    echo "Deployment:"
    echo "  deploy_all            - Deploy all manifests"
    echo "  delete_all            - Delete deployments"
    echo "  restart_web           - Restart web deployment"
    echo ""
    echo "Images:"
    echo "  build_and_push [tag]  - Build and push Docker image"
    echo "  list_images           - List images in Artifact Registry"
    echo ""
    echo "Debug:"
    echo "  get_all               - Get all resources"
    echo "  get_errors            - Get recent errors from logs"
    echo "  shell_web             - Shell into web pod"
    echo "  shell_db              - Shell into postgres pod"
    echo "  psql_connect          - Connect to postgres"
    echo ""
    echo "Monitoring:"
    echo "  watch_pods            - Watch pod status"
    echo "  get_usage             - Get resource usage"
    echo "  get_events            - Get recent events"
    echo ""
    echo "Secrets:"
    echo "  update_django_secret  - Generate new Django secret"
    echo "  update_db_password    - Generate new DB password"
}

# Show help by default
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    show_help
fi
