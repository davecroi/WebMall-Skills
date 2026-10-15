from dataclasses import dataclass
from browsergym.experiments.loop import ExpArgs
from .env_args import EnvArgsWebMall

@dataclass
class ExpArgsWebMall(ExpArgs):
    env_args: EnvArgsWebMall 
    # agents run on AX-tree only (use_screenshot=False); step PNGs are never read
    save_screenshot: bool = False
