#!/bin/bash
# local-teardown.sh - Remove Todo App from Minikube
# Usage: ./scripts/local-teardown.sh [--stop-minikube]

set -e

echo "=========================================="
echo "  Todo App - Local Kubernetes Teardown"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

STOP_MINIKUBE=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --stop-minikube)
            STOP_MINIKUBE=true
            shift
            ;;
    esac
done

# Check if Minikube is running
if ! minikube status &> /dev/null; then
    echo -e "${YELLOW}Minikube is not running. Nothing to clean up.${NC}"
    exit 0
fi

# Uninstall Helm release
echo -e "\n${YELLOW}Uninstalling Helm release...${NC}"
if helm list -n todo-app | grep -q todo-app; then
    helm uninstall todo-app -n todo-app
    echo -e "${GREEN}✓${NC} Helm release uninstalled"
else
    echo "No Helm release found"
fi

# Delete secrets
echo -e "\n${YELLOW}Deleting secrets...${NC}"
kubectl delete secret todo-app-secrets -n todo-app --ignore-not-found=true
echo -e "${GREEN}✓${NC} Secrets deleted"

# Delete namespace
echo -e "\n${YELLOW}Deleting namespace...${NC}"
kubectl delete namespace todo-app --ignore-not-found=true
echo -e "${GREEN}✓${NC} Namespace deleted"

# Verify cleanup
echo -e "\n${YELLOW}Verifying cleanup...${NC}"
if kubectl get namespace todo-app &> /dev/null; then
    echo -e "${RED}WARNING: Namespace still exists, waiting for deletion...${NC}"
    kubectl wait --for=delete namespace/todo-app --timeout=60s || true
fi
echo -e "${GREEN}✓${NC} All resources cleaned up"

# Optionally stop Minikube
if [ "$STOP_MINIKUBE" = true ]; then
    echo -e "\n${YELLOW}Stopping Minikube...${NC}"
    minikube stop
    echo -e "${GREEN}✓${NC} Minikube stopped"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}  Teardown Complete!${NC}"
echo "=========================================="
echo ""
echo "To completely reset Minikube (delete cluster):"
echo "  minikube delete"
echo ""
