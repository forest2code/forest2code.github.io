# forest2code.github.io

极简黑客风格的个人笔记与博客系统。

- **写作格式**：仅需在 `posts/` 目录下编写 Markdown 文件。
- **自动构建**：每次 `git push` 推送到 GitHub，GitHub Actions 会自动将其渲染为纯静态 HTML 并部署到 GitHub Pages。
- **功能特性**：
  - 原汁原味极简等宽终端风排版（`main-light.css` / `main-dark.css`）
  - 原生支持 **LaTeX 数学公式**（KaTeX 自动渲染，支持 `$行内公式$` 与 `$$块级公式$$`）
  - 原生支持 **代码语法高亮**（Pygments）
  - 自动生成首页按日期倒序的文章列表与 `/archive` 年份归档

---

## 📝 日常如何记笔记？

在 `posts/` 目录下新建一个 `.md` 文件（如 `posts/2024-02-01-my-note.md`）：

```markdown
---
title: 笔记标题
date: 2024-02-01
---

这里编写 Markdown 内容。

支持代码块与高亮：
```python
def hello():
    print("hello world")
```

支持数学公式：
$$\lim_{x \to 0} \frac{\sin x}{x} = 1$$
```

写完后提交并推送到 GitHub 即可：
```bash
git add .
git commit -m "add new note"
git push
```
云端 GitHub Actions 会在 1 分钟内自动编译发布！

---

## 💻 本地预览（可选）

如果想在本地先看一眼渲染效果，只需在终端运行：

```bash
# 安装依赖（首次运行需要）
pip install -r requirements.txt

# 构建并启动本地预览服务器
python build.py --serve
```
然后在浏览器打开 `http://localhost:8000` 即可实时预览。

---

## ⚙️ GitHub Pages 仓库设置（仅需检查一次）

在你的 GitHub 仓库中：
1. 点击 **Settings** -> **Pages**
2. 在 **Build and deployment** 下的 **Source** 中，选择 **GitHub Actions**
3. 以后每次 push 就会自动运行构建并部署上线。
