const BANKS = new Set([
  "convencao-acordo-coletivo",
  "contribuicao-sindical",
  "contribuicao-confederativa",
  "mensalidade-sindical",
  "aviso-previo"
]);


function json(data, status = 200){

  return new Response(
    JSON.stringify(data),
    {
      status,

      headers:{
        "content-type":
          "application/json; charset=utf-8",

        "cache-control":
          "no-store"
      }
    }
  );

}


function clean(value, max = 500){

  return String(
    value ?? ""
  )
    .trim()
    .slice(0, max);

}


function validScope(value){

  const scope =
    clean(value, 50);

  if(
    !/^[a-z0-9-]+$/.test(scope)
  ){
    return "site";
  }

  return scope;

}


async function ensureStats(DB, scope){

  await DB.prepare(`
    INSERT OR IGNORE INTO stats(scope)
    VALUES (?)
  `)
    .bind(scope)
    .run();

}


async function getStats(DB, scope){

  await ensureStats(
    DB,
    scope
  );

  const row =
    await DB.prepare(`
      SELECT
        views,
        likes,
        completions,
        feedbacks
      FROM stats
      WHERE scope = ?
    `)
      .bind(scope)
      .first();


  return {
    views:
      Number(row?.views || 0),

    likes:
      Number(row?.likes || 0),

    completions:
      Number(
        row?.completions || 0
      ),

    feedbacks:
      Number(
        row?.feedbacks || 0
      )
  };

}


async function changeCounter(
  DB,
  scope,
  field,
  amount
){

  const allowed =
    new Set([
      "views",
      "likes",
      "completions",
      "feedbacks"
    ]);


  if(!allowed.has(field)){
    throw new Error(
      "Invalid counter"
    );
  }


  const scopes =
    scope === "site"
      ? ["site"]
      : ["site", scope];


  for(const target of scopes){

    await ensureStats(
      DB,
      target
    );


    await DB.prepare(`
      UPDATE stats
      SET
        ${field} =
          MAX(0, ${field} + ?),

        updated_at =
          CURRENT_TIMESTAMP

      WHERE scope = ?
    `)
      .bind(
        amount,
        target
      )
      .run();

  }

}


async function addEvent(
  DB,
  {
    type,
    scope,
    bank = null,
    visitorId = null,
    attemptId = null
  }
){

  await DB.prepare(`
    INSERT INTO events(
      event_type,
      scope,
      bank,
      visitor_id,
      attempt_id
    )
    VALUES (?, ?, ?, ?, ?)
  `)
    .bind(
      type,
      scope,
      bank,
      visitorId,
      attemptId
    )
    .run();

}


/* =========================================================
   GET
   ========================================================= */

