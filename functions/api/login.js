export async function onRequestPost(context) {
  const PASSWORD = context.env.PASSWORD || "admin123";

  let body;
  try {
    body = await context.request.json();
  } catch {
    return Response.json({ ok: false, msg: "invalid body" }, { status: 400 });
  }

  if (body.password !== PASSWORD) {
    return Response.json({ ok: false, msg: "wrong password" }, { status: 401 });
  }

  return new Response(JSON.stringify({ ok: true }), {
    status: 200,
    headers: {
      "Content-Type": "application/json",
      "Set-Cookie": `auth_token=${btoa(PASSWORD)}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=604800`,
    },
  });
}
