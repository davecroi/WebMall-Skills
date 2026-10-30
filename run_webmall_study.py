"""
Note: This script is a convenience script to launch experiments instead of using
the command line.

Copy this script and modify at will, but don't push your changes to the
repository.
"""

import os
import sys
import logging
import subprocess
from dotenv import load_dotenv
import bgym

from agentlab.agents.visualwebmall_agent.agent import WA_AGENT_4O
from agentlab.agents.webmall_generic_agent import (
    AGENT_4o_VISION,
    AGENT_4o_MINI,
    AGENT_4o,
    AGENT_CLAUDE_SONNET_35,
    AGENT_37_SONNET,
)
from webmall_overrides.study import WebMallStudy
from webmall_skills.injection import skill_path, with_skill
from webmall_skills.split import benchmarks as split_benchmarks
from pathlib import Path
from datetime import datetime
from analyze_agentlab_results.aggregate_log_statistics import process_study_directory
from analyze_agentlab_results.summarize_study import summarize_all_tasks_in_subdirs


logging.getLogger().setLevel(logging.DEBUG)

from agentlab.agents import dynamic_prompting as dp

from agentlab.llm.llm_configs import CHAT_MODEL_ARGS_DICT
from agentlab.llm.chat_api import OpenAIModelArgs, OpenRouterModelArgs

from agentlab.agents.generic_agent.generic_agent import (
    GenericAgent,
    GenericPromptFlags,
    GenericAgentArgs,
)

FLAGS_default = GenericPromptFlags(
    obs=dp.ObsFlags(
        use_html=False,
        use_ax_tree=True,
        use_focused_element=True,
        use_error_logs=True,
        use_history=True,
        use_past_error_logs=False,
        use_action_history=True,
        use_think_history=True,
        use_diff=False,
        html_type="pruned_html",
        use_screenshot=False,
        use_som=False,
        extract_visible_tag=True,
        extract_clickable_tag=True,
        extract_coords="False",
        filter_visible_elements_only=False,
    ),
    action=dp.ActionFlags(
        action_set=bgym.HighLevelActionSetArgs(
            subsets=["bid"],
            multiaction=False,
        ),
        long_description=False,
        individual_examples=False,
    ),
    use_plan=False,
    use_criticise=False,
    use_thinking=True,
    use_memory=False,
    use_concrete_example=True,
    use_abstract_example=True,
    use_hints=True,
    enable_chat=False,
    max_prompt_tokens=60_000,
    be_cautious=True,
    extra_instructions=None,
)

FLAGS_AX = FLAGS_default.copy()

FLAGS_V = FLAGS_default.copy()
FLAGS_V.obs.use_screenshot = True
FLAGS_V.obs.use_som = True
FLAGS_V.obs.use_ax_tree = False

FLAGS_AX_V = FLAGS_default.copy()
FLAGS_AX_V.obs.use_screenshot = True
FLAGS_AX_V.obs.use_som = True

FLAGS_AX_M = FLAGS_default.copy()
FLAGS_AX_M.use_memory = True
FLAGS_AX_M.extra_instructions = "Use your memory to note down important information like the URLs of potential solutions and corresponding pricing information."

AGENT_41_AX = GenericAgentArgs(
    chat_model_args=CHAT_MODEL_ARGS_DICT["openai/gpt-4.1-2025-04-14"],
    flags=FLAGS_AX,
)

AGENT_CLAUDE_AX = GenericAgentArgs(
    chat_model_args=CHAT_MODEL_ARGS_DICT["anthropic/claude-sonnet-4-20250514"],
    flags=FLAGS_AX,
)

AGENT_41_V = GenericAgentArgs(
    chat_model_args=CHAT_MODEL_ARGS_DICT["openai/gpt-4.1-2025-04-14"],
    flags=FLAGS_V,
)

AGENT_CLAUDE_V = GenericAgentArgs(
    chat_model_args=CHAT_MODEL_ARGS_DICT["anthropic/claude-sonnet-4-20250514"],
    flags=FLAGS_V,
)

AGENT_41_AX_V = GenericAgentArgs(
    chat_model_args=CHAT_MODEL_ARGS_DICT["openai/gpt-4.1-2025-04-14"],
    flags=FLAGS_AX_V,
)

