---
name: find-skills
description: >-
  用户说「怎么做 X」「有没有 X 的技能」「找个技能做 X」或想扩展能力时使用。用 skills.sh 与 npx skills find
  发现并安装专业技能。
---
# Find Skills

帮助发现并安装开源 agent skills 生态里的专业技能。

## 何时使用

- 用户问「怎么做 X」且 X 可能已有现成技能
- 用户说「找个技能做 X」「有没有技能可以…」
- 用户问「你会不会 X」而 X 是专项能力
- 用户想扩展能力、找工具/模板/工作流
- 用户提到设计、测试、部署等专业领域希望有现成包

## Skills CLI

`npx skills` 是开源 skills 的包管理器。

关键命令：

- `npx skills find [query] [--owner <owner>]` 按关键词搜索
- `npx skills add <source>` 从 GitHub 等安装
- `npx skills update` 更新已装技能
- `npx skills list` 列出已装技能

浏览：https://skills.sh/

## 步骤

### 1. 弄清需求

识别领域（如 React、测试、设计、部署）、具体任务，以及是否常见到可能已有技能。

### 2. 先看排行榜

先打开 https://skills.sh/ 看热门技能，再跑 CLI。常见来源：

- `vercel-labs/agent-skills`（React、Next.js、设计）
- `anthropics/skills`（前端设计、文档处理）

### 3. 搜索

```bash
npx skills find [query] [--owner <owner>]
```

示例：

- React 性能 → `npx skills find react performance`
- PR 评审 → `npx skills find pr review`
- changelog → `npx skills find changelog`

### 4. 推荐前先核质量

不要只凭搜索结果推荐。核对：

1. 安装量：优先 1K+，低于 100 要谨慎
2. 来源信誉：优先官方（vercel-labs、anthropics、microsoft）
3. GitHub stars：来源仓库过少 stars 要谨慎

### 5. 给用户选项

说明技能名与用途、安装量与来源、安装命令、skills.sh 链接。

示例：

```
找到可用技能 react-best-practices：Vercel 工程的 React/Next 性能指南（安装量见 skills.sh）。
安装：npx skills add vercel-labs/agent-skills@react-best-practices
详情：https://skills.sh/vercel-labs/agent-skills/react-best-practices
```

### 6. 用户同意后再装

在本机或机器人电脑上安装：

```bash
npx skills add <owner/repo@skill> -g -y
```

`-g` 装到用户级，`-y` 跳过确认。

若要给 Grok Bot 各机器人共用，在用户确认后：拉取该技能的 `SKILL.md`，用 UpdateSkill 写入用户技能库（scope user），并读回。不要未经确认批量安装未知技能。凭证、token 不进技能正文。

## 常见检索词

| 类别 | 示例 |
| --- | --- |
| Web | react, nextjs, typescript, css, tailwind |
| 测试 | testing, jest, playwright, e2e |
| DevOps | deploy, docker, kubernetes, ci-cd |
| 文档 | docs, readme, changelog, api-docs |
| 质量 | review, lint, refactor, best-practices |
| 设计 | ui, ux, design-system, accessibility |
| 效率 | workflow, automation, git |

## 搜不到时

1. 如实说没找到
2. 用现有能力直接帮
3. 可建议用户自建：`npx skills init my-xyz-skill`

来源参考：https://github.com/vercel-labs/skills/blob/main/skills/find-skills/SKILL.md
