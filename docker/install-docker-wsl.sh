#!/usr/bin/env bash
# Install Docker Engine + Compose plugin inside an Ubuntu WSL2 distro.
# Run from an Ubuntu shell:
#   bash /mnt/c/Users/User/Work/c2java/docker/install-docker-wsl.sh
# Idempotent: safe to re-run.
set -euo pipefail

if [ ! -f /etc/os-release ] || ! grep -qi ubuntu /etc/os-release; then
  echo "error: this script expects Ubuntu" >&2
  exit 1
fi

echo "==> Enabling systemd for this WSL distro (needed for 'systemctl start docker')"
if ! grep -qs '^systemd=true' /etc/wsl.conf 2>/dev/null; then
  sudo tee /etc/wsl.conf >/dev/null <<'EOF'
[boot]
systemd=true
EOF
  NEEDS_WSL_RESTART=1
else
  NEEDS_WSL_RESTART=0
fi

echo "==> Adding Docker's official apt repository"
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null

echo "==> Installing Docker Engine, CLI, buildx and compose plugins"
sudo apt-get update
sudo apt-get install -y \
  docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo "==> Allowing $USER to use docker without sudo"
sudo usermod -aG docker "$USER"

sudo systemctl enable docker >/dev/null 2>&1 || true
sudo systemctl start  docker >/dev/null 2>&1 || sudo service docker start || true

echo
echo "==> Versions"
docker --version || true
docker compose version || true

echo
if [ "$NEEDS_WSL_RESTART" = "1" ]; then
  echo "systemd was just enabled and your user was added to the 'docker' group."
else
  echo "Your user was added to the 'docker' group."
fi
echo "Run this in Windows PowerShell to restart WSL, then re-open Ubuntu:"
echo
echo "    wsl --shutdown"
echo
echo "After that, verify with:  docker run --rm hello-world"
