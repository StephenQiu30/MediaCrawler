# MediaCrawler 本地容器入口

`docker-compose.yml` 的 `crawler` 服务只按需运行，不配置开机自动采集。镜像安装与 `uv.lock` 对应的 Python 依赖和 Chromium，容器模式禁用宿主机 Chrome CDP，使用无头浏览器。

```bash
docker compose build crawler
docker compose run --rm crawler uv run --no-sync main.py --help
# 在获授权且已处理登录方式后，传入项目 main.py 的参数执行具体任务。
```

任务数据保存在原项目 `data/`；容器浏览器状态保存在独立的 `browser_data/docker/`，不会覆盖 macOS 上已有的 Chrome 或 MediaCrawler 浏览器目录。二维码、短信、验证码登录和具体平台采集尚需单独验收。HotKey 当前的 MediaCrawler 适配器仍使用宿主机子进程，本容器入口不代表 HotKey 已改为容器调用。

本项目许可证为非商业学习研究用途，使用时仍需遵守许可证及目标平台条款。
