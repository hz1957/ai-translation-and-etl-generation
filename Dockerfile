# 使用 Python 3.11-slim 作为基础镜像
FROM python:3.11-slim

# 安装 Node.js 18.x
RUN apt-get update && \
    apt-get install -y curl gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制 package.json
COPY package.json ./

# 安装 Node.js 依赖 (including devDependencies for Playwright)
RUN npm install

# 安装 Playwright 浏览器（只安装 chromium 以减小镜像体积）
RUN npx playwright install chromium

# 将依赖文件复制到工作目录
COPY requirements.txt .

# 安装依赖，使用清华大学镜像源加速下载
# --no-cache-dir: 不保留缓存，减小镜像体积
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 将生产环境的配置文件复制到镜像中
COPY .env.prod /app/.env.prod

# 将应用代码复制到工作目录
COPY ./app /app/app
COPY ./static /app/static
COPY ./knowledge_base /app/knowledge_base

# 设置环境变量，指定为生产环境
# 这将使 app/config.py 加载 .env.prod 文件
ENV APP_ENV=prod

# 暴露5432端口，以便容器外部可以访问
EXPOSE 5432

# 容器启动时执行的命令
# 启动uvicorn服务器，监听所有网络接口的5432端口
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5432"]