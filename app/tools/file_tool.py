import subprocess
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FILES_DIR = os.path.join(PROJECT_ROOT, "knowledge_base")


def read_file(filename: str) -> str:
    """
    Read file content from the files directory while preventing directory traversal.

    This function safely reads a file from the designated files directory by validating
    that the requested file path is within the allowed directory structure.

    Args:
        filename (str): The filename relative to the files directory

    Returns:
        str: The file content if successful, or an error message string if failed

    Raises:
        Exception: If there's an error reading the file (permissions, encoding, etc.)
    """
    if not filename:
        return "Error: filename is empty."
    
    file_path = os.path.abspath(os.path.join(FILES_DIR, filename))
    if not file_path.startswith(FILES_DIR):
        return "Error: Access denied. Attempted directory traversal."
    
    if not os.path.exists(file_path):
        return f"Error: File '{filename}' does not exist."
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading file '{filename}': {str(e)}"

def store_file(path: str, content: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"File saved to {path}"

# def main():
#     # 示例调用
#     content = read_file("观远数据ETL_JSON节点说明文档.md")
#     print(content)
# if __name__ == "__main__": 
#     main()
#     # 取消注释以运行示例