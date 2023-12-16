import csv
import random
from PIL import Image
from fuzzywuzzy import process
from typing import List, Dict, Any, TypedDict
from bestdori import songs
from bestdori.utils import get_bands_all
from bestdori.charts import Chart, Statistics
from bestdori.songs import Song

from bridge.tomorin import on_activator, on_event, h, admin_list
from bridge.session_adder import SessionExtension

from .BanGDreamChartRender import render, non_slice_render
from .BanGDreamChartRender.config import PPS


proxy = "http://127.0.0.1:7890"
# 不需要写 None 即可


class GuessChartContext(TypedDict):
    chart_id: str
    chart_difficulty: str
    game_difficulty: str
    song: Dict[str, Song]
    chart: Chart
    chart_statistics: Statistics
    song_detail: Dict[str, Any]
    prompt: Dict[str, bool]


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


def render_to_slices(chart: list) -> Image.Image:
    chart_img = non_slice_render(chart)

    height = chart_img.height
    # 每个切片展示 5s 的谱面
    slice_height = PPS * 5

    # 随机抽取三段不重复的部分进行切片
    slices = Image.new("RGB", (chart_img.width * 3, slice_height), (255, 255, 255, 255))
    for i in range(3):
        start = random.randint(0, height - slice_height)
        slices.paste(
            chart_img.crop((0, start, chart_img.width, start + slice_height)),
            (i * chart_img.width, 0),
        )
    return slices


def compare_origin_songname(guessed_name: str, song_data: Dict[str, Dict[str, Any]]):
    for key, data in song_data.items():
        if guessed_name in data["musicTitle"]:
            return key
    return None


def num_to_range(num: int):
    """将数字转换为区间

    e.g. 233 -> tuple(200, 300)
    """
    start = num // 100 * 100
    end = start + 100
    return start, end


def get_value_from_list(song_names: List[str]):
    return (
        song_names[3]
        or song_names[0]
        or song_names[2]
        or song_names[1]
        or song_names[4]
    )


guess_chart_context: Dict[str, GuessChartContext] = {}
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
    song_data = songs.get_all(proxy=proxy)
    band_data = get_bands_all(proxy=proxy)


refresh_data()


@on_event.message_created
def guess_bang_chart(session: SessionExtension):
    print(session.function.cutshort.cutshort_dict)
    session.function.register(["猜谱面", "猜谱", "cpm", "谱面挑战"])  # 注册函数，抹掉上一个插件带来的属性
    session.function.description = "zhaomaoniu写的猜谱面游戏"  # 功能描述
    session.function.examples.add(None, "开始猜谱面").add("提示", "展示提示").add(
        "结束", "结束游戏"
    )  # 功能示例（参数）
    (
        session.function.cutshort.add(("-e", "end", "结束", "bzd"), "bzd").add(
            ("-t", "tips", "提示", "给点提示"), ["提示", "给点提示"]
        )
    )  # cutshort 回复bot一个值，快捷调用 「指令 + 指定参数」（参数需要和 action 中的参数一致）
    session.action(
        {
            None: guess_chart,  # 无参数
            ("-e", "end", "结束", "bzd"): end,
            ("-t", "tips", "提示", "给点提示"): tips,
            "su": send_guess_chart_context,
        }
    ).action(
        handle_answer
    )  # action 用于最终执行函数，当参数类型为 dict 时，key 为参数，value 为函数，按照参数匹配执行对应的函数
    session.function.cutshort.add(
        None
    )  # 注意，这里的 None 表示执行action里面的 None 函数，而第二个值没有填，代表任何回复都可以触发
    session.action(
        {
            None: handle_answer,  # 无参数
        }
    )


def send_guess_chart_context(session: SessionExtension):
    # 测试用
    global guess_chart_context
    global nickname_song
    global song_data
    global band_data

    # print(session.data)

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
        song_data = songs.get_all(proxy=proxy)

    song_id, song_info = random.choice(list(song_data.items()))

    song_detail = songs.Song(song_id, proxy=proxy)

    if song_data[song_id]["difficulty"].get(diff_num["special"]):
        chart_difficulty = random.choice(["expert", "special"])
    else:
        chart_difficulty = "expert"

    chart = Chart.get_chart(song_id, chart_difficulty, proxy=proxy)
    chart_statistics = chart.count()

    if song_info["difficulty"][diff_num[chart_difficulty]]["playLevel"] <= 27:
        img = render(chart.to_list())
    else:
        img = render_to_slices(chart.to_list())

    guess_chart_context[session.channel.id] = {
        "chart_id": song_id,
        "chart_difficulty": chart_difficulty,
        "game_difficulty": game_difficulty,
        "song": song_info,
        "chart": chart,
        "chart_statistics": chart_statistics,
        "song_detail": song_detail.get_info(),
        "prompt": {
            "level": False,
            "band": False,
            "notes": False,
            "bpm": False,
        },
    }
    session.send(h.image(img) + "help: @Kasumi /猜谱面 帮助")


def get_msgs(session: SessionExtension):
    """
    Args:
        session: SessionExtension

    Returns:
        correct_chart_id: 正确谱面的ID
        diff: 谱面难度
        level: 谱面等级
        song_name: 歌曲名称
    """
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
    # else:
    #     session.send("？你回答的什么几把")


def end(session: SessionExtension):
    global guess_chart_context
    global nickname_song
    global song_data
    global band_data
    if session.channel.id not in guess_chart_context:
        return None

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
    elif not guess_chart_context[session.channel.id]["prompt"]["notes"]:
        note_num = guess_chart_context[session.channel.id]["chart_statistics"].notes
        note_num_range = num_to_range(note_num)
        session.send(f"这首曲子的物量是 {note_num_range[0]} 到 {note_num_range[1]} 哦")
        guess_chart_context[session.channel.id]["prompt"]["notes"] = True
    elif not guess_chart_context[session.channel.id]["prompt"]["band"]:
        if not band_data:
            band_data = get_bands_all(proxy=proxy)

        band_id: int = guess_chart_context[session.channel.id]["song_detail"]["bandId"]
        band_name = get_value_from_list(band_data[str(band_id)]["bandName"])

        session.send(f"这首曲子是 {band_name} 的哦")

        guess_chart_context[session.channel.id]["prompt"]["band"] = True
    else:
        session.send("已经没有提示啦")
    return None
