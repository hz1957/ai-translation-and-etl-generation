import subprocess
import os
import tempfile

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FILES_DIR = os.path.join(PROJECT_ROOT, "knowledge_base")

def run_playwright_test(json_filename: str, test_file: str = "upload_json_file.spec.js") -> str:
    """
    Execute a Playwright test script with a specified JSON configuration file.

    This function reads a Playwright test script, replaces a placeholder with the path
    to the specified JSON file, creates a temporary copy of the modified script, runs
    the test, and then cleans up the temporary file.

    Args:
        json_filename (str): The name of the JSON file to use in the test, located in the files directory
        test_file (str, optional): The name of the Playwright test file to use. Defaults to "upload_json_file.spec.js"

    Returns:
        str: The stdout output from the Playwright test if successful, or stderr/error message if failed

    Raises:
        subprocess.CalledProcessError: If the Playwright test fails
        FileNotFoundError: If the npx command or specified files are not found
    """
    temp_file_path = None
    try:
        # 绝对路径
        test_file_path = os.path.join(FILES_DIR, test_file)
        json_file_path = os.path.join(FILES_DIR, json_filename)

        # 读取原始脚本
        with open(test_file_path, 'r', encoding='utf-8') as f:
            script_content = f.read()

        # 替换占位符
        modified_content = script_content.replace('__JSON_FILE_PLACEHOLDER__', json_file_path)

        # 写到 files 目录下的临时文件（这样 cwd 也在 files 下）
        temp_fd, temp_file_path = tempfile.mkstemp(dir=FILES_DIR, suffix=".spec.js")
        with os.fdopen(temp_fd, 'w', encoding='utf-8') as temp_f:
            temp_f.write(modified_content)

        print(f"Created temporary script: {temp_file_path}")

        # 执行 Playwright
        command = ["npx", "playwright", "test", os.path.basename(temp_file_path)]
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            cwd=FILES_DIR, # 让 Playwright 在 files 下找测试文件
            timeout=20
        )
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        return e.stderr.strip()
    except FileNotFoundError:
        return "Command 'npx' not found or file not found."
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            print(f"Removed temporary script: {temp_file_path}")


# def main():
#     # 示例调用
#     result = run_playwright_test(json_filename="fixed_etl_config.json")
#     print(result)

# if __name__ == "__main__":
#     main()