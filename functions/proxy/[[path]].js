const BLOCKED = [
  /^localhost$/i,
  /^127\./,
  /^192\.168\./,
  /^10\./,
  /^172\.(1[6-9]|2\d|3[01])\./,
  /^0\.0\.0\.0$/,
  /^::1$/,
  /^fc00:/i,
  /^fe80:/i,
];

function isPrivate(hostname) {
  return BLOCKED.some((r) => r.test(hostname));
}

class LinkRewriter {
  constructor(base, origin) {
    this.base = base;
    this.origin = origin;
  }

  rewrite(attr, el) {
    const val = el.getAttribute(attr);
    if (!val || val.startsWith("data:") || val.startsWith("#") || val.startsWith("javascript:")) return;

    let absolute;
    try {
      absolute = new URL(val, this.base).href;
    } catch {
      return;
    }

    el.setAttribute(attr, `${this.origin}/proxy/?target=${encodeURIComponent(absolute)}`);
  }

  element(el) {
    const tag = el.tagName.toLowerCase();
    if (tag === "a" || tag === "area") this.rewrite("href", el);
    if (tag === "form") this.rewrite("action", el);
    if (tag === "script" || tag === "img" || tag === "audio" || tag === "video" || tag === "source" || tag === "track") this.rewrite("src", el);
    if (tag === "link") this.rewrite("href", el);
    if (tag === "iframe" || tag === "frame") this.rewrite("src", el);
  }
}

export async function onRequest(context) {
  const url = new URL(context.request.url);
  const target = url.searchParams.get("target");

  if (!target) {
    return Response.json({ error: "missing ?target=" }, { status: 400 });
  }

  let targetUrl;
  try {
    targetUrl = new URL(target);
  } catch {
    return Response.json({ error: "invalid url" }, { status: 400 });
  }

  if (targetUrl.protocol !== "http:" && targetUrl.protocol !== "https:") {
    return Response.json({ error: "only http/https allowed" }, { status: 400 });
  }

  if (isPrivate(targetUrl.hostname)) {
    return Response.json({ error: "private/internal address blocked" }, { status: 403 });
  }

  const proxyReq = new Request(targetUrl.href, {
    method: context.request.method,
    headers: {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
      "Accept": context.request.headers.get("Accept") || "*/*",
      "Accept-Language": context.request.headers.get("Accept-Language") || "zh-CN,zh;q=0.9,en;q=0.8",
      "Accept-Encoding": "gzip, deflate, br",
      "Referer": targetUrl.origin,
    },
    body: ["GET", "HEAD"].includes(context.request.method) ? null : context.request.body,
    redirect: "follow",
  });

  let response;
  try {
    response = await fetch(proxyReq);
  } catch (e) {
    return Response.json({ error: `fetch failed: ${e.message}` }, { status: 502 });
  }

  const contentType = response.headers.get("Content-Type") || "";
  const isHtml = contentType.includes("text/html");

  const newHeaders = new Headers(response.headers);
  newHeaders.delete("Content-Security-Policy");
  newHeaders.delete("Content-Security-Policy-Report-Only");
  newHeaders.delete("X-Frame-Options");
  newHeaders.delete("X-Content-Type-Options");
  newHeaders.set("Access-Control-Allow-Origin", "*");

  if (isHtml) {
    const rewriter = new HTMLRewriter()
      .on("a, area, form, script, img, audio, video, source, track, link, iframe, frame",
        new LinkRewriter(targetUrl.origin, url.origin)
      );

    return rewriter.transform(
      new Response(response.body, { status: response.status, headers: newHeaders })
    );
  }

  return new Response(response.body, {
    status: response.status,
    headers: newHeaders,
  });
}
