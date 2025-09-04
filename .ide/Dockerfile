# 使用 Python 最新版本作为基础镜像
FROM docker.cnb.cool/examples/language/python-3:latest

# 安装 curl 和 apt-get 环境
RUN apt-get update && apt-get install -y curl wget unzip openssh-server sudo

# 安装 code-server 和 vscode 常用插件
RUN curl -fsSL https://code-server.dev/install.sh | sh \
  && code-server --install-extension cnbcool.cnb-welcome \
  && code-server --install-extension redhat.vscode-yaml \
  && code-server --install-extension dbaeumer.vscode-eslint \
  && code-server --install-extension waderyan.gitblame \
  && code-server --install-extension mhutchie.git-graph \
  && code-server --install-extension donjayamanne.githistory \
  && code-server --install-extension tencent-cloud.coding-copilot \
  && echo done


# 安装python依赖
RUN pip install -r yilai.txt

# 指定字符集支持命令行输入中文（根据需要选择字符集）
ENV LANG C.UTF-8
ENV LANGUAGE C.UTF-8