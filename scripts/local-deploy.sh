#!/bin/bash
# local-deploy.sh - Deploy Todo App to Minikube
# Usage: ./scripts/local-deploy.sh

set -e

echo "=========================================="
echo "  Todo App - Local Kubernetes Deployment"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "\n${YELLOW}Checking prerequisites...${NC}"

check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}ERROR: $1 is not installed${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} $1 found"
}

check_command docker
check_command minikube
check_command helm
check_command kubectl

# Start Minikube if not running
echo -e "\n${YELLOW}Checking Minikube status...${NC}"
if ! minikube status &> /dev/null; then
    echo "Starting Minikube cluster..."
    minikube start --driver=docker --memory=4096 --cpus=2 --disk-size=20g
else
    echo -e "${GREEN}✓${NC} Minikube is already running"
fi

# Configure Docker to use Minikube's Docker daemon
echo -e "\n${YELLOW}Configuring Docker environment...${NC}"
eval $(minikube docker-env)
echo -e "${GREEN}✓${NC} Docker configured for Minikube"

# Build images
echo -e "\n${YELLOW}Building Docker images...${NC}"
echo "Building frontend image..."
docker build -t todo-frontend:local ./frontend
echo "Building backend image..."
docker build -t todo-backend:local ./backend
echo -e "${GREEN}✓${NC} Images built successfully"

# Create namespace
echo -e "\n${YELLOW}Creating namespace...${NC}"
kubectl create namespace todo-app --dry-run=client -o yaml | kubectl apply -f -
echo -e "${GREEN}✓${NC} Namespace ready"

# Check for secrets
echo -e "\n${YELLOW}Checking secrets...${NC}"
if ! kubectl get secret todo-app-secrets -n todo-app &> /dev/null; then
    echo -e "${RED}WARNING: Secrets not found!${NC}"
    echo ""
    echo "Please create secrets manually with your actual values:"
    echo ""
    echo "  kubectl create secret generic todo-app-secrets \\"
    echo "    --namespace todo-app \\"
    echo "    --from-literal=DATABASE_URL='your-database-url' \\"
    echo "    --from-literal=JWT_SECRET_KEY='your-jwt-secret' \\"
    echo "    --from-literal=OPENAI_API_KEY='your-openrouter-api-key'"
    echo ""
    read -p "Press Enter after creating secrets to continue, or Ctrl+C to abort..."
fi

# Deploy with Helm
echo -e "\n${YELLOW}Deploying with Helm...${NC}"
helm upgrade --install todo-app ./k8s/todo-app \
    --namespace todo-app \
    --set secrets.create=false \
    --set secrets.existingSecret=todo-app-secrets \
    --wait --timeout 5m

echo -e "${GREEN}✓${NC} Helm deployment complete"

# Wait for pods
echo -e "\n${YELLOW}Waiting for pods to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=todo-app -n todo-app --timeout=120s

# Get access URL
echo -e "\n${YELLOW}Getting access URL...${NC}"
FRONTEND_URL=$(minikube service todo-app-frontend -n todo-app --url 2>/dev/null || echo "")

echo ""
echo "=========================================="
echo -e "${GREEN}  Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "Pod Status:"
kubectl get pods -n todo-app
echo ""
echo "Services:"
kubectl get services -n todo-app
echo ""
if [ -n "$FRONTEND_URL" ]; then
    echo -e "Frontend URL: ${GREEN}${FRONTEND_URL}${NC}"
else
    echo "To get frontend URL, run:"
    echo "  minikube service todo-app-frontend -n todo-app --url"
fi
echo ""
echo "To open in browser:"
echo "  minikube service todo-app-frontend -n todo-app"
echo ""
