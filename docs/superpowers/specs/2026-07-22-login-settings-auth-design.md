# 登录页 / 个人设置页 / JWT 认证体系设计

日期：2026-07-22
状态：已获用户批准

## 背景

油擎智安（Vue 3 + Element Plus / FastAPI + SQLAlchemy + SQLite）现有 19 个业务页面，但：

- 登录页与个人设置页仅有设计稿（`picture/Stitch生成稿-高清/20-登录页.png`、`21-个人设置页.png`）与 HTML 原型（`docs/design-mockups/login.html`、`settings.html`），Vue 端无路由无组件。
- 后端零认证：无 JWT/session、无登录接口、无 User 表，所有 API 开放。
- `MainLayout.vue` 用户名硬编码，「个人中心」按钮与「退出登录」图标无行为。

## 决策（用户已确认）

1. **完整 JWT 认证**：User 表 + bcrypt 密码哈希 + JWT 登录接口 + 前端路由守卫 + API 鉴权依赖。
2. **UI 1:1 复刻设计稿**（与其余 19 页同标准），以 HTML 原型为实现基准。
3. **全部业务 API 纳入 JWT 保护**；保留「后端未启动时前端回退演示数据」机制。

## 方案选型

采用 **JWT 无状态认证 + 前端轻量 auth 模块**：

- 后端 `python-jose`（JWT）+ `passlib[bcrypt]`（密码哈希），FastAPI 依赖注入鉴权。
- 前端不引入 Pinia（避免过度设计），用 `src/auth.js` reactive 模块管理登录态；token 存 localStorage。
- 否决 Session/Cookie 方案（前后端分离 + CORS credentials 繁琐，SQLite 下需额外会话存储，收益低）。

## 数据库

`backend-python/app/db/models.py` 新增（沿用 Mapped/mapped_column 风格）：

```
users
  id            int PK
  username      str 唯一索引
  password_hash str
  name          str          # 显示名，如「安全管理员」
  role          str          # 如「系统管理员」
  email         str
  avatar_text   str          # 头像字，如「安」
  last_login_at datetime 可空
  last_login_ip str 可空
  preferences   Text(JSON)   # 主题/侧栏收起/通知开关/默认落地页
  created_at    datetime
```

- `seed.py` 播种默认账号 `admin / admin123`（README 注明仅供演示）。
- `config.py` 新增 `JWT_SECRET`、`JWT_EXPIRE_MINUTES`（默认 12h），`.env.example` 给占位；`.env` 可覆盖。

preferences JSON 结构：

```json
{
  "theme": "dark | light | auto",
  "sidebarCollapsed": false,
  "notifyRisk": true,
  "notifyDeviceOffline": true,
  "notifyApproval": false,
  "landingPage": "/workbench"
}
```

## 后端 API

新增 `app/api/auth.py` + `app/core/security.py`，统一 `{code,message,data}` 响应：

| 接口 | 说明 |
|---|---|
| `POST /api/auth/login` | 校验用户名密码；成功更新 last_login_at/ip、写一条 audit_logs（模块「用户登录」）、返回 `{token, user}` |
| `GET /api/auth/me` | 当前用户信息（含 preferences） |
| `PUT /api/auth/me` | 更新资料（name/email/avatar_text）与 preferences |
| `PUT /api/auth/password` | 校验旧密码后修改密码 |

鉴权：

- `security.py` 提供 `hash_password / verify_password / create_token / get_current_user`（HTTPBearer，解析 JWT → 查库返回 User，失败抛 401）。
- `main.py` 中 dashboard / sites / resources 路由统一挂 `dependencies=[Depends(get_current_user)]`；`/api/auth/login`、`/`、`/health` 开放。
- 401 走现有统一异常处理，返回 `{code:401,...}`。

## 前端

### 路由与守卫（`router/index.js`）

- 新增顶层路由 `/login`（不套 MainLayout）。
- MainLayout 下新增 `settings`（title「个人设置」，crumbs「个人中心 / 个人设置」）。
- 全局 beforeEach：无 token 且目标非 `/login` → 重定向 `/login`；已登录访问 `/login` → 跳 landingPage。

### 登录态模块（`src/auth.js`）

reactive 模块：`token`、`user`、`login()`、`logout()`、`loadMe()`、preferences 读写；token 与 user 持久化 localStorage。后端不可用时回退演示账号 `admin/admin123` 本地校验（与全站「回退演示数据」惯例一致）。

### LoginView.vue（1:1 复刻 login.html / 设计稿 20）

- 左 55% 品牌区：`login-bg.png` 背景 + 深色渐变叠层 + 青色网格线、品牌 logo、kicker 徽章、衬线大标语（「重新定义吊装安全的技术边界」）、三条特性卡。
- 右 45% 表单区：登录/注册胶囊 Tab（注册为展示态）、明暗主题切换按钮、账号/密码输入（focus 蓝色光圈、密码可见切换）、记住登录、忘记密码、渐变「立即登录 →」按钮、底部版权。
- 提交调 `POST /api/auth/login`，成功后跳 landingPage；失败 Element Plus 报错提示。

### SettingsView.vue（1:1 复刻 settings.html / 设计稿 21）

- 个人资料卡：72px 渐变大头像（角标相机）、姓名+角色徽章、email/上次登录/IP、「编辑资料」按钮（弹窗改 name/email）。
- 外观偏好：三张主题预览卡（夜间/日间/跟随系统）、「侧边栏默认收起」开关。
- 通知偏好：风险事件告警 / 设备离线提醒 / 审批待办提醒 三开关。
- 常规设置：默认落地页下拉、修改密码（弹窗，旧密码+新密码+确认）。
- 偏好变更即时 `PUT /api/auth/me` 保存（后端不可用则仅存 localStorage）。

### MainLayout.vue 改造

- 侧栏 user-box 与顶栏头像接入真实用户（name/role/avatar_text）。
- 顶栏头像点击弹下拉（按设计稿样式）：头部姓名+邮箱、「个人设置」→ `/settings`、「退出登录」（danger，清 token 跳 `/login`）。侧栏退出图标同样绑定登出。

### 主题体系（`styles/index.css`）

- 现有深色令牌归入 `[data-theme="dark"]`（默认），新增 `[data-theme="light"]` 令牌组（取自 settings.html：`--bg:#eef2f8`、`--panel:#ffffff` 等；侧边栏两主题下均保持深色）。
- Element Plus dark class 与 `data-theme` 联动；`auto` 跟随 `prefers-color-scheme`。
- 主题选择持久化于 preferences + localStorage，登录页也提供切换。

### request.js 整理

- 单行压缩代码整理为可读格式。
- 请求拦截器注入 `Authorization: Bearer <token>`；响应 401 → 清登录态并跳 `/login`。

## 错误处理

- 登录失败（用户名不存在/密码错）统一提示「账号或密码错误」。
- 改密旧密码错误 → 400 提示。
- 业务接口 401 → 前端拦截器统一登出跳转；各页面现有 try/catch 回退演示数据逻辑不变。

## 测试

pytest（沿用现有 tests/ 风格，测试库独立）：

1. 登录成功返回 token 与用户信息；密码错误返回失败 code。
2. 未带 token 访问受保护业务接口 → 401；带 token → 200。
3. `GET/PUT /api/auth/me` 读写资料与 preferences。
4. 改密流程：旧密码错拒绝；改密成功后新密码可登录。

## 范围外

- 真实注册流程（Tab 仅展示态）、忘记密码、角色权限控制（RBAC）、多用户管理页。
