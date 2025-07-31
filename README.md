# Fantasy Premier League Insights Dashboard

This project is a fully containerized Fantasy Premier League (FPL) insights dashboard built with **Flask** and **React**, designed to showcase a complete DevOps and DevSecOps pipeline using a self-hosted runner on a local VM (Node-02).

## 🔍 Features

- **Gameweek Overview** – Average/highest scores and chip usage
- **Price Changes** – Top player price movements
- **Differential Picks** – Low-ownership high-performers
- **Top Players** – Total points leaders
- **Fixture Ticker** – Fixture difficulty rating
- **Upcoming Matches** – Kickoff times with timezone support
- **Watchlist** – Track player stats

---

## ⚙️ Running Locally

```bash
git clone https://github.com/ringsfrings/fpl-insights.git
cd fpl-insights
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python3 fpl/fpl_app.py
```

Access the app at `http://localhost:5000/`

---

## 🐳 Docker Workflow

```bash
docker run -d --name fpl_app -p 5000:5000 --restart always ringsfrings/fpl-insights-app:latest
```

---

## 🧪 DevOps & DevSecOps Pipeline

### 🔐 Ansible Vault

Secrets like sudo password and SSH key paths are encrypted with:

```bash
ansible-playbook -i ansible/inventory.ini ansible/playbooks/deploy.yml --vault-password-file ~/.vault_pass.txt
```

### 🛠️ GitHub Actions CI/CD

Pipeline stages:

- Lint Dockerfile with **Hadolint**
- Scan Ansible with **Checkov**
- Scan Docker image with **Trivy**
- Build & push image to DockerHub
- SSH deploy using **Ansible** on a **self-hosted runner (Node-02)**

---

## 🤖 Self-Hosted Runner

The runner on the VM (Node-02) is configured using GitHub’s action runner binary and set up as a systemd service.

No manual intervention: All provisioning (Docker, image pulling, running) is handled **remotely from GitHub Actions** using:

```yml
ansible_user=bil
ansible_ssh_private_key_file=~/.ssh/id_rsa
```

## 🛡️ DevSecOps Tools

- **Hadolint** – Dockerfile static analysis
- **Checkov** – IaC scanning for Ansible
- **Trivy** – Docker image CVE scanning

---

## 📁 Structure

```
fpl-insights/
├── Dockerfile
├── fpl/
│   ├── fpl_app.py
│   └── templates/
├── ansible/
│   ├── inventory.ini
│   ├── vault.yml
│   └── playbooks/
│       └── deploy.yml
├── .github/
│   └── workflows/
│       └── ci-cd.yml
└── README.md
```

---

## 🚀 Future Work

- Add Prometheus/Grafana monitoring
- Integration testing via Pytest or UnitTest
- Real-time webhooks or Discord alerts
- Terraform-based cloud deployment

---

## 🧩 License

This project is open-source for educational and demonstration purposes.