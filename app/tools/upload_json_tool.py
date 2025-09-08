import subprocess
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FILES_DIR = os.path.join(PROJECT_ROOT, "knowledge_base")


def run_playwright_test(json_data: str, test_file: str = "upload_json_file.spec.js") -> str:
    """
    Execute a Playwright test script with JSON data passed as an environment variable.
    """
    try:
        # 设置环境变量传递JSON数据
        env = os.environ.copy()
        env['JSON_DATA'] = json_data

        # 执行 Playwright，传递环境变量
        command = ["npx", "playwright", "test", test_file]
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            cwd=FILES_DIR,  # 让 Playwright 在 files 下找测试文件
            env=env,
            timeout=20
        )
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        return e.stderr.strip()
    except FileNotFoundError:
        return "Command 'npx' not found or file not found."

# def main():
#     # 示例调用
#     result = run_playwright_test(json_data="1234567890")
#     print(result)

# if __name__ == "__main__":
#     main()