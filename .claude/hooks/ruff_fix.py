# PostToolUse で渡される JSON を stdin から受け取り、
# 編集した .py ファイルを抽出して Ruff --fix をかける。
#
# - すべて修正できれば exit 0
# - 修正後も違反が残れば exit 2（Claude に自動修正を依頼）

import json
import subprocess
import sys

data = json.load(sys.stdin)
tool_input = data.get("tool_input", {})

paths = []
if isinstance(tool_input.get("file_path"), str):
    paths.append(tool_input["file_path"])
if isinstance(tool_input.get("file_paths"), list):
    paths.extend(tool_input["file_paths"])

py_files = [p for p in paths if p.endswith(".py")]
if not py_files:
    sys.exit(0)  # 対象なし

failed = []
for path in py_files:
    # uv run ruff check --fix <file>
    result = subprocess.run(
        ["uv", "run", "ruff", "check", "--fix", path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if result.returncode != 0:  # 0: OK, 1:違反残り、2/123 等:設定エラー
        failed.append((path, result.stdout))

if not failed:
    sys.exit(0)  # 全部 OK

# ここに来たら Ruff が修正し切れなかった or 設定エラー
# Claude にフィードバックするため stderr に詳細を流して exit 2
for path, log in failed:
    print(
        f"それぞれの問題に対してどのような選択肢があるかを考えて、適切に修正してください。Ruff のエラー内容: {path}:{log}",
        file=sys.stderr,
    )

sys.exit(2)
