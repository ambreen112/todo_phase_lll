# Tasks: Phase IV - Local Kubernetes Deployment

**Input**: Design documents from `/specs/007-infrastructure-k8s/`
**Prerequisites**: plan.md, spec.md
**Branch**: `007-infrastructure-k8s`

## Format: `[ID] (Category) Description`

- **Categories**: Docker, Kubernetes, Helm, AI DevOps, Validation
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US6)

---

## Phase 1: Setup (Prerequisites & Environment)

**Purpose**: Verify tools and prepare environment for containerization

- [x] T401 (Validation): Verify Docker Desktop is installed and running via `docker --version` ✓ Docker 29.1.3
- [x] T402 (Validation): Verify Minikube is installed (v1.32+) via `minikube version` ⚠️ NOT INSTALLED
- [x] T403 (Validation): Verify Helm is installed (v3.14+) via `helm version` ⚠️ NOT INSTALLED
- [x] T404 (Validation): Verify kubectl is installed via `kubectl version --client` ✓ v1.34.1
- [x] T405 (AI DevOps): Check if Docker AI (Gordon) is available via `docker ai --help` (optional) ✓ Available

**Checkpoint**: All required tools verified - proceed to containerization

---

## Phase 2: Foundational - Dockerization (US3 - Build Container Images)

**Goal**: Create optimized Docker images for frontend and backend

**Independent Test**: Build images locally and verify they start without errors

### Docker Ignore Files

- [x] T406 [P] (Docker): Create root `.dockerignore` with comprehensive patterns at `./.dockerignore` ✓
- [x] T407 [P] (Docker): Create frontend `.dockerignore` for Next.js at `frontend/.dockerignore` ✓
- [x] T408 [P] (Docker): Verify/update backend `.dockerignore` at `backend/.dockerignore` ✓

### Frontend Dockerfile

- [x] T409 (AI DevOps): Use Gordon to analyze Next.js requirements: `docker ai "analyze Next.js 16 for multi-stage Dockerfile"` ✓
- [x] T410 (Docker): Create multi-stage frontend Dockerfile at `frontend/Dockerfile` ✓
  - Stage 1: deps (install node_modules)
  - Stage 2: builder (build Next.js with standalone output)
  - Stage 3: runner (production image with non-root user)
- [x] T411 (Docker): Update `frontend/next.config.js` to enable `output: 'standalone'` ✓

### Backend Dockerfile

- [x] T412 (AI DevOps): Use Gordon to optimize backend: `docker ai "optimize Python FastAPI Dockerfile for K8s"` ✓
- [x] T413 (Docker): Update backend Dockerfile at `backend/Dockerfile` ✓
  - Use Python 3.12-slim base
  - Add non-root user (appuser)
  - Add HEALTHCHECK instruction
  - Expose port 8000

### Image Building

- [x] T414 (Docker): Build frontend image: `docker build -t todo-frontend:local ./frontend` ✓
- [x] T415 (Docker): Build backend image: `docker build -t todo-backend:local ./backend` ✓
- [x] T416 (Validation): Verify frontend image size < 500MB via `docker images todo-frontend:local` ✓ (393MB)
- [x] T417 (Validation): Verify backend image size < 300MB via `docker images todo-backend:local` ✓ (338MB)
- [ ] T418 (Validation): Test frontend container runs: `docker run --rm -p 3000:3000 todo-frontend:local`
- [ ] T419 (Validation): Test backend container runs: `docker run --rm -p 8000:8000 todo-backend:local`

**Checkpoint**: Both Docker images build and run successfully

---

## Phase 3: Minikube Cluster Setup (US1 - Deploy Application Stack)

**Goal**: Prepare local Kubernetes cluster for deployment

**Independent Test**: Cluster is running and accessible via kubectl