export async function onRequestGet(context){

  try{

    const { request, env } =
      context;

    const url =
      new URL(request.url);

    const scope =
      validScope(
        url.searchParams.get(
          "scope"
        ) || "site"
      );


    /* -----------------------------------------------------
       MOST LIKED QUESTIONS
       ----------------------------------------------------- */

    if(
      url.searchParams.get(
        "ranking"
      ) === "questions"
    ){

      const result =
        await env.DB.prepare(`
          SELECT
            q.bank,
            q.question_id,
            q.section,
            q.question_type,
            q.prompt,
            COUNT(l.visitor_id) AS likes

          FROM questions q

          JOIN question_likes l
            ON l.scope = q.scope
            AND l.bank = q.bank
            AND l.question_id =
              q.question_id

          WHERE q.scope = ?

          GROUP BY
            q.bank,
            q.question_id,
            q.section,
            q.question_type,
            q.prompt

          HAVING COUNT(
            l.visitor_id
          ) > 0

          ORDER BY
            q.bank ASC,
            q.section ASC,
            likes DESC,
            q.question_id ASC
        `)
          .bind(scope)
          .all();


      return json({
        ok:true,
        questions:
          result.results || []
      });

    }


    const bank =
      clean(
        url.searchParams.get(
          "bank"
        ),
        80
      );

    const questionId =
      clean(
        url.searchParams.get(
          "question"
        ),
        100
      );

    const visitorId =
      clean(
        url.searchParams.get(
          "visitor"
        ),
        100
      );


    const stats =
      await getStats(
        env.DB,
        scope
      );


    let liked = false;
    let questionLikes = 0;


    if(
      bank &&
      questionId
    ){

      const count =
        await env.DB.prepare(`
          SELECT COUNT(*) AS n
          FROM question_likes
          WHERE
            scope = ?
            AND bank = ?
            AND question_id = ?
        `)
          .bind(
            scope,
            bank,
            questionId
          )
          .first();


      questionLikes =
        Number(count?.n || 0);


      if(visitorId){

        const mine =
          await env.DB.prepare(`
            SELECT 1
            FROM question_likes
            WHERE
              scope = ?
              AND bank = ?
              AND question_id = ?
              AND visitor_id = ?
            LIMIT 1
          `)
            .bind(
              scope,
              bank,
              questionId,
              visitorId
            )
            .first();


        liked =
          Boolean(mine);

      }

    }


    return json({
      ok:true,
      ...stats,
      liked,
      questionLikes
    });


  }catch(error){

    console.error(error);

    return json(
      {
        ok:false,
        error:"stats_unavailable"
      },
      500
    );

  }

}


/* =========================================================
   POST
   ========================================================= */

