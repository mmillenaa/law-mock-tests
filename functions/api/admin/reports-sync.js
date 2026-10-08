/*
 * Exportação privada de feedbacks
 * Cloudflare Pages + D1
 *
 * Rota: /api/admin/reports-sync
 */

export async function onRequestGet({ request, env }) {
  const headers = {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store, private",
    "X-Robots-Tag": "noindex, nofollow"
  };

  const respond = (data, status) =>
    new Response(JSON.stringify(data), { status, headers });

  const token = env.REPORTS_SYNC_TOKEN;

  if (!env.DB || !token || token.length < 32) {
    return respond({
      ok: false,
      error: "sync_not_configured"
    }, 503);
  }

  const authorization = request.headers.get("Authorization");

  if (authorization !== `Bearer ${token}`) {
    return respond({
      ok: false,
      error: "unauthorized"
    }, 401);
  }

  const url = new URL(request.url);
  const rawAfter = url.searchParams.get("after") || "0";

  if (!/^\d{1,15}$/.test(rawAfter)) {
    return respond({
      ok: false,
      error: "invalid_cursor"
    }, 400);
  }

  const after = Number(rawAfter);

  if (!Number.isSafeInteger(after)) {
    return respond({
      ok: false,
      error: "invalid_cursor"
    }, 400);
  }

  try {
    const result = await env.DB.prepare(`
      SELECT
        id,
        created_at,
        bank,
        question_id,
        question_version,
        question_type,
        original_prompt,
        category,
        report_text,
        visitor_id,
        status,
        resolved_at
      FROM reports
      WHERE scope = 'labour-law'
        AND id > ?
      ORDER BY id ASC
      LIMIT 100
    `).bind(after).all();

    const reports = result.results || [];

    return respond({
      ok: true,
      reports,
      nextAfter: reports.length
        ? reports[reports.length - 1].id
        : after,
      hasMore: reports.length === 100
    }, 200);

  } catch (error) {
    console.error("Reports export failed:", error);

    return respond({
      ok: false,
      error: "database_error"
    }, 500);
  }
}
