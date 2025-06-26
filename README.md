# Todo App

A full-stack, production-ready Todo application with React frontend and FastAPI backend. This project is fully containerized, supports authentication, monitoring, scaling, and is ready for both local development and cloud deployment.

---

## Features
- Add, view, update, and delete tasks
- Mark tasks as completed or pending
- JWT-based authentication (register/login, protected API)
- Prometheus monitoring (`/metrics` endpoint)
- Health check endpoint (`/healthz`)
- Persistent storage (SQLite, with Docker volume and Kubernetes PVC)
- Kubernetes manifests with autoscaling (HPA)
- Terraform scripts for AWS cloud infrastructure
- CI/CD pipeline (GitHub Actions)

---

## Getting Started Locally (Docker Compose)

1. **Clone the repository:**

   git clone <your-repo-url>
   cd todo-application


2. **Build and start the app:**

   docker-compose up --build

   - This will build and start both backend and frontend containers.
   - The backend will use a persistent SQLite DB in `backend/db`.

3. **Access the app:**
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Health: [http://localhost:8000/healthz](http://localhost:8000/healthz)
   - Metrics: [http://localhost:8000/metrics](http://localhost:8000/metrics)

4. **Stop the app:**
   Press `Ctrl+C` in the terminal, then run:

   docker-compose down


---

## Authentication Flow
- **Register:**

  curl -X POST "http://localhost:8000/register" -d "username=testuser&password=testpass" -H "Content-Type: application/x-www-form-urlencoded"

- **Login:**

  curl -X POST "http://localhost:8000/token" -d "username=testuser&password=testpass" -H "Content-Type: application/x-www-form-urlencoded"

  - Copy the `access_token` from the response.
- **Use the token:**
  - All `/tasks` endpoints require an `Authorization: Bearer <token>` header.

---

## Monitoring & Health
- **Health check:** [http://localhost:8000/healthz](http://localhost:8000/healthz)
- **Prometheus metrics:** [http://localhost:8000/metrics](http://localhost:8000/metrics)

---

## Troubleshooting
- If the frontend fails to connect to the backend (e.g., 502 or 401 errors):
  - Make sure both containers are running: `docker ps`
  - Ensure you are logged in and using a valid token for protected endpoints.
  - The Nginx config in the frontend is set to use `backend:8000` for Docker Compose.
- If the backend fails to start due to DB errors:
  - Ensure `backend/db` exists and is writable on your host.

---

## Kubernetes Deployment
- All manifests are in the `k8s/` directory.
- Includes Deployments, Services, PersistentVolumeClaim, and HorizontalPodAutoscaler (HPA) for both frontend and backend.
- To deploy:

  kubectl apply -f k8s/
  kubectl apply -f k8s/backend-hpa.yaml
  kubectl apply -f k8s/frontend-hpa.yaml

- Use port-forwarding or a LoadBalancer service to access the app.

---

## Cloud Infrastructure (Terraform)
- All scripts are in the `terraform/` directory.
- Provisions VPC, ECS, ECR, RDS, ALB, etc. on AWS.
- To use:

  cd terraform
  terraform init
  terraform plan
  terraform apply

- See `terraform/README.md` for details.

---

## What's Achieved
- **Full-stack app** with authentication, monitoring, and scaling
- **Containerized** for local and cloud use
- **Persistent storage** for backend data
- **Kubernetes-ready** with autoscaling
- **Cloud-ready** with Terraform
- **CI/CD pipeline** for automated builds and deployment
- **Comprehensive documentation**

---


---
