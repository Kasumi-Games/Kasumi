import csv
import random
from fuzzywuzzy import process
from typing import List, Dict, Any
from bestdori import songs
from bestdori.utils import get_bands_all
from bestdori.charts import Chart
from bestdori.songs import Song

from bridge.tomorin import on_activator, on_event, h, rm_all_xml, rm_perfix, admin_list
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


def get_value_from_list(song_names: List[str]):
    return (
        song_names[3]
        or song_names[0]
        or song_names[2]
        or song_names[1]
        or song_names[4]
    )


guess_chart_context = {}
song_data = None
band_data = None
nickname_song = read_csv_to_dict("plugins/guess_chart/nickname_song.csv")

diff_num = {
    "easy": "0",
    "normal": "1",
    "hard": "2",
    "expert": "3",
    "special": "4",
}


@on_activator.interval(24 * 3600)
def refresh_data():
    global song_data
    global band_data
    # song_data = songs.get_all(proxy="http://127.0.0.1:7890")
    # band_data = get_bands_all(proxy="http://127.0.0.1:7890")
    song_data = songs.get_all()
    band_data = get_bands_all()


refresh_data()


@on_event.message_created
def guess_bang_chart(session: SessionExtension):
    print(session.function.cutshort.cutshort_dict)
    session.function.register(["猜谱面", "猜谱", "cpm", "谱面挑战"])  # 注册函数，抹掉上一个插件带来的属性
    session.function.description = "zhaomaoniu写的猜谱面游戏"  # 功能描述
    session.function.examples.add(None, "开始猜谱面").add('提示', '展示提示').add('结束', '结束游戏')   # 功能示例（参数）
    (session.function.cutshort
     .add(('-e', 'end', '结束', 'bzd'), 'bzd')
     .add(("-t", "tips", "提示", "给点提示"), ['提示', '给点提示']))  # cutshort 回复bot一个值，快捷调用 「指令 + 指定参数」（参数需要和 action 中的参数一致）
    session.action({
        None: guess_chart,  # 无参数
        ('-e', 'end', '结束', 'bzd'): end,
        ("-t", "tips", "提示", "给点提示"): tips,
        'su': send_guess_chart_context,
    }).action(handle_answer)  # action 用于最终执行函数，当参数类型为 dict 时，key 为参数，value 为函数，按照参数匹配执行对应的函数
    session.function.cutshort.add(None)  # 注意，这里的 None 表示执行action里面的 None 函数，而第二个值没有填，代表任何回复都可以触发
    session.action({
        None: handle_answer,  # 无参数
    })


def send_guess_chart_context(session: SessionExtension):
    # 测试用
    global guess_chart_context
    global nickname_song
    global song_data
    global band_data

    print(session.data)

    if session.channel.id not in guess_chart_context:
        print("没有在猜谱面")
        return None
    if session.user.id not in admin_list:
        print("不是管理员")
        return None
    correct_chart_id, diff, level, song_name = get_msgs(session)
    session.send(f"谱面：{song_name} " f"{diff.upper()} LV.{level}")
    return None


def guess_chart(session: SessionExtension):
    global song_data
    global guess_chart_context

    if session.channel.id in guess_chart_context:
        session.send("你已经在猜谱面了哦")
        return None
    guess_chart_context[session.channel.id] = {}  # 初始化，防止短时间内多次触发
    session.send("正在加载谱面...")

    game_difficulty: str = get_difficulty(session.message.command.args)

    if not song_data:
        # song_data = songs.get_all(proxy="http://127.0.0.1:7890")
        song_data = songs.get_all()

    song_id, song_info = random.choice(list(song_data.items()))

    # song_detail = songs.Song(song_id, proxy="http://127.0.0.1:7890")
    song_detail = songs.Song(song_id)

    if song_data[song_id]["difficulty"].get(diff_num["special"]):
        chart_difficulty = random.choice(["expert", "special"])
    else:
        chart_difficulty = "expert"

    # chart = Chart.get_chart(song_id, chart_difficulty, proxy="http://127.0.0.1:7890")
    chart = Chart.get_chart(song_id, chart_difficulty)

    if song_info["difficulty"][diff_num[chart_difficulty]]["playLevel"] <= 27:
        img = render(chart.to_list())
    else:
        # TODO: 改为渲染不完整的谱面
        img = render(chart.to_list())

    guess_chart_context[session.channel.id] = {
        "chart_id": song_id,
        "chart_difficulty": chart_difficulty,
        "game_difficulty": game_difficulty,
        "song": song_info,
        "chart": chart,
        "song_detail": song_detail.get_info(),
        "prompt": {
            "level": False,
            "band": False,
        },
    }
    session.send(h.image(img) + '发送/猜谱面 ID/名称 回答\n发送/猜谱面 提示 展示提示\n发送/猜谱面 结束 结束游戏')


