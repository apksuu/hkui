# Navigator Pro

一个多文件、纯静态的个人导航站项目。

## 特性

- 多视图布局：总览、网站库、收藏夹、最近打开、设置
- 原生 ES Modules 架构
- 大型站点库，适合搜索、过滤、排序、置顶、收藏测试
- 本地持久化，使用 `localStorage`
- 导入 / 导出 JSON 备份
- 命令面板与快捷键
- Open-Meteo 天气面板
- GitHub 用户资料面板
- 多主题切换

## 目录结构

```text
personal-nav-pro/
  index.html
  README.md
  assets/
    css/
      reset.css
      variables.css
      base.css
      layout.css
      components.css
      animations.css
      utilities.css
    js/
      app.js
      dom.js
      state.js
      storage.js
      utils.js
      api/
        weather.js
        github.js
      data/
        sites.js
        tips.js
      modules/
        notify.js
        modal.js
        theme.js
        renderers.js
        dashboard.js
        bookmarks.js
        commands.js
        settings.js
```

## 本地运行

直接双击 `index.html` 即可。

如果你想测试地理定位与更稳定的模块加载，建议使用本地静态服务器：

```bash
python -m http.server 8080
```

然后访问：

```text
http://localhost:8080
```

## 部署

上传整个目录到 GitHub Pages、Cloudflare Pages、Netlify 或任意静态托管服务即可。

## 定制

- 修改 `assets/js/data/sites.js` 可替换默认站点库
- 修改 `assets/css/variables.css` 可调整主题配色
- 修改 `assets/js/api/` 可接入更多公开 API