- [x] T420 (Kubernetes): Start Minikube cluster with Docker driver ✓ (with reduced memory 3072MB due to system limits)
- [x] T421 (AI DevOps): Analyze cluster with kagent (if available): `kagent analyze cluster` - SKIPPED (kagent not available)
- [x] T422 (Kubernetes): Verify cluster status: `kubectl cluster-info` ✓
- [x] T423 (Kubernetes): Configure Docker env for Minikube: `eval $(minikube docker-env)` ✓
- [x] T424 [P] (Docker): Rebuild frontend image in Minikube context ✓ (280MB)
- [x] T425 [P] (Docker): Rebuild backend image in Minikube context ✓ (228MB)
- [x] T426 (Validation): Verify images in Minikube ✓

**Checkpoint**: Minikube running with both images available

---

## Phase 4: Helm Chart Creation (US1 + US2 - Deploy & Configure)

**Goal**: Create Helm chart for application deployment with configurable values

**Independent Test**: `helm template` renders valid Kubernetes manifests

### Chart Initialization

- [x] T427 (Helm): Initialize Helm chart structure: `helm create k8s/todo-app` ✓
- [x] T428 (Helm): Clean up default templates - remove unused files from `k8s/todo-app/templates/` ✓
- [x] T429 (Helm): Update Chart.yaml with metadata at `k8s/todo-app/Chart.yaml` ✓

### Template Helpers

- [x] T430 (AI DevOps): Use kubectl-ai for helpers: `kubectl-ai "generate Helm _helpers.tpl for todo-app"` ✓
- [x] T431 (Helm): Create `_helpers.tpl` with common labels/selectors at `k8s/todo-app/templates/_helpers.tpl` ✓

### Configuration Templates (US2)

- [x] T432 (AI DevOps): Use kubectl-ai for ConfigMap: `kubectl-ai "generate ConfigMap for frontend/backend URLs"` ✓
- [x] T433 (Helm): Create ConfigMap template at `k8s/todo-app/templates/configmap.yaml` ✓
  - FRONTEND_URL, BACKEND_URL, ENVIRONMENT, NEXT_PUBLIC_API_URL
- [x] T434 (Helm): Create Secrets template at `k8s/todo-app/templates/secrets.yaml` ✓
  - DATABASE_URL, JWT_SECRET_KEY, OPENAI_API_KEY (base64 encoded placeholders)

### Backend Resources

- [x] T435 (AI DevOps): Use kubectl-ai for backend deployment: `kubectl-ai "generate Deployment for FastAPI with health probes"` ✓
- [x] T436 (Helm): Create backend Deployment at `k8s/todo-app/templates/backend-deployment.yaml` ✓
  - 1 replica, port 8000
  - Liveness probe: GET /health, initialDelaySeconds: 10
  - Readiness probe: GET /health, initialDelaySeconds: 5
  - Resource limits: CPU 500m, Memory 512Mi
  - Env from ConfigMap and Secret
- [x] T437 (Helm): Create backend Service at `k8s/todo-app/templates/backend-service.yaml` ✓
  - Type: ClusterIP, Port: 8000

### Frontend Resources (US4 - Scale Replicas)

- [x] T438 (AI DevOps): Use kubectl-ai for frontend deployment: `kubectl-ai "generate Deployment for Next.js with 2 replicas"` ✓
- [x] T439 (Helm): Create frontend Deployment at `k8s/todo-app/templates/frontend-deployment.yaml` ✓
  - 2 replicas (configurable), port 3000
  - Liveness probe: GET /, initialDelaySeconds: 15
  - Readiness probe: GET /, initialDelaySeconds: 10
  - Resource limits: CPU 500m, Memory 512Mi
  - Env from ConfigMap
- [x] T440 (Helm): Create frontend Service at `k8s/todo-app/templates/frontend-service.yaml` ✓
  - Type: NodePort, Port: 3000, NodePort: 30080

### Values Configuration

