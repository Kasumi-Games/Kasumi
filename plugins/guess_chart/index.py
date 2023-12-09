import csv
import random
from fuzzywuzzy import process
from typing import List, Dict, Any
from bestdori import songs
from bestdori.charts import Chart

from bridge.tomorin import on_activator, on_event, h
from bridge.session_adder import SessionExtension

from .BanGDreamChartRender import render


def read_csv_to_dict(file_path):
    data_dict = {}
    with open(file_path, "r", encoding="UTF-8") as file:
        csv_reader = csv.reader(file)
        next(csv_reader)
        for row in csv_reader:
            key = row[0]  # 使用第一列作为字典的键
            values = row[1:]  # 使用剩余列作为字典的值
            if key is not None and values is not None and key != "":
                data_dict[key] = [value for value in values if value != ""]
    result = {}
    for key, values in data_dict.items():
        new_values = []
        for value in values:
            new_values.extend(value.split(","))
        result[key] = new_values
    return result


def fuzzy_match(query: str, dictionary: dict):
    max_ratio = 0
    matched_key = None
    for key, value in dictionary.items():
        if query in value:
            return key
        _, ratio = process.extractOne(query, value) or (0, 0)
        if ratio > max_ratio:
            max_ratio = ratio
            matched_key = key
    return matched_key


def get_difficulty(args: list):
    if not args:
        return "expert"

    if args[0] in ["ez", "easy", "简单"]:
        return "easy"

    if args[0] in ["nm", "normal", "普通"]:
        return "normal"

    if args[0] in ["hd", "hard", "困难"]:
        return "hard"

    if args[0] in ["ex", "expert", "专家"]:
        return "expert"


def sep_chart(chart: Chart, difficulty: str) -> List[List[Dict[str, Any]]]:
    chart: List[Dict[str, Any]] = chart.to_list()
    chart_length = len(chart)

    if difficulty == "easy":
        sep_num = 2
        sep_length = 200
    elif difficulty == "normal":
        sep_num = 2
        sep_length = 100
    elif difficulty == "hard":
        sep_num = 2
        sep_length = 50
    elif difficulty == "expert":
        sep_num = 1
        sep_length = 50
    else:
        raise ValueError("Invalid difficulty level")

    # 根据 sep_num 随机切割 chart 为不重复的多段
    sep_points = []
    sep_range = list(range(chart_length - sep_length))
    for _ in range(sep_num):
        sep_point = random.choice(sep_range)
        sep_points.append(sep_point)

        for i in range(sep_point, sep_point + sep_length):
            sep_range.remove(i)

    sep_points = sorted(sep_points)

    sep_charts: List[List[Dict[str, Any]]] = []
    for i in sep_points:
        sep_charts.append(Chart.normalize(chart[i : i + sep_length]).to_list())

    return sep_charts


def compare_origin_songname(guessed_name: str, song_data: Dict[str, Dict[str, Any]]):
    for key, data in song_data.items():
        if guessed_name in data["musicTitle"]:
            return key
    return None


guess_chart_context = {}
song_data = None
nickname_song = read_csv_to_dict("plugins/guess_chart/nickname_song.csv")

diff_num = {
    "easy": "0",
    "normal": "1",
    "hard": "2",
    "expert": "3",
    "special": "4",
}


@on_activator.interval(24 * 3600)
def refresh_song_data():
    global song_data
    song_data = songs.get_all(proxy="http://127.0.0.1:7890")


@on_activator.command(["猜谱面", "cpm"])
def guess_chart(session: SessionExtension):
    """猜邦邦谱面"""
    global song_data
    global guess_chart_context

    if session.channel.id in guess_chart_context:
        session.send("你已经在猜谱面了哦")
        return None

    game_difficulty: str = get_difficulty(session.command.args)

    if not song_data:
        song_data = songs.get_all(proxy="http://127.0.0.1:7890")

    song_id, song_info = random.choice(list(song_data.items()))

    if song_data[song_id]["difficulty"].get(diff_num["special"]):
        chart_difficulty = random.choice(["expert", "special"])
    else:
        chart_difficulty = "expert"

    chart = Chart.get_chart(song_id, chart_difficulty, proxy="http://127.0.0.1:7890")

    if song_info["difficulty"][diff_num[chart_difficulty]]["playLevel"] <= 27:
        img = render(chart.to_list())
    else:
        # TODO: 改为渲染不完整的谱面
        img = render(chart.to_list())

    # charts = sep_chart(chart, game_difficulty)

    # chart_images = [render(chart) for chart in charts]

    guess_chart_context[session.channel.id] = {
        "chart_id": song_id,
        "chart_difficulty": chart_difficulty,
        "game_difficulty": game_difficulty,
        "song": song_info,
        "chart": chart,
        "prompt": {
            "level": False,
            "diff": False,
        },
    }

    # for image in chart_images:
    #     session.send(h.image(image))

    session.send(h.image(img))


@on_event.message_created
def handle_answer(session: SessionExtension):
    global guess_chart_context
    global nickname_song
    global song_data

    if session.channel.id not in guess_chart_context:
        return None

    if session.message.content.strip().startswith(("猜谱面", "cpm")):
        return None

    correct_chart_id: str = guess_chart_context[session.channel.id]["chart_id"]
    diff: str = guess_chart_context[session.channel.id]["chart_difficulty"]
    level = guess_chart_context[session.channel.id]["song"]["difficulty"][
        diff_num[diff]
    ]["playLevel"]

    if session.message.content.strip() in ["bzd", "不知道", "结束猜谱", "结束猜谱面"]:
        session.send(
            f"要再试一次吗？\n谱面：{nickname_song[correct_chart_id][0]} "
            f"{diff.upper()} LV.{level}"
        )
        guess_chart_context.pop(session.channel.id)
        return None

    if session.message.content.strip() in ["提示", "给点提示"]:
        if not guess_chart_context[session.channel.id]["prompt"]["level"]:
            session.send(f"这首曲子是 {level} 级的哦")
            guess_chart_context[session.channel.id]["prompt"]["level"] = True
        elif not guess_chart_context[session.channel.id]["prompt"]["diff"]:
            session.send(f"这首曲子是 {diff} 难度的哦")
            guess_chart_context[session.channel.id]["prompt"]["diff"] = True
        else:
            session.send("已经没有提示啦")
        return None

    print(guess_chart_context)

    if not session.message.content.strip().isdigit():
        guessed_chart_id = fuzzy_match(session.message.content.strip(), nickname_song)
        if guessed_chart_id is None:
            guessed_chart_id = compare_origin_songname(session.message.content.strip(), song_data)
    else:
        guessed_chart_id = session.message.content.strip()

    if correct_chart_id == guessed_chart_id:
        session.send(
            "回答正确！"
            f"谱面：{nickname_song[correct_chart_id][0]} "
            f"{diff.upper()} LV.{level}"
            # f"{h.image(render(guess_chart_context[session.channel.id]['chart']))}"
        )
        guess_chart_context.pop(session.channel.id)

    # else:
    #     session.send("不对哦，再想想吧")
