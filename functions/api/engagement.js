const SCOPE = "labour-law";

const BANKS = new Set([
  "convencao-acordo-coletivo",
  "contribuicao-sindical",
  "contribuicao-confederativa",
  "mensalidade-sindical",
  "aviso-previo"
]);


function json(data, status = 200) {
  return new Response(
    JSON.stringify(data),
    {
      status,
      headers: {
        "content-type":
          "application/json; charset=utf-8",

        "cache-control":
          "no-store"
      }
    }
  );
}


function safeString(value, max = 180) {
  return String(value || "")
    .trim()
    .slice(0, max);
}


async function ensureStats(DB) {
  await DB.prepare(`
    INSERT OR IGNORE INTO stats(scope)
    VALUES (?)
  `)
    .bind(SCOPE)
    .run();
}


async function currentStats(DB) {

  await ensureStats(DB);

  const row = await DB.prepare(`
    SELECT
      views,
      likes,
      completions,
      feedbacks
    FROM stats
    WHERE scope = ?
  `)
    .bind(SCOPE)
    .first();

  return {
    views:
      Number(row?.views || 0),

    likes:
      Number(row?.likes || 0),

    completions:
      Number(row?.completions || 0),

    feedbacks:
      Number(row?.feedbacks || 0)
  };
}


/* =========================================================
   GET
   /api/engagement

   Returns public counters.
   Optionally returns whether this visitor liked this bank.
   ========================================================= */

export async function onRequestGet(context) {

  try {

    const { request, env } =
      context;

    const url =
      new URL(request.url);

    const visitorId =
      safeString(
        url.searchParams.get("visitor"),
        100
      );

    const bank =
      safeString(
        url.searchParams.get("bank"),
        80
      );

    const stats =
      await currentStats(env.DB);

    let liked = false;


    if(
      visitorId &&
      BANKS.has(bank)
    ){

      const row =
        await env.DB.prepare(`
          SELECT 1 AS liked
          FROM bank_likes
          WHERE
            scope = ?
            AND bank = ?
            AND visitor_id = ?
          LIMIT 1
        `)
          .bind(
            SCOPE,
            bank,
            visitorId
          )
          .first();

      liked =
        Boolean(row);

    }


    return json({
      ok: true,
      ...stats,
      liked
    });

  } catch(error) {

    console.error(error);

    return json(
      {
        ok: false,
        error: "stats_unavailable"
      },
      500
    );

  }
}


/* =========================================================
   POST
   ========================================================= */

