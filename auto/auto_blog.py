import os
import re
import subprocess
import datetime
import shutil
import hashlib
import time
import json

# 路径配置
HEX0_PATH = r"E:\my_japan_blog"
PUBLIC_SRC = os.path.join(HEX0_PATH, "public")
PUBLIC_DST = r"E:\my_japan_blog_pv"
POST_PATH = os.path.join(HEX0_PATH, "source", "_posts")

PROMPT_REVIEW = os.path.join(HEX0_PATH, "auto", "prompt_product_review_v3.txt")
WEB_INTEL_FILE = os.path.join(HEX0_PATH, "auto", "web_intel_today.json")


# -----------------------------
# 工具函数
# -----------------------------
def slugify(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()[:10]


def run_cmd(cmd, cwd=None):
    print(f"[CMD] {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    if result.returncode != 0:
        raise RuntimeError(f"命令执行失败：{cmd}")


def strip_json_fences(text):
    match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if match:
        return match.group(1).strip()
    return text.strip()


# -----------------------------
# ① 加载手动选品 JSON
# -----------------------------
def load_web_intel():
    if not os.path.exists(WEB_INTEL_FILE):
        raise FileNotFoundError("web_intel_today.json 不存在，请先手动生成")

    if os.path.getsize(WEB_INTEL_FILE) == 0:
        raise ValueError("web_intel_today.json 是空文件")

    with open(WEB_INTEL_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            raise ValueError("web_intel_today.json 内容不是合法 JSON")

    return data["selected_products"]


# -----------------------------
# ② 构建价格上下文
# -----------------------------
def build_price_context(p):
    return (
        f"商品名称：{p['name']}｜"
        f"中国新品价格（CNY）：{p['price_cn_new']}｜"
        f"日本新品价格（JPY）：{p['price_jp_new']}｜"
        f"中国二手价格（CNY）：{p['price_cn_used']}｜"
        f"日本二手价格（JPY）：{p['price_jp_used']}｜"
        f"中国新品链接：{p['link_cn_new']}｜"
        f"日本新品链接：{p['link_jp_new']}｜"
        f"中国二手链接：{p['link_cn_used']}｜"
        f"日本二手链接：{p['link_jp_used']}｜"
        f"中日价差比例（约）：{p['price_diff_ratio']}｜"
        f"热度（CN）：{p['hot_cn']}，热度（JP）：{p['hot_jp']}"
    )


# -----------------------------
# ③ 调用 deepseek / qwen / gpt（你自己选择）
# -----------------------------
def call_llm_with_price(product_info):
    price_ctx = build_price_context(product_info)
    review_prompt = open(PROMPT_REVIEW, "r", encoding="utf-8").read()
    full_prompt = review_prompt + "\n\n" + price_ctx

    # 你可以替换成任何模型，例如：
    # ["ollama", "run", "qwen2:7b"]
    # ["ollama", "run", "deepseek-v3.1"]
    # ["ollama", "run", "gpt-4.1-mini"]
    process = subprocess.Popen(
        ["ollama", "run", "qwen2:7b"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )

    raw_output, err = process.communicate(full_prompt)

    if process.returncode != 0:
        print(f"[ERROR] 文章生成失败：{err}")
        raise RuntimeError(f"LLM 调用失败：{product_info['name']}")

    return raw_output


# -----------------------------
# ④ Mermaid 图表
# -----------------------------
def append_mermaid_chart(content, p):
    chart = (
        "```mermaid\n"
        "graph LR\n"
        f"    CN_NEW[中国新品 {p['price_cn_new']} CNY] -->|对比| JP_NEW[日本新品 {p['price_jp_new']} JPY]\n"
        f"    CN_USED[中国二手 {p['price_cn_used']} CNY] -->|对比| JP_USED[日本二手 {p['price_jp_used']} JPY]\n"
        "```"
    )
    return content + "\n\n---\n\n## 中日价格对比图（Mermaid）\n\n" + chart


# -----------------------------
# ⑤ 写入 Hexo 文章
# -----------------------------
def write_post_file(product_info, content):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    slug = slugify(product_info["name"] + today)
    filename = f"{today}-{slug}.md"
    filepath = os.path.join(POST_PATH, filename)

    content = content.replace("{{SLUG}}", slug)
    content = append_mermaid_chart(content, product_info)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[WRITE] 文章已生成：{filepath}")
    return filepath


# -----------------------------
# ⑥ Hexo 构建 + Git 推送
# -----------------------------
def build_hexo():
    print("\n=== 构建 Hexo ===")
    run_cmd("hexo clean", cwd=HEX0_PATH)
    run_cmd("hexo g", cwd=HEX0_PATH)


def sync_public():
    print("\n=== 同步 public ===")
    if os.path.exists(PUBLIC_DST):
        shutil.rmtree(PUBLIC_DST)
    shutil.copytree(PUBLIC_SRC, PUBLIC_DST)
    print("[SYNC] Done.")


def git_push():
    print("\n=== 推送 GitHub ===")
    run_cmd("git add .", cwd=PUBLIC_DST)
    run_cmd(f'git commit -m "Auto update {datetime.datetime.now()}"', cwd=PUBLIC_DST)
    run_cmd("git push", cwd=PUBLIC_DST)


# -----------------------------
# 主流程
# -----------------------------
def main():
    print("=== 手动选品模式：生成文章 → 构建博客 ===")

    products = load_web_intel()

    for p in products:
        print(f"\n=== 生成文章：{p['name']} ===")
        article = call_llm_with_price(p)
        write_post_file(p, article)
        time.sleep(2)

    build_hexo()
    sync_public()
    git_push()

    print("\n=== 全流程完成 ===")


if __name__ == "__main__":
    main()
