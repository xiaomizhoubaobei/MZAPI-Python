#!/bin/bash

# 定义新的 APT 源配置
NEW_APT_SOURCES="
deb https://mirrors.cernet.edu.cn/ubuntu/ noble main restricted universe multiverse
deb-src https://mirrors.cernet.edu.cn/ubuntu/ noble main restricted universe multiverse
deb https://mirrors.cernet.edu.cn/ubuntu/ noble-updates main restricted universe multiverse
deb-src https://mirrors.cernet.edu.cn/ubuntu/ noble-updates main restricted universe multiverse
deb https://mirrors.cernet.edu.cn/ubuntu/ noble-backports main restricted universe multiverse
deb-src https://mirrors.cernet.edu.cn/ubuntu/ noble-backports main restricted universe multiverse

# 以下安全更新软件源包含了官方源与镜像站配置，如有需要可自行修改注释切换
deb https://mirrors.cernet.edu.cn/ubuntu/ noble-security main restricted universe multiverse
deb-src https://mirrors.cernet.edu.cn/ubuntu/ noble-security main restricted universe multiverse

deb http://security.ubuntu.com/ubuntu/ noble-security main restricted universe multiverse
deb-src http://security.ubuntu.com/ubuntu/ noble-security main restricted universe multiverse"

# 备份原始的 APT 源列表
sudo cp /etc/apt/sources.list /etc/apt/sources.list.bak

# 将新的 APT 源配置写入文件
echo "$NEW_APT_SOURCES" | sudo tee /etc/apt/sources.list

# 检查是否写入成功
if echo "$NEW_APT_SOURCES" | sudo tee /etc/apt/sources.list; then
    echo "APT 源配置更新成功"
    # 更新 APT 缓存
    sudo apt-get update
    # 删除备份文件
    sudo rm /etc/apt/sources.list.bak
else

    echo "APT源配置更新失败恢复原始配置"
    sudo mv /etc/apt/sources.list.bak /etc/apt/sources.list
    exit 1
fi