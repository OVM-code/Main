export const meta = {
  name: 'port-ai-system',
  description: 'Port an AI system (prompts, tool schemas, orchestration) from a source model to a target model, using live-researched current conventions for both',
  whenToUse: 'Call with args: { sourceModel, targetModel, system, outputPath? }. system is the content of the AI system to port, or a path/description an agent can read. See skills/cross-model-porting-discipline.md for the methodology this operationalizes.',
  phases: [
    { title: 'Research', detail: 'live-lookup current prompting conventions for source and target models' },
    { title: 'Map', detail: 'synthesize a compatibility map: same-capability-different-syntax, gaps, opportunities' },
    { title: 'Transform', detail: 'rewrite the system for the target model per the map' },
    { title: 'Verify', detail: 'adversarially check behavioral equivalence and target-convention fidelity' },
  ],
}

const parsedArgs = typeof args === 'string' ? JSON.parse(args) : args

if (!parsedArgs || !parsedArgs.sourceModel || !parsedArgs.targetModel || !parsedArgs.system) {
  throw new Error(
    'port-ai-system requires args: { sourceModel, targetModel, system, outputPath? }. ' +
    'system is the content of the AI system to port (or a path/description an agent can read). ' +
    'Pass args as an actual JSON object in the tool call, not a JSON-encoded string.'
  )
}

const { sourceModel, targetModel, system, outputPath } = parsedArgs

const RESEARCH_SCHEMA = {
  type: 'object',
  properties: {
    model: { type: 'string' },
    messageRoles: { type: 'string' },
    toolCalling: { type: 'string' },
    contextWindow: { type: 'string' },
    reasoningSupport: { type: 'string' },
    multimodal: { type: 'string' },
    costMechanisms: { type: 'string' },
    styleConventions: { type: 'string' },
    quirks: { type: 'string' },
    unverifiedFields: { type: 'array', items: { type: 'string' } },
    sources: { type: 'array', items: { type: 'string' } },
  },
  required: ['model', 'sources'],
}

function researchPrompt(model) {
  return `Research the CURRENT, official prompting and architecture conventions for "${model}" as of today. Use web search and fetch official provider documentation (API reference, prompting guide, model card) rather than relying on memorized training data alone — prompting conventions and model capabilities change between releases faster than any single knowledge cutoff tracks. Cover, as best you can find documented: message roles (system/developer/user/assistant) and how each is meant to be used; tool/function-calling format (schema style, structured output, parallel tool calls); context window size; extended-reasoning/"thinking" support and how it's invoked, if any; multimodal input support; prompt-caching or other cost/latency mechanisms; documented style conventions (e.g. XML tags vs markdown, instruction placement, typical system-prompt length); known quirks or failure modes specific to this family. Cite the specific URLs you actually used in "sources". If you cannot find current official documentation for this exact model, say so explicitly in "unverifiedFields" rather than filling the gap from memory.`
}

phase('Research')
log(`Researching current conventions for source (${sourceModel}) and target (${targetModel})`)

const [sourceResearch, targetResearch] = await parallel([
  () => agent(researchPrompt(sourceModel), { label: `research:${sourceModel}`, phase: 'Research', schema: RESEARCH_SCHEMA, effort: 'low' }),
  () => agent(researchPrompt(targetModel), { label: `research:${targetModel}`, phase: 'Research', schema: RESEARCH_SCHEMA, effort: 'low' }),
])

if (!sourceResearch || !targetResearch) {
  throw new Error('Research phase failed for source or target model — cannot map without both.')
}

phase('Map')
const MAP_SCHEMA = {
  type: 'object',
  properties: {
    sameCapabilityDifferentSyntax: {
      type: 'array',
      items: {
        type: 'object',
        properties: { concept: { type: 'string' }, sourceSyntax: { type: 'string' }, targetSyntax: { type: 'string' } },
        required: ['concept', 'targetSyntax'],
      },
    },
    sourceOnlyGaps: {
      type: 'array',
      items: {
        type: 'object',
        properties: { capability: { type: 'string' }, recommendedHandling: { type: 'string' } },
        required: ['capability', 'recommendedHandling'],
      },
    },
    targetOnlyOpportunities: {
      type: 'array',
      items: {
        type: 'object',
        properties: { capability: { type: 'string' }, suggestion: { type: 'string' } },
        required: ['capability', 'suggestion'],
      },
    },
    structuralChanges: { type: 'array', items: { type: 'string' } },
  },
  required: ['sameCapabilityDifferentSyntax', 'sourceOnlyGaps', 'targetOnlyOpportunities'],
}

