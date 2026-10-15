"""
Scripted exploration of the four WebMall shops for the base skill.

Runs fixed probe scenarios through BrowserGym's open-ended task and saves the
same flattened AX tree the agent receives. Actions use the agent's action
strings (fill/click/keyboard_press/goto). No order is placed.

Usage (from the repo root): python -m webmall_skills.skill_construction.explore_shops
"""

import json
import os
import re

import gymnasium as gym
import browsergym.core  # noqa: F401  registers browsergym/openended
from browsergym.core.action.highlevel import HighLevelActionSet
from browsergym.utils.obs import flatten_axtree_to_str
from dotenv import load_dotenv

from webmall_skills.paths import REPO_ROOT, SKILLS_DIR

CONSTRUCTION_DIR = SKILLS_DIR / "base/construction"
EVIDENCE_DIR = CONSTRUCTION_DIR / "evidence"
SEARCH_INPUT = "input[name='s']"
NO_RESULTS_QUERY = "qqzxv wqpl"


def axtree_text(obs: dict) -> str:
    return flatten_axtree_to_str(
        obs["axtree_object"],
        extra_properties=obs["extra_element_properties"],
        with_visible=True,
        with_clickable=True,
        filter_visible_only=False,
    )


def slug_from_url(url: str) -> str | None:
    m = re.search(r"/product/([^/?#]+)", url)
    return m.group(1) if m else None


def evidence_name(shop: str, scenario: str, term: str = "") -> str:
    safe = re.sub(r"[^a-z0-9]+", "-", term.lower()).strip("-")
    return f"{shop}__{scenario}" + (f"__{safe}" if safe else "") + ".txt"


def short_query(title: str) -> str:
    return " ".join(re.findall(r"[A-Za-z0-9]+", title)[:2])


class Explorer:
    def __init__(self, start_url: str):
        action_set = HighLevelActionSet(
            subsets=["webarena"], multiaction=False, strict=False, retry_with_force=True
        )
        self.env = gym.make(
            "browsergym/openended",
            task_kwargs={"start_url": start_url},
            headless=True,
            action_mapping=action_set.to_python_code,
        )
        self.obs, _ = self.env.reset()

    @property
    def page(self):
        return self.env.unwrapped.page

    def act(self, action: str) -> dict:
        self.obs, _, _, _, _ = self.env.step(action)
        if action.startswith("click(") and "Timeout" in (self.obs.get("last_action_error") or ""):
            self.obs, _, _, _, _ = self.env.step("noop()")
            self.obs, _, _, _, _ = self.env.step(action)
        return self.obs

    def goto(self, url: str) -> dict:
        return self.act(f"goto({url!r})")

    def bid_of(self, selector: str) -> str | None:
        loc = self.page.locator(selector)
        for i in range(loc.count()):
            el = loc.nth(i)
            if el.is_visible():
                return el.get_attribute("bid")
        return None

    def product_urls(self) -> list[str]:
        urls = self.page.eval_on_selector_all(
            "a[href*='/product/']", "els => els.map(e => e.href)"
        )
        return sorted(set(urls))

    def save(self, name: str, obs: dict, note: str) -> str:
        EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
        header = f"url: {obs['url']}\nnote: {note}\nlast_action_error: {obs.get('last_action_error', '')}\n\n"
        (EVIDENCE_DIR / name).write_text(header + axtree_text(obs), encoding="utf-8")
        return name

    def close(self):
        self.env.close()


def search_result(obs: dict, n_links: int) -> dict:
    return {
        "url": obs["url"],
        "n_product_links": n_links,
        "action_error": obs.get("last_action_error") or "",
        "landed_on_product": slug_from_url(obs["url"]) is not None,
        "obs": obs,
    }


def _search(ex: Explorer, home: str, query: str, submit: str) -> dict:
    ex.goto(home)
    bid = ex.bid_of(SEARCH_INPUT)
    if bid is None:
        return {"error": "no visible search input"}
    ex.act(f"fill({bid!r}, {query!r})")
    if submit == "enter":
        obs = ex.act("keyboard_press('Enter')")
    else:
        button = ex.bid_of(
            "form:has(input[name='s']) button, form:has(input[name='s']) input[type='submit']"
        )
        if button is None:
            return {"error": "no visible search button"}
        obs = ex.act(f"click({button!r})")
    return search_result(obs, len(ex.product_urls()))


def _record(ex, shop, scenario, term, result, note) -> dict:
    obs = result.pop("obs", None)
    if obs is not None:
        result["evidence"] = ex.save(evidence_name(shop, scenario, term), obs, note)
    return result


def explore(shops: dict[str, str], terms: list[str], solution_url: str) -> dict:
    summary: dict = {}
    ex = Explorer(solution_url)
    try:
        for shop, home in shops.items():
            s = summary[shop] = {}
            ex.goto(home)
            s["_home"] = {"action_error": ex.obs.get("last_action_error") or "", "evidence": ex.save(evidence_name(shop, "home"), ex.obs, "shop home page")}
            first_product = None
            for term in terms:
                t = s[term] = {}
                for submit in ("enter", "button"):
                    r = _search(ex, home, term, submit)
                    t[submit] = _record(ex, shop, f"search_{submit}", term, r, f"search {term!r} via {submit}")
                    if submit == "enter" and first_product is None and ex.product_urls():
                        first_product = ex.product_urls()[0]
            r = _search(ex, home, NO_RESULTS_QUERY, "enter")
            s["_no_results"] = _record(ex, shop, "no_results", "", r, "nonsense query")
            if first_product:
                obs = ex.goto(first_product)
                title = ex.page.locator("h1").first.inner_text() if ex.page.locator("h1").count() else ""
                s["_product_page"] = {
                    "url_pattern": re.sub(r"/product/[^/]+", "/product/<slug>", obs["url"]),
                    "action_error": obs.get("last_action_error") or "",
                    "evidence": ex.save(evidence_name(shop, "product_page"), obs, "first product URL (alphabetical) from search results"),
                }
                for label, query in (("long", title), ("short", short_query(title))):
                    r = _search(ex, home, query, "enter")
                    s[f"_{label}_query"] = _record(ex, shop, f"{label}_query", "", r, f"{label} query from product title")
                ex.goto(first_product)
                add = ex.bid_of("button[name='add-to-cart'], button.single_add_to_cart_button")
                if add:
                    ex.act(f"click({add!r})")
                obs = ex.goto(home.rstrip("/") + "/cart/")
                s["_cart"] = {"action_error": obs.get("last_action_error") or "", "evidence": ex.save(evidence_name(shop, "cart"), obs, "cart after add-to-cart")}
                obs = ex.goto(home.rstrip("/") + "/checkout/")
                s["_checkout"] = {"action_error": obs.get("last_action_error") or "", "evidence": ex.save(evidence_name(shop, "checkout"), obs, "checkout form, NOT submitted")}
        obs = ex.goto(solution_url)
        summary["_solution_page"] = {"evidence": ex.save(evidence_name("solution", "page"), obs, "solution page")}
    finally:
        ex.close()
    (EVIDENCE_DIR / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    load_dotenv(REPO_ROOT / ".env")
    shops = {f"shop{i}": os.environ[f"SHOP{i}_URL"] for i in range(1, 5)}
    terms = [
        line.split("#", 1)[0].strip()
        for line in (CONSTRUCTION_DIR / "probe_terms.txt").read_text(encoding="utf-8").splitlines()
    ]
    terms = [t for t in terms if t]
    explore(shops, terms, os.environ["FRONTEND_URL"])
    print(f"evidence written to {EVIDENCE_DIR}")


if __name__ == "__main__":
    main()
