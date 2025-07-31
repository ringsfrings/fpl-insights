# Fantasy Premier League Insights Dashboard

This project is a fully containerized Fantasy Premier League (FPL) insights dashboard built with **Flask** and **React**. It demonstrates a modern DevOps and DevSecOps workflow, from development to automated deployment on a self-hosted virtual machine (VM).

## 🔍 Features

- Gameweek Overview – Scores and chip usage
- Price Changes – Top risers and fallers
- Differential Picks – Low-ownership high performers
- Top Players – Based on total points
- Fixture Ticker – Difficulty color-coded
- Upcoming Matches – Localized kickoff times
- Watchlist – Track your chosen players

## ⚙️ Running Locally

```bash
git clone https://github.com/ringsfrings/fpl-insights.git
cd fpl-insights
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python3 fpl/fpl_app.py
```

## 🐳 Docker Workflow

```bash
docker run -d --name fpl_app -p 5000:5000 --restart always ringsfrings/fpl-insights-app:latest
```

## 🧪 DevOps & DevSecOps Workflow

This project uses GitHub Actions CI/CD pipeline with full security automation:

- **Docker Build & Push**: Builds and pushes image to DockerHub
- **Ansible Playbook**: Deploys containerized app to local VMware VM using Ansible
- **Secrets Management**: Ansible Vault handles sensitive info like SSH keys and sudo password
- **Checkov**: Scans Ansible playbooks for misconfigurations
- **Hadolint**: Lints Dockerfile for best practices
- **Trivy**: Scans Docker image for vulnerabilities
- **GitHub Self-Hosted Runner**: Installed and registered securely on the same VM as deployment target

## 🖥️ VM-Based Deployment

No cloud provider used. CI/CD deploys the app from GitHub to a local VM (Node-02) using a self-hosted runner with systemd-managed service. The runner triggers Ansible directly without needing manual SSH configuration.

## 🔄 Directory Structure

```
fpl-insights/
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
└── README.md
```

## 📈 Future Improvements

- Add Prometheus/Grafana for observability
- Extend CI/CD with test automation
- Add cloud deployment option via Terraform
- Integrate GitHub webhooks for real-time alerts

## 🧩 License

This project is open-source for educational and demonstration purposes.