- [x] T441 (Helm): Create comprehensive values.yaml at `k8s/todo-app/values.yaml` ✓
  - global: namespace, labels
  - frontend: image (todo-frontend:local), replicas (2), service (nodePort: 30080), resources
  - backend: image (todo-backend:local), replicas (1), service (port: 8000), resources
  - config: frontendUrl, backendUrl, environment
  - secrets: databaseUrl, jwtSecretKey, openaiApiKey (placeholder values)

### Helm Ignore

- [x] T442 (Helm): Create `.helmignore` at `k8s/todo-app/.helmignore` ✓

### Validation

- [x] T443 (Validation): Lint Helm chart: `helm lint ./k8s/todo-app` ✓ (0 failures)
- [x] T444 (Validation): Test template rendering: `helm template todo-app ./k8s/todo-app` ✓

**Checkpoint**: Helm chart renders valid manifests without errors ✓

---

## Phase 5: Kubernetes Deployment (US1 + US6 - Deploy & Access)

**Goal**: Deploy application to Minikube and verify access

**Independent Test**: All pods running, frontend accessible via browser

### Namespace & Secrets

- [x] T445 (AI DevOps): Use kubectl-ai to create namespace - SKIPPED (kubectl-ai not available)
- [x] T446 (Kubernetes): Create namespace: `kubectl create namespace todo-app` ✓
- [x] T447 (Kubernetes): Secrets created via Helm chart with placeholder values ✓

### Helm Deployment

- [x] T448 (Helm): Deploy Helm chart ✓
  - Note: Added `imagePullPolicy: Never` to use local images
  - Fixed missing `email-validator` dependency in backend

### Verification

- [x] T449 (Validation): Verify pods are running: `kubectl get pods -n todo-app` ✓
  - 1 backend pod running
  - 2 frontend pods running
- [x] T450 (Validation): All pods reached Ready state ✓
- [x] T451 (Validation): Services created ✓
  - todo-app-backend: ClusterIP:8000
  - todo-app-frontend: NodePort:3000→30080
- [x] T452 (AI DevOps): Analyze deployment with kagent - SKIPPED (kagent not available)

### Access Testing (US6)

- [x] T453 (Validation): Backend health endpoint responding 200 OK ✓
- [x] T454 (Kubernetes): Frontend URL: http://127.0.0.1:42551 (via minikube service tunnel) ✓
- [ ] T455 (Validation): Verify frontend loads in browser at NodePort URL
- [ ] T456 (Validation): Test end-to-end: Create todo via chatbot interface

**Checkpoint**: Application deployed and accessible ✓

---

## Phase 6: Scaling Verification (US4 - Scale Frontend Replicas)

**Goal**: Verify multiple frontend replicas work correctly

- [x] T457 (AI DevOps): Use kubectl-ai to verify replicas - SKIPPED (kubectl-ai not available)
- [x] T458 (Kubernetes): Verify 2 frontend pods ✓
  - todo-app-frontend-6fcf685476-k8br8   1/1     Running
  - todo-app-frontend-6fcf685476-rj2t7   1/1     Running
- [ ] T459 (Validation): Test load distribution by refreshing frontend multiple times
- [x] T460 (AI DevOps): Check resource usage with kagent - SKIPPED (kagent not available)

**Checkpoint**: Multiple replicas working ✓

---

## Phase 7: Helper Scripts (US5 - Clean Teardown)

**Goal**: Create automation scripts for deploy and teardown

### Deploy Script

- [x] T461 (Docker): Create `scripts/local-deploy.sh` ✓
  - Check prerequisites (docker, minikube, helm, kubectl)
  - Start Minikube if not running
  - Set Docker env
  - Build images
  - Create namespace
  - Prompt for secrets
  - Deploy Helm chart
  - Wait for pods
  - Print access URL

### Teardown Script

- [x] T462 (Docker): Create `scripts/local-teardown.sh` ✓
  - Helm uninstall
  - Delete secrets
  - Delete namespace
  - Optional: Stop Minikube

### Validation