export async function onRequestPost(context) {

  try {

    const { request, env } =
      context;

    const body =
      await request.json();

    const action =
      safeString(
        body.action,
        40
      );

    const visitorId =
      safeString(
        body.visitorId,
        100
      );

    const bank =
      safeString(
        body.bank,
        80
      );

    const attemptId =
      safeString(
        body.attemptId,
        100
      );


    await ensureStats(env.DB);


    /* -----------------------------------------------------
       VIEW
       ----------------------------------------------------- */

    if(action === "view"){

      await env.DB.batch([

        env.DB.prepare(`
          UPDATE stats
          SET
            views = views + 1,
            updated_at = CURRENT_TIMESTAMP
          WHERE scope = ?
        `)
          .bind(SCOPE),

        env.DB.prepare(`
          INSERT INTO events(
            event_type,
            scope,
            bank,
            visitor_id
          )
          VALUES(
            'view',
            ?,
            ?,
            ?
          )
        `)
          .bind(
            SCOPE,
            BANKS.has(bank)
              ? bank
              : null,
            visitorId || null
          )

      ]);

      return json({
        ok: true,
        ...(await currentStats(env.DB))
      });
    }


    /* -----------------------------------------------------
       LIKE / UNLIKE

       One active like per browser per bank.
       ----------------------------------------------------- */

    if(action === "toggle_like"){

      if(
        !visitorId ||
        !BANKS.has(bank)
      ){
        return json(
          {
            ok: false,
            error: "invalid_like"
          },
          400
        );
      }


      const existing =
        await env.DB.prepare(`
          SELECT 1
          FROM bank_likes
          WHERE
            scope = ?
            AND bank = ?
            AND visitor_id = ?
        `)
          .bind(
            SCOPE,
            bank,
            visitorId
          )
          .first();


      if(existing){

        await env.DB.batch([

          env.DB.prepare(`
            DELETE FROM bank_likes
            WHERE
              scope = ?
              AND bank = ?
              AND visitor_id = ?
          `)
            .bind(
              SCOPE,
              bank,
              visitorId
            ),

          env.DB.prepare(`
            UPDATE stats
            SET
              likes =
                CASE
                  WHEN likes > 0
                  THEN likes - 1
                  ELSE 0
                END,
              updated_at =
                CURRENT_TIMESTAMP
            WHERE scope = ?
          `)
            .bind(SCOPE),

          env.DB.prepare(`
            INSERT INTO events(
              event_type,
              scope,
              bank,
              visitor_id
            )
            VALUES(
              'unlike',
              ?,
              ?,
              ?
            )
          `)
            .bind(
              SCOPE,
              bank,
              visitorId
            )

        ]);


        return json({
          ok: true,
          liked: false,
          ...(await currentStats(env.DB))
        });

      }


      await env.DB.batch([

        env.DB.prepare(`
          INSERT OR IGNORE
          INTO bank_likes(
            scope,
            bank,
            visitor_id
          )
          VALUES(?, ?, ?)
        `)
          .bind(
            SCOPE,
            bank,
            visitorId
          ),

        env.DB.prepare(`
          UPDATE stats
          SET
            likes = likes + 1,
            updated_at =
              CURRENT_TIMESTAMP
          WHERE scope = ?
        `)
          .bind(SCOPE),

        env.DB.prepare(`
          INSERT INTO events(
            event_type,
            scope,
            bank,
            visitor_id
          )
          VALUES(
            'like',
            ?,
            ?,
            ?
          )
        `)
          .bind(
            SCOPE,
            bank,
            visitorId
          )

      ]);


      return json({
        ok: true,
        liked: true,
        ...(await currentStats(env.DB))
      });
    }


    /* -----------------------------------------------------
       COMPLETION

       Same attempt cannot be counted twice.
       ----------------------------------------------------- */

    if(action === "completion"){

      if(
        !visitorId ||
        !attemptId ||
        !BANKS.has(bank)
      ){
        return json(
          {
            ok: false,
            error:
              "invalid_completion"
          },
          400
        );
      }


      const inserted =
        await env.DB.prepare(`
          INSERT OR IGNORE
          INTO completions(
            scope,
            bank,
            attempt_id,
            visitor_id
          )
          VALUES(?, ?, ?, ?)
        `)
          .bind(
            SCOPE,
            bank,
            attemptId,
            visitorId
          )
          .run();


      if(
        Number(
          inserted.meta?.changes || 0
        ) > 0
      ){

        await env.DB.batch([

          env.DB.prepare(`
            UPDATE stats
            SET
              completions =
                completions + 1,
              updated_at =
                CURRENT_TIMESTAMP
            WHERE scope = ?
          `)
            .bind(SCOPE),

          env.DB.prepare(`
            INSERT INTO events(
              event_type,
              scope,
              bank,
              visitor_id,
              attempt_id
            )
            VALUES(
              'completion',
              ?,
              ?,
              ?,
              ?
            )
          `)
            .bind(
              SCOPE,
              bank,
              visitorId,
              attemptId
            )

        ]);

      }


      return json({
        ok: true,
        counted:
          Number(
            inserted.meta?.changes || 0
          ) > 0,

        ...(await currentStats(env.DB))
      });
    }


    return json(
      {
        ok: false,
        error: "unknown_action"
      },
      400
    );


  } catch(error) {

    console.error(error);

    return json(
      {
        ok: false,
        error: "server_error"
      },
      500
    );

  }

}