AGENT_CLAUDE_AX_V = GenericAgentArgs(
    chat_model_args=CHAT_MODEL_ARGS_DICT["anthropic/claude-sonnet-4-20250514"],
    flags=FLAGS_AX_V,
)

AGENT_41_AX_M = GenericAgentArgs(
    chat_model_args=CHAT_MODEL_ARGS_DICT["openai/gpt-4.1-2025-04-14"],
    flags=FLAGS_AX_M,
)

AGENT_5mini_AX_M = GenericAgentArgs(
    chat_model_args=CHAT_MODEL_ARGS_DICT["openai/gpt-5-mini-2025-08-07"],
    flags=FLAGS_AX_M,
)

AGENT_5_AX_M = GenericAgentArgs(
    chat_model_args=CHAT_MODEL_ARGS_DICT["openai/gpt-5-2025-08-07"],
    flags=FLAGS_AX_M,
)

AGENT_CLAUDE_AX_M = GenericAgentArgs(
    chat_model_args=CHAT_MODEL_ARGS_DICT["anthropic/claude-sonnet-4-20250514"],
    flags=FLAGS_AX_M,
)

AGENT_GPT6_LUNA_AX_M = GenericAgentArgs(
    chat_model_args=OpenAIModelArgs(
        model_name="gpt-6-luna",
        max_total_tokens=1_050_000,
        max_input_tokens=922_000,
        max_new_tokens=128_000,
        temperature=1,  # gpt-6-luna supports temperature of 1 only
        vision_support=True,
    ),
    flags=FLAGS_AX_M,
)

# ---- OpenRouter agents (requires OPENROUTER_API_KEY in .env) ----
# model_name is the OpenRouter model id, see https://openrouter.ai/models
AGENT_OR_41_AX_M = GenericAgentArgs(
    chat_model_args=OpenRouterModelArgs(
        model_name="openai/gpt-4.1",
        max_total_tokens=1_047_576,
        max_input_tokens=1_047_576 - 16_384,
        max_new_tokens=16_384,
        temperature=1e-1,
        vision_support=True,
    ),
    flags=FLAGS_AX_M,
)

AGENT_OR_CLAUDE_AX_M = GenericAgentArgs(
    chat_model_args=OpenRouterModelArgs(
        model_name="anthropic/claude-sonnet-4",
        max_total_tokens=200_000,
        max_input_tokens=200_000 - 16_384,
        max_new_tokens=16_384,
        temperature=1e-1,
        vision_support=True,
    ),
    flags=FLAGS_AX_M,
)

AGENT_DEEPSEEK_V41_FLASH_AX_M = GenericAgentArgs(
    chat_model_args=OpenRouterModelArgs(
        model_name="deepseek/deepseek-v4.1-flash",
        max_total_tokens=1_048_576,
        max_input_tokens=1_048_576 - 32_768,
        max_new_tokens=32_768,
        # 1 like gpt-6-luna and the other reasoning models; at 0.1 a parse retry resamples
        # the same malformed answer, and the model falls into repetition loops
        temperature=1,
        provider={"sort": "price"},  # cheapest provider first, fallbacks stay enabled
        vision_support=True,
    ),
    flags=FLAGS_AX_M,
)

AGENT_GLM_53_FLASH_AX_M = GenericAgentArgs(
    chat_model_args=OpenRouterModelArgs(
        model_name="z-ai/glm-5.3-flash",
        max_total_tokens=1_048_576,
        max_input_tokens=1_048_576 - 32_768,
        max_new_tokens=32_768,
        temperature=1,
        provider={"sort": "price"},  # cheapest provider first, fallbacks stay enabled
        vision_support=True,
    ),
    flags=FLAGS_AX_M,
)

current_file = Path(__file__).resolve()
PATH_TO_DOT_ENV_FILE = current_file.parent / ".env"
load_dotenv(PATH_TO_DOT_ENV_FILE)


# choose your agent or provide a new agent
# agent_args = [AGENT_DEEPSEEK_V41_FLASH_AX_M]
agent_args = [AGENT_GLM_53_FLASH_AX_M]