def get_msgs(session: SessionExtension):
    '''
    Args:
        session: SessionExtension

    Returns:
        correct_chart_id: 正确谱面的ID
        diff: 谱面难度
        level: 谱面等级
        song_name: 歌曲名称
    '''
    global guess_chart_context
    global nickname_song
    global song_data
    global band_data

    correct_chart_id: str = guess_chart_context[session.channel.id]["chart_id"]
    diff: str = guess_chart_context[session.channel.id]["chart_difficulty"]
    level = guess_chart_context[session.channel.id]["song"]["difficulty"][
        diff_num[diff]
    ]["playLevel"]
    song_name = get_value_from_list(
        guess_chart_context[session.channel.id]["song"]["musicTitle"]
    )
    return correct_chart_id, diff, level, song_name


def handle_answer(session: SessionExtension):
    global guess_chart_context
    global nickname_song
    global song_data
    global band_data
    # msg_pure = rm_all_xml(session.message.content)
    # msg_pure = rm_perfix(msg_pure)
    msg_pure = session.message.command.args[0]
    if session.channel.id not in guess_chart_context:
        return None
    if not msg_pure.isdigit():
        guessed_chart_id = fuzzy_match(msg_pure, nickname_song)
        if guessed_chart_id is None:
            guessed_chart_id = compare_origin_songname(msg_pure, song_data)
    else:
        guessed_chart_id = msg_pure
    correct_chart_id, diff, level, song_name = get_msgs(session)
    if correct_chart_id == guessed_chart_id:
        guess_chart_context.pop(session.channel.id)
        session.send("回答正确！" f"谱面：{song_name} " f"{diff.upper()} LV.{level}")
    else:
        session.send("？你回答的什么几把")


def end(session: SessionExtension):
    global guess_chart_context
    global nickname_song
    global song_data
    global band_data
    correct_chart_id, diff, level, song_name = get_msgs(session)
    guess_chart_context.pop(session.channel.id)

    session.send(f"要再试一次吗？\n谱面：{song_name} " f"{diff.upper()} LV.{level}")
    song_ = Song(int(correct_chart_id))
    s = song_.get_jacket()
    session.send(h.image(s[0].bytes))
    return None


def tips(session: SessionExtension):
    global guess_chart_context
    global nickname_song
    global song_data
    global band_data
    correct_chart_id, diff, level, song_name = get_msgs(session)

    if not guess_chart_context[session.channel.id]["prompt"]["level"]:
        session.send(f"这首曲子是 {level} 级的哦")
        guess_chart_context[session.channel.id]["prompt"]["level"] = True
    elif not guess_chart_context[session.channel.id]["prompt"]["band"]:
        if not band_data:
            # band_data = get_bands_all(proxy="http://127.0.0.1:7890")
            band_data = get_bands_all()

        band_id: int = guess_chart_context[session.channel.id]["song_detail"][
            "bandId"
        ]
        band_name = get_value_from_list(band_data[str(band_id)]["bandName"])

        session.send(f"这首曲子是 {band_name} 的哦")

        guess_chart_context[session.channel.id]["prompt"]["band"] = True
    else:
        session.send("已经没有提示啦")
    return None

