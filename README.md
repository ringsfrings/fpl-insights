# Fantasy Premier League Insights Dashboard

This project is a fully containerized Fantasy Premier League (FPL) insights dashboard built with **Flask** and **React**, designed primarily to demonstrate a modern DevOps and DevSecOps workflow from local development to production deployment.

## 🔍 Features

- **Gameweek Overview** – Average/highest scores and chip usage for the current or upcoming gameweek
- **Price Changes** – Top player price increases and decreases
- **Differential Picks** – Low-ownership players with strong recent performance
- **Top Players** – High scorers by total points
- **Fixture Ticker** – Colour-coded fixture difficulty for the next six gameweeks
- **Upcoming Matches** – Kickoff times with timezone localization
- **Watchlist** – Track specific players across dashboards

The UI is minimal by design and built using a CDN-loaded front end with **React**, **TailwindCSS**, and **GSAP** animations.

---

## ⚙️ Running Locally

```bash
git clone https://github.com/ringsfrings/fpl-insights.git
cd fpl-insights
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python3 fpl/fpl_app.py
```

App available at `http://localhost:5000/`

---

## 🐳 Docker Workflow

```bash
 docker run -d --name fpl_app -p 5000:5000 --restart always ringsfrings/fpl-insights-app:latest
```

---

## 🧪 DevOps & DevSecOps Workflow

### 🔐 Secrets Management with Ansible Vault

Ansible Vault encrypts sensitive data (like sudo passwords). The deployment uses:

```bash
ansible-playbook -i ansible/inventory.ini ansible/playbooks/deploy.yml --vault-password-file ~/.vault_pass.txt
```

### 📦 GitHub Actions CI/CD

File: `.github/workflows/ci-cd.yml`

CI/CD pipeline includes:

- **Bandit** – SAST for Python code
- **Trivy** – Docker image scanning
- **Checkov** – Scanning Ansible roles for misconfigurations
- **Build & Push** – Docker image pushed to DockerHub
- **Deployment** – Ansible playbook executes against remote VM

### 🛠️ Ansible Automation

All provisioning and deployment are handled through Ansible, targeting a VM defined in `inventory.ini`:

```ini
[fpl_server]
192.168.238.131 ansible_user=bil ansible_ssh_private_key_file=~/.ssh/id_rsa
```

Playbook tasks:

- Install Docker Engine and dependencies
- Pull latest Docker image
- Remove existing container
- Run updated container

### 🖥️ VM-Based Deployment

This project avoids Terraform or cloud provisioning and focuses on deploying to a local VM (via VMware), ideal for lab setups or air-gapped environments.

---

## 🔄 Directory Structure

```bash
fpl_app/
├── Dockerfile
├── fpl/
│   ├── fpl_app.py
│   └── templates/
├── ansible/
│   ├── inventory.ini
│   ├── vault.yml (encrypted)
│   └── playbooks/
│       └── deploy.yml
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── terraform.tfstate (legacy)
├── main.tf (legacy)
└── README.md
```

---

## 📈 Future Improvements

- Add Prometheus/Grafana for monitoring & alerting
- Add persistent watchlist with user accounts
- Migrate deployment to cloud using Terraform with load balancing and autoscaling

---

## 👏 Acknowledgements

- Uses public FPL API for all data
- DevSecOps guided by community best practices for CI/CD

---

## 🧩 License

This project is open-source for educational and demonstration purposes.
