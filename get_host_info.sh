#!/usr/bin/env bash
# =============================================================================
# get_host_info.sh — 查询主机名和 IP 地址
# 兼容 Linux (GNU) 和 macOS (BSD) 环境
# =============================================================================

set -euo pipefail

# --- 颜色输出 (可选) ----------------------------------------------------------
if [[ -t 1 ]]; then
  BOLD='\033[1m'
  GREEN='\033[0;32m'
  CYAN='\033[0;36m'
  RESET='\033[0m'
else
  BOLD='' GREEN='' CYAN='' RESET=''
fi

# --- 主机名 -------------------------------------------------------------------
echo -e "${BOLD}=== 主机名 ===${RESET}"
echo -e "  ${GREEN}$(hostname)${RESET}"
echo

# --- IP 地址 ------------------------------------------------------------------
echo -e "${BOLD}=== IP 地址 ===${RESET}"

# 检测操作系统
OS="$(uname -s)"

if [[ "$OS" == "Darwin" ]]; then
  # macOS: 用 ifconfig 枚举活跃接口的 IPv4 地址
  ifconfig -l | tr ' ' '\n' | while read -r iface; do
    addr=$(ifconfig "$iface" 2>/dev/null \
      | awk '/inet / {print $2}')
    if [[ -n "$addr" && "$addr" != "127.0.0.1" ]]; then
      printf "  ${CYAN}%-10s${RESET} %s\n" "${iface}:" "$addr"
    fi
  done
else
  # Linux: 优先用 ip 命令，回退到 ifconfig
  if command -v ip &>/dev/null; then
    ip -4 -o addr show | while read -r _ iface _ addr _; do
      addr="${addr%%/*}"
      if [[ "$addr" != "127.0.0.1" && -n "$iface" ]]; then
        printf "  ${CYAN}%-10s${RESET} %s\n" "${iface}:" "$addr"
      fi
    done
  elif command -v ifconfig &>/dev/null; then
    ifconfig | awk '
      /^[a-zA-Z0-9]/ { iface=$1; gsub(/:$/, "", iface) }
      /inet /        { addr=$2; if (addr != "127.0.0.1") printf "  %-10s %s\n", iface":", addr }
    '
  else
    echo "  无可用网络工具 (ip/ifconfig 均未找到)" >&2
    exit 1
  fi
fi

echo
echo -e "${BOLD}=== 公网 IP (可选) ===${RESET}"
# 尝试通过外部服务获取公网出口 IP (超时 3 秒,静默失败)
pub_ip=$(curl -s --connect-timeout 3 --max-time 5 \
  ifconfig.me 2>/dev/null || true)
if [[ -n "$pub_ip" ]]; then
  echo -e "  ${GREEN}${pub_ip}${RESET}"
else
  echo "  (无法获取公网 IP)"
fi