const map = await agent(
  `Given this research on the SOURCE model (${sourceModel}):\n${JSON.stringify(sourceResearch)}\n\n` +
  `And this research on the TARGET model (${targetModel}):\n${JSON.stringify(targetResearch)}\n\n` +
  `Produce a compatibility map for porting an AI system from source to target: (a) same-capability-different-syntax items with the concrete syntax translation for each; (b) capabilities the source system might rely on that the target lacks, each with a recommended handling (substitute / degrade gracefully / drop, and why); (c) capabilities the target has that the source doesn't use but could benefit from adopting; (d) structural changes needed (message roles, section markers, instruction style). Be concrete — this map is what the transform step will mechanically apply, not a prose summary.`,
  { label: 'map', phase: 'Map', schema: MAP_SCHEMA, effort: 'high' }
)

phase('Transform')
const transformed = await agent(
  `Port the following AI system from ${sourceModel} to ${targetModel}.\n\n` +
  `ORIGINAL SYSTEM (source: ${sourceModel}) — if this looks like a file path or description rather than full content, read that file (and anything it references) first:\n${system}\n\n` +
  `COMPATIBILITY MAP:\n${JSON.stringify(map)}\n\n` +
  `Rewrite the system for ${targetModel}: apply every same-capability-different-syntax translation, handle every source-only gap per its recommended handling (note inline which decision you applied and why), and apply the structural changes. Preserve the original's intent and behavior — this is a port, not a rewrite from scratch. Return the complete ported system, followed by a short changelog of what changed and why.`,
  { label: 'transform', phase: 'Transform' }
)

phase('Verify')
const VERDICT_SCHEMA = {
  type: 'object',
  properties: {
    passes: { type: 'boolean' },
    issues: { type: 'array', items: { type: 'string' } },
  },
  required: ['passes', 'issues'],
}

const lenses = [
  {
    key: 'behavioral-equivalence',
    prompt: `Compare the ORIGINAL system and the PORTED system below. Would a user interacting with the ported system on ${targetModel} get materially the same behavior and intent as the original on ${sourceModel}? Find a concrete case where behavior would differ in a way that matters, if one exists.\n\nORIGINAL:\n${system}\n\nPORTED:\n${transformed}`,
  },
  {
    key: 'target-convention-fidelity',
    prompt: `Given this research on ${targetModel}'s current conventions:\n${JSON.stringify(targetResearch)}\n\nDoes the PORTED system below actually follow those conventions (message roles, tool-calling format, style), or does it just look structurally similar to the original without adapting to the target?\n\nPORTED:\n${transformed}`,
  },
  {
    key: 'silent-regression',
    prompt: `Compare the COMPATIBILITY MAP below against the PORTED system. Did every source-only gap listed in the map get an explicit, visible handling in the ported system, or was anything silently dropped?\n\nMAP:\n${JSON.stringify(map)}\n\nPORTED:\n${transformed}`,
  },
]

const verdicts = (await parallel(lenses.map(l => () =>
  agent(l.prompt, { label: `verify:${l.key}`, phase: 'Verify', schema: VERDICT_SCHEMA, effort: 'high' })
    .then(v => v && { lens: l.key, ...v })
))).filter(Boolean)

// A lens can self-report passes:true while still listing real issues (a soft-fail,
// e.g. "this doesn't break the port but the field name is wrong") — repair on any
// reported issue, not only on a lens that failed outright, or those slip through.
const flaggedIssues = verdicts.flatMap(v => (v.issues || []).map(issue => ({ lens: v.lens, passes: v.passes, issue })))

let finalSystem = transformed
if (flaggedIssues.length) {
  log(`${flaggedIssues.length} issue(s) flagged across ${verdicts.length} verification lenses — repairing before finalizing`)
  finalSystem = await agent(
    `Fix the following ported AI system based on these verification issues, without breaking anything that already passed. Some issues come from a lens that otherwise judged the port passing ("passes": true) — fix them anyway if they're real, since a passing lens can still flag a genuine defect.\n\nISSUES:\n${JSON.stringify(flaggedIssues)}\n\nPORTED SYSTEM TO FIX:\n${transformed}\n\nReturn the complete corrected system.`,
    { label: 'repair', phase: 'Verify', effort: 'high' }
  )
}

if (outputPath) {
  await agent(
    `Write the following content exactly as given to the file at ${outputPath} (verify the parent directory exists first, creating it if needed). Do not modify, summarize, or reformat it.\n\n${finalSystem}`,
    { label: 'write-output', phase: 'Verify' }
  )
  log(`Wrote ported system to ${outputPath}`)
}

return {
  sourceModel,
  targetModel,
  compatibilityMap: map,
  portedSystem: finalSystem,
  verification: verdicts,
  repaired: flaggedIssues.length > 0,
  outputPath: outputPath || null,
}