export async function onRequestPost(context){

  try{

    const { request, env } =
      context;

    const body =
      await request.json();


    const action =
      clean(
        body.action,
        50
      );

    const scope =
      validScope(
        body.scope ||
        "labour-law"
      );

    const bank =
      clean(
        body.bank,
        80
      );

    const visitorId =
      clean(
        body.visitorId,
        100
      );


    /* -----------------------------------------------------
       VIEW
       ----------------------------------------------------- */

    if(action === "view"){

      await changeCounter(
        env.DB,
        scope,
        "views",
        1
      );


      await addEvent(
        env.DB,
        {
          type:"view",
          scope,
          bank:
            BANKS.has(bank)
              ? bank
              : null,

          visitorId:
            visitorId || null
        }
      );


      return json({
        ok:true,
        ...(
          await getStats(
            env.DB,
            scope
          )
        )
      });

    }


    /* -----------------------------------------------------
       QUESTION LIKE
       ----------------------------------------------------- */

    if(
      action ===
      "toggle_question_like"
    ){

      const questionId =
        clean(
          body.questionId,
          100
        );

      const section =
        clean(
          body.section,
          180
        );

      const questionType =
        clean(
          body.questionType,
          80
        );

      const prompt =
        clean(
          body.prompt,
          4000
        );


      if(
        !visitorId ||
        !BANKS.has(bank) ||
        !questionId ||
        !section ||
        !prompt
      ){

        return json(
          {
            ok:false,
            error:"invalid_like"
          },
          400
        );

      }


      await env.DB.prepare(`
        INSERT INTO questions(
          scope,
          bank,
          question_id,
          section,
          question_type,
          prompt
        )
        VALUES (?, ?, ?, ?, ?, ?)

        ON CONFLICT(
          scope,
          bank,
          question_id
        )

        DO UPDATE SET
          section =
            excluded.section,

          question_type =
            excluded.question_type,

          prompt =
            excluded.prompt,

          updated_at =
            CURRENT_TIMESTAMP
      `)
        .bind(
          scope,
          bank,
          questionId,
          section,
          questionType,
          prompt
        )
        .run();


      const existing =
        await env.DB.prepare(`
          SELECT 1
          FROM question_likes

          WHERE
            scope = ?
            AND bank = ?
            AND question_id = ?
            AND visitor_id = ?

          LIMIT 1
        `)
          .bind(
            scope,
            bank,
            questionId,
            visitorId
          )
          .first();


      let liked;


      if(existing){

        await env.DB.prepare(`
          DELETE FROM question_likes

          WHERE
            scope = ?
            AND bank = ?
            AND question_id = ?
            AND visitor_id = ?
        `)
          .bind(
            scope,
            bank,
            questionId,
            visitorId
          )
          .run();


        await changeCounter(
          env.DB,
          scope,
          "likes",
          -1
        );


        liked = false;

      }else{

        await env.DB.prepare(`
          INSERT INTO question_likes(
            scope,
            bank,
            question_id,
            visitor_id
          )

          VALUES (?, ?, ?, ?)
        `)
          .bind(
            scope,
            bank,
            questionId,
            visitorId
          )
          .run();


        await changeCounter(
          env.DB,
          scope,
          "likes",
          1
        );


        liked = true;

      }


      const count =
        await env.DB.prepare(`
          SELECT COUNT(*) AS n

          FROM question_likes

          WHERE
            scope = ?
            AND bank = ?
            AND question_id = ?
        `)
          .bind(
            scope,
            bank,
            questionId
          )
          .first();


      await addEvent(
        env.DB,
        {
          type:
            liked
              ? "question_like"
              : "question_unlike",

          scope,
          bank,
          visitorId
        }
      );


      return json({
        ok:true,
        liked,

        questionLikes:
          Number(
            count?.n || 0
          ),

        ...(
          await getStats(
            env.DB,
            scope
          )
        )
      });

    }


    /* -----------------------------------------------------
       COMPLETION
       ----------------------------------------------------- */

    if(action === "completion"){

      const attemptId =
        clean(
          body.attemptId,
          100
        );


      if(
        !visitorId ||
        !attemptId ||
        !BANKS.has(bank)
      ){

        return json(
          {
            ok:false,
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

          VALUES (?, ?, ?, ?)
        `)
          .bind(
            scope,
            bank,
            attemptId,
            visitorId
          )
          .run();


      const counted =
        Number(
          inserted.meta?.changes || 0
        ) > 0;


      if(counted){

        await changeCounter(
          env.DB,
          scope,
          "completions",
          1
        );


        await addEvent(
          env.DB,
          {
            type:"completion",
            scope,
            bank,
            visitorId,
            attemptId
          }
        );

      }


      return json({
        ok:true,
        counted,

        ...(
          await getStats(
            env.DB,
            scope
          )
        )
      });

    }


    /* -----------------------------------------------------
       REPORT / FEEDBACK
       ----------------------------------------------------- */

    if(action === "report"){

      const questionId =
        clean(
          body.questionId,
          100
        );

      const questionType =
        clean(
          body.questionType,
          80
        );

      const prompt =
        clean(
          body.prompt,
          4000
        );

      const category =
        clean(
          body.category,
          100
        );

      const reportText =
        clean(
          body.reportText,
          4000
        );


      if(
        !BANKS.has(bank) ||
        !questionId ||
        !prompt ||
        !category ||
        !reportText
      ){

        return json(
          {
            ok:false,
            error:"invalid_report"
          },
          400
        );

      }


      await env.DB.prepare(`
        INSERT INTO reports(
          scope,
          bank,
          question_id,
          question_type,
          original_prompt,
          category,
          report_text,
          visitor_id
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      `)
        .bind(
          scope,
          bank,
          questionId,
          questionType,
          prompt,
          category,
          reportText,
          visitorId || null
        )
        .run();


      await changeCounter(
        env.DB,
        scope,
        "feedbacks",
        1
      );


      await addEvent(
        env.DB,
        {
          type:"report",
          scope,
          bank,
          visitorId:
            visitorId || null
        }
      );


      return json({
        ok:true,

        ...(
          await getStats(
            env.DB,
            scope
          )
        )
      });

    }


    return json(
      {
        ok:false,
        error:"unknown_action"
      },
      400
    );


  }catch(error){

    console.error(error);

    return json(
      {
        ok:false,
        error:"server_error"
      },
      500
    );

  }

}
