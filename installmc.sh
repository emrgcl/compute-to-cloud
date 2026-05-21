#!/bin/bash
set -euo pipefail

# ====== Config ======
MC_VERSION="1.21.4"          # Minecraft version to install
MC_USER="minecraft"          # System user to run the server
MC_DIR="/opt/minecraft"      # Install directory
MC_RAM="2G"                  # RAM allocation (adjust to your server)
# =====================

# Must run as root
if [[ $EUID -ne 0 ]]; then
  echo "Please run as root (use sudo)." >&2
  exit 1
fi

echo "==> Updating packages and installing dependencies..."
apt-get update
# Minecraft 1.21.x needs Java 21
apt-get install -y openjdk-21-jre-headless wget curl screen

echo "==> Creating service user '$MC_USER'..."
if ! id "$MC_USER" &>/dev/null; then
  useradd -r -m -d "$MC_DIR" -s /bin/bash "$MC_USER"
fi
mkdir -p "$MC_DIR"

echo "==> Fetching server download URL for $MC_VERSION..."
# Resolve the version manifest -> version metadata -> server jar URL
MANIFEST=$(curl -s https://launchermeta.mojang.com/mc/game/version_manifest.json)
VERSION_URL=$(echo "$MANIFEST" | grep -o "\"id\": \"$MC_VERSION\"[^}]*}" | grep -o 'https://[^"]*')

if [[ -z "$VERSION_URL" ]]; then
  echo "Could not find version $MC_VERSION. Check the version number." >&2
  exit 1
fi

SERVER_JAR_URL=$(curl -s "$VERSION_URL" | grep -o '"server":[^}]*' | grep -o 'https://[^"]*\.jar')

echo "==> Downloading server.jar..."
wget -O "$MC_DIR/server.jar" "$SERVER_JAR_URL"

echo "==> Accepting EULA..."
echo "eula=true" > "$MC_DIR/eula.txt"

# Basic server.properties (created on first run too, but seed sensible defaults)
cat > "$MC_DIR/server.properties" <<EOF
motd=My Minecraft Server
max-players=20
online-mode=true
EOF

chown -R "$MC_USER:$MC_USER" "$MC_DIR"

echo "==> Creating systemd service..."
cat > /etc/systemd/system/minecraft.service <<EOF
[Unit]
Description=Minecraft Server
After=network.target

[Service]
User=$MC_USER
WorkingDirectory=$MC_DIR
ExecStart=/usr/bin/java -Xms$MC_RAM -Xmx$MC_RAM -jar $MC_DIR/server.jar nogui
Restart=on-failure
SuccessExitStatus=0 1

[Install]
WantedBy=multi-user.target
EOF

echo "==> Enabling and starting service..."
systemctl daemon-reload
systemctl enable minecraft
systemctl start minecraft

echo ""
echo "==> Done!"
echo "    Status:  systemctl status minecraft"
echo "    Logs:    journalctl -u minecraft -f"
echo "    Port:    25565 (open it in your firewall/security group)"
