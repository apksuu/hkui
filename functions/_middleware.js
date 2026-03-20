export async function onRequest(context) {
  const { request, next, env } = context;
  const url = new URL(request.url);
  const path = url.pathname;

  // 放行登录相关 + 所有静态资源
  if (
    path === "/login.html" ||
    path.startsWith("/api/") ||
    path.match(/\.(css|js|ico|png|jpg|svg|woff|woff2|ttf)$/)
  ) {
    return next();
  }

  const PASSWORD = env.PASSWORD || "admin123";
  const cookie = request.headers.get("Cookie") || "";
  const token = cookie.match(/auth_token=([^;]+)/)?.[1];

  if (!token || token !== btoa(PASSWORD)) {
    // 已经在 login.html 了就不要再跳，防止死循环
    if (path === "/login.html") return next();
    return Response.redirect(new URL("/login.html", request.url), 302);
  }

  return next();
}
