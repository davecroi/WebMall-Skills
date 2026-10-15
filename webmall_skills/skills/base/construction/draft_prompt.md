You are writing a skill document for a web agent that solves comparison-shopping
tasks across four web shops (the WebMall benchmark). The skill is inserted into
the agent's prompt at every step under the heading "## Skill Knowledge".

Use ONLY the two attached inputs:
1. SOURCES — the general task instruction, the task-category descriptions and
   the layout of the agent's prompt.
2. FINDINGS — observed behaviour of the shops. Only findings with
   "Status: rule" may become rules; ignore "one-off" findings.

Hard constraints:
- At most 800 words.
- No product names, brands, model numbers, prices or statements about which shop
  sells what.
- Every instruction must be traceable to SOURCES or to a finding ID. Do not add
  advice from general knowledge.
- Write in English, as direct instructions to the agent.

Use exactly this structure:
1. "# WebMall Shopping Skill" with a short overview, then an "Output format"
   paragraph: every answer contains <think>, <memory> and exactly one
   <action>...</action>; never answer in plain text without an <action>.
2. "## Environment": the four shops, the solution page and the submission rules,
   and shop behaviour from the findings.
3. "## Task Categories": a table with one row per task category (11 rows):
   Category | Goal | Key steps.
4. "## General Principles": numbered list.
5. "## Common Mistakes to Avoid": bullet list.

After the skill, output a line "---TRACE---" followed by one line per
instruction giving its source ("SOURCES §n" or a finding ID). The trace is for
the reviewer and will be removed from the final skill.
