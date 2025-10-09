import os
import subprocess
from datetime import datetime
from anytree import Node, RenderTree
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🌲 ツリー構造の生成
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

# 📄 コード抜粋収集
def collect_code_info():
    """
    複数言語対応のコードスキャン関数。
    各対象ファイルの先頭数行を抜粋してAIに渡す。
    """
    result = []
    # 対象拡張子の一覧
    target_exts = [
        ".py", ".sh", ".yaml", ".yml", ".json",
        ".js", ".ts", ".go", ".rb", ".java",
        ".tf", ".ini", ".cfg", ".toml", ".sql"
    ]

    for dirpath, _, filenames in os.walk("."):
        if ".git" in dirpath or "wiki" in dirpath:
            continue

        # 対象拡張子のファイルを抽出
        target_files = [f for f in filenames if any(f.endswith(ext) for ext in target_exts)]
        if not target_files:
            continue

        section = {"path": dirpath, "files": []}

        for f in target_files:
            path = os.path.join(dirpath, f)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as fp:
                    # 各ファイルの先頭数行だけを抜粋
                    lines = fp.readlines()
                    # 構成ファイルは多めに、コードは40行程度
                    head = lines[:60] if f.endswith((".yaml", ".yml", ".json", ".toml")) else lines[:40]
                    content = "".join(head)
            except Exception as e:
                content = f"[読み込みエラー: {e}]"

            section["files"].append({
                "name": f,
                "content": content
            })
        result.append(section)

    return result

# 🤖 AIでMarkdown生成
def summarize_with_ai(code_sections, tree_text):
    prompt = f"""
次のリポジトリ構造とコード抜粋をもとに、各ディレクトリの概要と主要関数をMarkdownでまとめてください。

# ディレクトリ構造


# コード抜粋
{code_sections}
"""
    res = client.responses.create(model="gpt-4.1-mini", input=prompt, temperature=0.2)
    return res.output[0].content[0].text

# 📝 Wiki出力
def update_wiki(content, platform="local"):
    """
    Wikiまたはローカルにドキュメントを出力する。
    platform:
      - "gitlab": GitLab Wikiにpush
      - "github": GitHub Wikiにpush
      - "local": ローカルにMarkdown出力（デフォルト）
    """
    today = datetime.now().strftime("%Y-%m-%d")
    header = f"# 📘 Repository Structure Overview\n最終更新日: {today}\n\n---\n"
    filename = "Repository-Structure.md"

    # 出力先切り替え（switch）
    if platform == "gitlab":
        wiki_dir = "wiki"
        wiki_url = (
            f"https://oauth2:{os.environ['GITLAB_TOKEN']}"
            f"@{os.environ['CI_SERVER_HOST']}/{os.environ['CI_PROJECT_PATH']}.wiki.git"
        )
        os.system(f"git clone {wiki_url} {wiki_dir}")
        output_path = os.path.join(wiki_dir, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(header + content)
        os.chdir(wiki_dir)
        os.system("git config user.name 'ci-bot'")
        os.system("git config user.email 'ci@example.com'")
        os.system(f"git add . && git commit -m 'Update repo structure doc ({today})' && git push")
        print("✅ GitLab Wikiを更新しました。")

    elif platform == "github":
        wiki_dir = "wiki"
        wiki_url = (
            f"https://{os.environ['GITHUB_TOKEN']}"
            f"@github.com/{os.environ['GITHUB_REPOSITORY']}.wiki.git"
        )
        os.system(f"git clone {wiki_url} {wiki_dir}")
        output_path = os.path.join(wiki_dir, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(header + content)
        os.chdir(wiki_dir)
        os.system("git config user.name 'ci-bot'")
        os.system("git config user.email 'ci@example.com'")
        os.system(f"git add . && git commit -m 'Update repo structure doc ({today})' && git push")
        print("✅ GitHub Wikiを更新しました。")

    else:
        # Local mode
        output_path = filename
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(header + content)
        print(f"✅ ローカル出力完了: {output_path}")

def main():
    platform = os.getenv("CI_PLATFORM", "gitlab")
    platform = "local"
    print(f"🚀 {platform}向けドキュメント生成開始")
    tree = build_tree(".")
    tree_text = "\n".join([pre + f.name for pre, _, f in RenderTree(tree)])
    sections = collect_code_info()
    text_for_ai = "\n".join([f"## {s['path']}\n" + "\n".join([f['name'] for f in s['files']]) for s in sections])
    summary = summarize_with_ai(text_for_ai, tree_text)
    update_wiki(summary, platform)
    print("✅ Wiki更新完了")

if __name__ == "__main__":
    main()
