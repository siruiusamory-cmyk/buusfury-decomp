import type { APIRoute } from "astro";

import {
  buildoutDone,
  buildoutPercent,
  buildoutTotal,
  programmeDone,
  programmePercent,
  programmeTotal,
  project,
  roadmap,
  roadmapNextPhase,
} from "../data/project";

/**
 * The status data the page renders, as JSON.
 *
 * The progress page and this document are built from the same module in the
 * same build, so a consumer can check the rendered page against the data behind
 * it instead of matching prose. That is the point: the figures and the milestone
 * states have exactly one owner, and a test can prove the two never drift.
 */
export const GET: APIRoute = () =>
  new Response(
    JSON.stringify(
      {
        blocker: {
          paragraphs: project.blockerParagraphs,
          short: project.blockerShort,
          title: project.blockerTitle,
        },
        buildout: {
          done: buildoutDone,
          percent: buildoutPercent,
          total: buildoutTotal,
        },
        acceptanceTarget: project.acceptanceTarget,
        frontier: project.frontier,
        milestones: project.milestones,
        nextPhase: roadmapNextPhase
          ? { id: roadmapNextPhase.id, title: roadmapNextPhase.title }
          : null,
        programme: {
          done: programmeDone,
          percent: programmePercent,
          total: programmeTotal,
        },
        roadmapPhases: roadmap.phases.map((phase) => ({
          id: phase.id,
          state: phase.state,
          title: phase.title,
        })),
        breakthroughs: project.breakthroughs.map((breakthrough) => ({
          id: breakthrough.id,
          recent: breakthrough.recent ?? false,
          summary: breakthrough.summary,
          technical: breakthrough.technical ?? null,
          title: breakthrough.title,
        })),
      },
      null,
      2,
    ),
    { headers: { "content-type": "application/json; charset=utf-8" } },
  );
