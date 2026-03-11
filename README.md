# 三引擎搜索聚合器（Streamlit）

这是一个基于 Streamlit 的搜索聚合网站：
- 支持 **百度 / 必应 / Google** 并排展示搜索结果。
- 支持 **单引擎搜索** 与 **三引擎同时搜索** 两种模式。
- 点击任意搜索结果标题即可跳转到对应页面。

## 本地运行

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

默认访问：`http://localhost:8501`

## 功能说明

- 侧边栏可切换模式：
  - `单引擎`
  - `三引擎同时搜索`
- 可设置每个引擎显示结果数量。
- 主页面输入关键词后点击“开始搜索”。

## 部署到 Streamlit Community Cloud

1. 将项目推送到你的 GitHub 仓库。
2. 打开 [https://share.streamlit.io/](https://share.streamlit.io/)。
3. 选择仓库、分支和入口文件 `streamlit_app.py`。
4. 点击 Deploy，即可获得公开访问链接。

## 开源建议

- 建议添加 `LICENSE`（如 MIT License）。
- 建议补充 `CONTRIBUTING.md` 说明贡献流程。
- 可配置 GitHub Actions 做基础 CI（例如语法检查）。

## 注意事项

搜索引擎页面结构可能变化，且可能触发反爬策略（验证码/封锁），会导致部分结果抓取失败。代码中已加入基本异常提示。