# ## select the skill injected into the prompt (see webmall_skills/docs/skill_injection.md)
# None = no-skill baseline; a name = webmall_skills/skills/<name>/SKILL.md; or a path to a .md file
#skill = None
#skill = "base"       # hand-built base skill
# skill = "skillopt"   # SkillOpt C3 skill (best of the C3 run)
skill = "lite"
agent_args = [with_skill(a, skill_path(skill)) for a in agent_args]

# ## select the benchmark to run on

# benchmark = "webmall_specific_product_search_v1.0"
# benchmark = "webmall_vague_product_search_v1.0"
# benchmark = "webmall_cheapest_product_search_v1.0"
# benchmark = "webmall_action_and_transaction_v1.0"
# benchmark = "webmall_end_to_end_v1.0"
# benchmark = "webmall_old_setup_failure_v1.0"  # 1 task that failed with the old DeepSeek setup
# benchmark = "webmall_deepseek_fix_check_v1.0"  # 5 tasks of mixed categories to check the DeepSeek fixes
benchmark = "webmall_skills_test"   # 33 held-out test tasks of the webmall_skills split
# benchmark = "webmall_skills_val"    # 21 validation tasks (used by SkillOpt's gate)
# benchmark = "webmall_skills_train"  # 26 training tasks
split_benchmarks.register()

# Set reproducibility_mode = True for reproducibility
# this will "ask" agents to be deterministic. Also, it will prevent you from launching if you have
# local changes. For your custom agents you need to implement set_reproducibility_mode
reproducibility_mode = False

# Set relaunch = True to relaunch an existing study, this will continue incomplete
# experiments and relaunch errored experiments
relaunch = False

## Number of parallel jobs
n_jobs = 1  # Make sure to use 1 job when debugging in VSCode
# n_jobs = -1  # to use all available cores


def tee_console_to(log_path):
    """Copy everything written to stdout/stderr into log_path while still showing it.

    Works on the file descriptors, so output of Ray workers and subprocesses is captured too.
    tee runs in its own session so Ctrl+C does not kill it before the last lines are written.
    """
    log_path.parent.mkdir(parents=True, exist_ok=True)
    tee = subprocess.Popen(["tee", "-a", str(log_path)], stdin=subprocess.PIPE, start_new_session=True)
    sys.stdout.flush()
    sys.stderr.flush()
    os.dup2(tee.stdin.fileno(), sys.stdout.fileno())
    os.dup2(tee.stdin.fileno(), sys.stderr.fileno())
    sys.stdout.reconfigure(line_buffering=True)  # keep stdout and stderr lines in order


if __name__ == "__main__":  # necessary for dask backend

    if reproducibility_mode:
        [a.set_reproducibility_mode() for a in agent_args]

    if relaunch:
        #  relaunch an existing study
        study = WebMallStudy.load_most_recent(contains=None)
        study.find_incomplete(include_errors=True)

    else:
        study = WebMallStudy(
            agent_args, benchmark, logging_level_stdout=logging.INFO, suffix="AX_M"
        )
        study_name = study.name
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        # same place as AgentLab/original WebMall: $AGENTLAB_EXP_ROOT, or $HOME/agentlab_results
        # when it is unset or empty (an empty value would otherwise put the study under "/")
        exp_root = os.getenv("AGENTLAB_EXP_ROOT") or Path.home() / "agentlab_results"
        study_dir = f"{exp_root}/{timestamp}_{study_name}/"
        study = WebMallStudy(
            agent_args,
            benchmark,
            logging_level_stdout=logging.INFO,
            dir=study_dir,
            suffix="AX_M",
        )

    tee_console_to(Path(study.dir) / "console.log")

    parallel_backends = ["sequential", "ray"]
    study.run(
        n_jobs=n_jobs,
        parallel_backend=parallel_backends[1],
        strict_reproducibility=reproducibility_mode,
        n_relaunch=1,
    )

    if reproducibility_mode:
        study.append_to_journal(strict_reproducibility=True)

    summarize_all_tasks_in_subdirs(str(study.dir))
    process_study_directory(str(study.dir))
