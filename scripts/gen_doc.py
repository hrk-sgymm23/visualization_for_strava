import os
import subprocess
from datetime import datetime
from anytree import Node, RenderTree
from openai import OpenAI
from dotenv import load_dotenv

# ============================
# 🌍 実行環境の自動判別
# ============================
platform = os.getenv("PLATFORM")

if not platform:
    if os.getenv("GITHUB_ACTIONS") == "true":
        platform = "github"
    elif os.getenv("GITLAB_CI") == "true":
        platform = "gitlab"
    else:
        platform = "local"

print(f"🧭 実行環境を自動判別しました → PLATFORM={platform}")

# ============================
# 📦 環境変数読み込み
# ============================
if platform == "local":
    load_dotenv()
    print("🧪 .env から環境変数を読み込みました")
else:
    print(f"🚀 {platform} 環境で実行中（Secrets / CI Variables から取得）")

# ============================
# 🤖 OpenAI クライアント初期化
# ============================
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    raise RuntimeError("❌ OPENAI_API_KEY が見つかりません。環境変数または .env を確認してください。")

client = OpenAI(api_key=openai_key)


# 🌲 ディレクトリツリー構造を作成
def build_tree(base_dir="."):
    root = Node(".")
    nodes = {".": root}
    for dirpath, dirnames, filenames in os.walk(base_dir):
        if ".git" in dirpath or "wiki" in dirpath:
            continue
        rel_path = os.path.relpath(dirpath, base_dir)
        parent_path = os.path.dirname(rel_path)
        parent_node = nodes.get(parent_path if parent_path != "." else ".", root)
        current_node = Node(rel_path, parent=parent_node)
        nodes[rel_path] = current_node
        for f in filenames:
            Node(os.path.join(rel_path, f), parent=current_node)
    return root


# 📄 コード抜粋収集（多言語対応）
def collect_code_info():
    result = []
    target_exts = [
        ".py", ".sh", ".yaml", ".yml", ".json",
        ".js", ".ts", ".go", ".rb", ".java",
        ".tf", ".ini", ".cfg", ".toml", ".sql"
    ]

    for dirpath, _, filenames in os.walk("."):
        if ".git" in dirpath or "wiki" in dirpath:
            continue

        target_files = [f for f in filenames if any(f.endswith(ext) for ext in target_exts)]
        if not target_files:
            continue

        section = {"path": dirpath, "files": []}
        for f in target_files:
            path = os.path.join(dirpath, f)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as fp:
                    lines = fp.readlines()
                    head = lines[:60] if f.endswith((".yaml", ".yml", ".json", ".toml")) else lines[:40]
                    content = "".join(head)
            except Exception as e:
                content = f"[読み込みエラー: {e}]"

            section["files"].append({"name": f, "content": content})
        result.append(section)

    return result


# 🤖 AIでMarkdown生成
def summarize_with_ai(code_sections, tree_text):
    prompt = f"""
次のリポジトリ構造とコード抜粋をもとに、各ディレクトリの概要と主要関数をMarkdownでまとめてください。

# ディレクトリ構造
{tree_text}

# コード抜粋
{code_sections}
"""
    res = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        temperature=0.2
    )
    return res.output[0].content[0].text


# 📝 Wiki出力
def update_wiki(content, platform="local"):
    today = datetime.now().strftime("%Y-%m-%d")
    header = f"# 📘 Repository Structure Overview\n最終更新日: {today}\n\n---\n"
    filename = "Repository-Structure.md"

    if platform == "gitlab":
        wiki_dir = "wiki"
        wiki_url = (
            f"https://oauth2:{os.environ['GITLAB_TOKEN']}"
            f"@{os.environ['CI_SERVER_HOST']}/{os.environ['CI_PROJECT_PATH']}.wiki.git"
        )
        subprocess.run(["git", "clone", wiki_url, wiki_dir], check=True)
        output_path = os.path.join(wiki_dir, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(header + content)
        os.chdir(wiki_dir)
        subprocess.run(["git", "config", "user.name", "ci-bot"], check=True)
        subprocess.run(["git", "config", "user.email", "ci@example.com"], check=True)
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"Update repo structure doc ({today})"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ GitLab Wikiを更新しました。")

    elif platform == "github":
        wiki_dir = "wiki"
        token = os.environ["GITHUB_TOKEN"]
        repo = os.environ["GITHUB_REPOSITORY"]
        wiki_url = f"https://x-access-token:{token}@github.com/{repo}.wiki.git"

        subprocess.run(["git", "clone", wiki_url, wiki_dir], check=True)
        output_path = os.path.join(wiki_dir, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(header + content)
        os.chdir(wiki_dir)
        subprocess.run(["git", "config", "user.name", "ci-bot"], check=True)
        subprocess.run(["git", "config", "user.email", "ci@example.com"], check=True)
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"Update repo structure doc ({today})"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ GitHub Wikiを更新しました。")

    else:
        # ローカル出力
        output_path = filename
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(header + content)
        print(f"✅ ローカル出力完了: {output_path}")


# 🏃 メイン処理
def main():
    print(f"🚀 {platform} 環境でドキュメント生成を開始")
    tree = build_tree(".")
    tree_text = "\n".join([pre + f.name for pre, _, f in RenderTree(tree)])
    sections = collect_code_info()
    text_for_ai = "\n".join(
        [f"## {s['path']}\n" + "\n".join([f['name'] for f in s['files']]) for s in sections]
    )
    summary = summarize_with_ai(text_for_ai, tree_text)
    update_wiki(summary, platform)
    print("✅ Wiki更新完了")


if __name__ == "__main__":
    main()