class Verification:
    @staticmethod
    def   sanitize_log_data(data, max_length=100):
        """处理日志中的敏感数据
        1. 如果是Base64数据，只显示最后10个字符并标记
        2. 长字符串自动截断并标记
        :param data: 需要处理的数据
        :param max_length: 最大长度，超过该长度将被截断
        """
        if data is None:
            return None
        if isinstance(data, str):
            if len(data) > max_length and 'base64' in data.lower():
                # 处理Base64数据
                return data[-20:] if len(data) > 100 else data[-10:]
            elif len(data) > max_length:
                # 处理长字符串
                if isinstance(data, str):
                    truncated = data[:max_length]
                    # 确保截断不会破坏UTF-8字符
                    while len(truncated.encode('utf-8')) > max_length:
                        truncated = truncated[:-1]
                    return truncated
                return data
        return data