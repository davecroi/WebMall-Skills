from webmall_skills.skillopt_webmall.tasks import gym_task_name, load_task_index, task_type


def test_index_has_91_tasks_in_11_categories():
    index = load_task_index()
    assert len(index) == 91
    assert len({t["category"] for t in index.values()}) == 11
    assert len({t["task_set_id"] for t in index.values()}) == 11


def test_task_text_is_stripped_of_tags():
    t = load_task_index()["Webmall_Find_Specific_Product_Task6"]
    assert "<task>" not in t["task_text"]
    assert "\\n" not in t["task_text"]
    assert "Corsair Vengeance" in t["task_text"]


def test_task_type_and_gym_name():
    assert task_type("Webmall_EndToEnd_Task3") == "Webmall_EndToEnd_Task"
    assert task_type("Webmall_Add_To_Cart_Task12") == "Webmall_Add_To_Cart_Task"
    assert gym_task_name("Webmall_Checkout_Task1") == "webmall.Webmall_Checkout_Task1"
