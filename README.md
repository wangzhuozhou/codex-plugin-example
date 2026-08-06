# Codex Plugin 完整示例

这是一个可以发布到 GitHub，并通过 Codex Marketplace 安装的完整示例仓库。

仓库内包含 wechat-article-reviewer 插件。它提供一个 review-wechat-article Skill，用于审校中文公众号文章，检查事实边界、结构、表达和作者辨识度。

## 仓库结构

~~~text
codex-plugin-example/
├── .agents/plugins/marketplace.json
├── .github/workflows/validate.yml
├── plugins/
│   └── wechat-article-reviewer/
│       ├── .codex-plugin/plugin.json
│       └── skills/
│           └── review-wechat-article/
│               ├── SKILL.md
│               └── references/review-rubric.md
├── scripts/validate.py
├── tests/test-cases.md
├── CHANGELOG.md
├── LICENSE
└── README.md
~~~

## 第一步：修改发布者信息

发布前，打开 plugins/wechat-article-reviewer/.codex-plugin/plugin.json，将 Your Name、your-github-name 和示例仓库地址替换成你的信息。

插件目录名、Marketplace 中的 name 和 plugin.json 中的 name 必须保持一致。

## 第二步：本地校验

在仓库根目录运行：

~~~bash
python3 scripts/validate.py
~~~

通过时会显示：

~~~text
Validation passed: wechat-article-reviewer 0.1.0
~~~

GitHub Actions 也会在每次推送和 Pull Request 时执行相同校验。

## 第三步：发布到 GitHub

先在 GitHub 创建名为 codex-plugin-example 的空仓库，然后在本目录运行：

~~~bash
git init
git add .
git commit -m "Initial Codex plugin"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_NAME/codex-plugin-example.git
git push -u origin main
~~~

也可以使用 GitHub CLI：

~~~bash
gh repo create codex-plugin-example --public --source=. --remote=origin --push
~~~

## 第四步：从 GitHub 安装

添加 GitHub Marketplace：

~~~bash
codex plugin marketplace add YOUR_GITHUB_NAME/codex-plugin-example
~~~

安装插件：

~~~bash
codex plugin add wechat-article-reviewer@example-codex-plugins
~~~

也可以启动 Codex CLI，输入 /plugins，切换到 Example Codex Plugins 后安装。安装后请新建任务或 CLI 会话，让 Codex 重新加载插件。

## 第五步：调用 Skill

显式调用示例：

~~~text
$wechat-article-reviewer:review-wechat-article

请审校下面这篇公众号文章，先评分，再指出最需要修改的三处：
……文章正文……
~~~

Codex 也可以根据 Skill 的描述自动判断是否调用它。

## 发布新版本

1. 修改插件内容。
2. 更新 plugin.json 中的 version。
3. 更新 CHANGELOG.md。
4. 重新运行校验。
5. 提交并创建 Git 标签。

~~~bash
git add .
git commit -m "Release 0.2.0"
git tag v0.2.0
git push origin main --tags
~~~

使用者可以刷新 Marketplace：

~~~bash
codex plugin marketplace upgrade example-codex-plugins
~~~

## 扩展方向

这个示例是 Skill-only 插件，因此不需要服务器或 API Key。后续可以增加：

- .mcp.json：打包本地 MCP Server。
- .app.json：关联已注册的远程 MCP 服务。
- hooks/hooks.json：增加生命周期检查。
- assets/：增加图标、Logo 和插件截图。

只有在对应文件真实存在时，才应在 plugin.json 中声明它们。

## GitHub 发布与官方上架

发布到 GitHub 后，知道仓库地址的人可以添加并安装它；这不等于进入 OpenAI 公共插件目录。公开目录需要另外通过 OpenAI 插件提交入口接受审核。

## 许可证

本示例使用 MIT License。
