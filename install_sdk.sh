# 安装阿里云、腾讯云、华为云、百度云、OpenAI、字节跳动和京东云的Python SDK
# 确保pip已安装
if ! which pip; then
  python3 -m ensurepip --upgrade
fi

# 安装阿里云SDK
echo "正在安装阿里云SDK..."
git clone https://github.com/aliyun/alibabacloud-python-sdk.git
cd alibabacloud-python-sdk || exit
for dir in */
do
  dir_name=$(basename "$dir")
  if [[ "$dir_name" =~ ^alibabacloud_ ]]; then
    echo "正在安装SDK：$dir_name..."
    pip install "$dir_name" || exit 1
  fi
done

# 安装腾讯云SDK
echo "正在安装腾讯云SDK..."
pip install --upgrade tencentcloud-sdk-python || exit 1

# 安装华为云SDK
echo "正在安装华为云SDK..."
cd / # 回到根目录
git clone --depth 1 https://github.com/huaweicloud/huaweicloud-sdk-python-v3.git
cd huaweicloud-sdk-python-v3/huaweicloud-sdk-all || exit
for dir in */
do
  dir_name=$(basename "$dir")
  # 仅处理以huaweicloud开头的目录
  if [[ "$dir_name" =~ ^huaweicloud ]]; then
    # 替换-sdk-为sdk，去掉其他连字符
    install_name=$(echo "$dir_name" | sed -e 's/-sdk-/sdk/g' -e 's/-//g')
    echo "正在安装SDK：$install_name..."
    pip install "$install_name" || exit 1
  fi
done

# 安装百度云SDK
echo "正在安装百度云SDK..."
pip install bce-python-sdk || exit 1

# 安装OpenAI和其他库
echo "正在安装OpenAI和其他库..."
pip install openai qianfan || exit 1

# 安装字节跳动 SDK
echo "正在安装字节跳动 SDK..."
pip install volcengine-python-sdk || exit 1

# 安装京东云 SDK
echo "正在安装京东云 SDK..."
pip install -U jdcloud_sdk || exit 1

echo "所有SDK安装完成！"