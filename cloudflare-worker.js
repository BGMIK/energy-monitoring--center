/**
 * MILCHO HUB scheduler.
 * Deploy as a Cloudflare Worker and add a Cron Trigger that runs every five minutes
 * Add secret GITHUB_TOKEN (fine-grained PAT with Actions: Read and write).
 *
 * The Worker does not collect or fabricate data. It reliably dispatches the
 * existing validated Python collector workflow; refresh_data.py remains the
 * sole authority for validating ESO sources and publishing data.json.
 */
const OWNER = "BGMIK";
const REPO = "energy-monitoring--center";
const WORKFLOW = "refresh-data.yml";
const BRANCH = "main";

export default {
  async scheduled(controller, env, ctx) {
    ctx.waitUntil(dispatchCollector(env));
  },

  async fetch(request, env) {
    if (request.method !== "GET") {
      return new Response("Method not allowed", { status: 405 });
    }
    return Response.json({
      service: "MILCHO HUB scheduler",
      status: env.GITHUB_TOKEN ? "configured" : "missing GITHUB_TOKEN",
      schedule: "*/5 * * * *",
      workflow: `.github/workflows/${WORKFLOW}`,
      note: "Scheduler health only; data freshness is reported by data.json."
    }, {
      headers: { "Cache-Control": "no-store" }
    });
  }
};

async function dispatchCollector(env) {
  if (!env.GITHUB_TOKEN) {
    console.error("Missing GITHUB_TOKEN secret; collector was not dispatched.");
    return;
  }

  const url = `https://api.github.com/repos/${OWNER}/${REPO}/actions/workflows/${WORKFLOW}/dispatches`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${env.GITHUB_TOKEN}`,
      "Accept": "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "MILCHO-HUB-Cloudflare-Scheduler",
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ ref: BRANCH })
  });

  if (!response.ok) {
    const detail = (await response.text()).slice(0, 500);
    console.error(`GitHub workflow dispatch failed: HTTP ${response.status}: ${detail}`);
    throw new Error(`GitHub workflow dispatch failed with HTTP ${response.status}`);
  }

  console.log(`Collector workflow dispatched at ${new Date().toISOString()}`);
}
