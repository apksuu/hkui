export async function onRequest(context) {
  const { request, next, env } = context;
  const url = new URL(request.url);
  const path = url.pathname;

  // 放行：登录页、登录接口
  if (path === "/login.html" || path === "/api/login") {
    return next();
  }

  const PASSWORD = env.PASSWORD || "admin123";
  const cookie = request.headers.get("Cookie") || "";
  const token = cookie.match(/auth_token=([^;]+)/)?.[1];

  if (!token || token !== btoa(PASSWORD)) {
    return Response.redirect(new URL("/login.html", request.url), 302);
  }

  return next();
}
