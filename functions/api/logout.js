export async function onRequestPost() {
  return new Response(JSON.stringify({ ok: true }), {
    status: 200,
    headers: {
      "Content-Type": "application/json",
      // Max-Age=0 立即过期，清除 Cookie
      "Set-Cookie": "auth_token=; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=0",
    },
  });
}
