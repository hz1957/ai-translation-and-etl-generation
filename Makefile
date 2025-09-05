.PHONY: setup dev test clean docker-build help

# 开发环境设置
setup:
	@echo "🚀 设置开发环境..."
	@if [ ! -f package.json ]; then npm init -y; fi
	@npm install --save-dev @playwright/test
	@npx playwright install chromium
	@pip install -r requirements.txt
	@echo "✅ 开发环境设置完成！"

# 启动开发服务器
dev:
	@echo "🔥 启动开发服务器..."
	@python run.py

# 运行测试
test:
	@echo "🧪 运行 Playwright 测试..."

# 清理缓存
clean:
	@echo "🧹 清理项目..."
	@rm -rf node_modules
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@rm -rf .pytest_cache
	@rm -rf test-results

# 构建 Docker 镜像
docker-build:
	@echo "🐳 构建 Docker 镜像..."
	@docker build -t model-platform .

# 显示帮助信息
help:
	@echo "可用命令:"
	@echo "  make setup        - 设置开发环境"
	@echo "  make dev          - 启动开发服务器"
	@echo "  make test         - 运行测试"
	@echo "  make clean        - 清理缓存"
	@echo "  make docker-build - 构建 Docker 镜像"