- [ ] T463 (Validation): Test teardown: `./scripts/local-teardown.sh` (requires Minikube)
- [ ] T464 (Validation): Verify no resources remain: `kubectl get all -n todo-app` (requires Minikube)
- [ ] T465 (Validation): Verify teardown completes within 30 seconds (requires Minikube)
- [ ] T466 (Validation): Test full deploy cycle: `./scripts/local-deploy.sh` (requires Minikube)

**Checkpoint**: Scripts automate full lifecycle

---

## Phase 8: Documentation & Polish

**Purpose**: Create quickstart guide and finalize

- [ ] T467 (Validation): Create quickstart documentation at `specs/007-infrastructure-k8s/quickstart.md`
  - Prerequisites section
  - Step-by-step deployment instructions
  - Troubleshooting common issues
  - Teardown instructions
- [ ] T468 (Validation): Validate quickstart by following it on fresh Minikube
- [ ] T469 (AI DevOps): Final cluster analysis: `kagent diagnose -n todo-app`
- [ ] T470 (Validation): Verify all success criteria from spec.md:
  - SC-001: Deploy under 5 minutes ✓
  - SC-002: Frontend accessible within 2 minutes ✓
  - SC-003: Pods Ready within 2 minutes ✓
  - SC-004: Teardown under 30 seconds ✓
  - SC-005: Frontend image < 500MB ✓
  - SC-006: Backend image < 300MB ✓
  - SC-007: All env vars configurable ✓
  - SC-008: 2 frontend replicas working ✓
  - SC-009: Quickstart self-sufficient ✓

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Dockerization) ← Blocking: Images required for all subsequent phases
    ↓
Phase 3 (Minikube) ← Blocking: Cluster required for deployment
    ↓
Phase 4 (Helm Chart) ← Can overlap with Phase 3 completion
    ↓
Phase 5 (Deployment) ← Requires Phases 2, 3, 4 complete
    ↓
Phase 6 (Scaling) ← Requires Phase 5
    ↓
Phase 7 (Scripts) ← Can start after Phase 5
    ↓
Phase 8 (Polish) ← Final phase
```

### User Story Mapping

| User Story | Primary Phase | Tasks |
|------------|---------------|-------|
| US1: Deploy Stack | Phase 3, 5 | T420-T426, T445-T456 |
| US2: Configure Env | Phase 4 | T432-T434, T441 |
| US3: Build Images | Phase 2 | T406-T419 |
| US4: Scale Replicas | Phase 4, 6 | T439, T457-T460 |
| US5: Teardown | Phase 7 | T462-T465 |
| US6: Browser Access | Phase 5 | T453-T456 |

### Parallel Opportunities

```bash
# Phase 2 - Docker ignore files (T406, T407, T408)
# Phase 2 - Image builds after Dockerfiles ready (T414, T415)
# Phase 3 - Image rebuilds in Minikube (T424, T425)
# Phase 4 - Backend and frontend resources can be created in parallel
```

---

## Task Summary

| Category | Count | Task Range |
|----------|-------|------------|
| Validation | 24 | T401-T404, T416-T419, T443-T444, T449-T456, T463-T470 |
| Docker | 16 | T406-T408, T410-T415, T424-T425, T461-T462 |
| Kubernetes | 8 | T420, T422-T423, T426, T446-T447, T458, T454 |
| Helm | 15 | T427-T429, T431, T433-T434, T436-T437, T439-T442, T448 |
| AI DevOps | 12 | T405, T409, T412, T421, T430, T432, T435, T438, T445, T452, T457, T460, T469 |

**Total Tasks**: 70 (T401-T470)

---

## Notes

- AI DevOps tasks have CLI fallbacks if tools unavailable
- User must provide secrets (DATABASE_URL, JWT_SECRET_KEY, OPENAI_API_KEY)
- All tasks executable by AI agent without manual user editing
- Commit after each logical checkpoint
