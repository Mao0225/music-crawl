import pyautogui
import time
from PIL import Image
import cv2
import numpy as np

# 定义歌手数组及其对应的模板路径
singers = [
    ("Yuko", "templates/Yuko.png"),
    ("HOSHI", "templates/HOSHI.png"),
    ("ISavetheWRLD", "templates/ISavetheWRLD.png"),
    ("Hoki", "templates/Hoki.png"),
    ("042", "templates/042.png"),
    ("Eleven_Hour", "templates/Eleven_Hour.png"),
    ("mike", "templates/mike.png"),
    # ("YoUrceZ", "templates/YoUrceZ.png"),
    ("Level_L", "templates/Level_L.png"),
    ("WulanNoDead", "templates/WulanNoDead.png"),
    ("saltfish", "templates/saltfish.png"),
    ("KG-Broli", "templates/KG-Broli.png"),
    ("roger", "templates/roger.png"),
    ("dan", "templates/dan.png"),
    ("tree", "templates/tree.png"),
    ("Macknight", "templates/Macknight.png"),
]

# 标记已点击的歌手
clicked_singers = {singer: 0 for singer, _ in singers}

# 返回按钮模板路径
template_path_return = "return.png"
# 箭头按钮模板路径
template_path_arrow = "arrow.png"
# 下载按钮路径
download = "download.png"
# 添加按钮路径
addsong = "add.png"

# 设置最大翻页次数
max_scroll_count = 5
scroll_count = 0

# 步骤1: 使用 OpenCV 替代 PyAutoGUI 进行模板匹配
def locate_template_with_opencv(template_path, threshold=0.8):
    try:
        screenshot = pyautogui.screenshot()
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)

        if locations[0].size > 0:
            center_x = int(locations[1][0] + template.shape[1] / 2)
            center_y = int(locations[0][0] + template.shape[0] / 2)
            return (center_x, center_y)
        return None
    except Exception as e:
        print(f"错误：无法读取模板 {template_path}: {e}")
        return None

# 步骤2: 使用模板匹配识别歌手名称并点击
def find_and_click_singers(singers, clicked_singers):
    found_singers = []
    for singer, template_path in singers:
        if clicked_singers[singer] == 0:
            center = locate_template_with_opencv(template_path)
            if center:
                pyautogui.click(center)
                print(f"点击了 {singer} 位置: {center}")
                clicked_singers[singer] = 1
                found_singers.append(singer)
                break  # 重新扫描页面
    return found_singers

# 步骤3: 右键点击箭头按钮并进行相应操作
def right_click_arrows(template_path):
    max_scroll = 2
    scroll_count = 0

    while scroll_count < max_scroll:
        try:
            locations = list(pyautogui.locateAllOnScreen(template_path, confidence=0.6))
        except Exception as e:
            print(f"无法读取模板 {template_path}: {e}")
            locations = []

        if not locations:
            print("当前页面未找到箭头按钮，尝试滚动...")
            scroll_down()
            time.sleep(1)
            scroll_count += 1
            continue  # 继续下次滚动

        for location in locations:
            try:
                center = pyautogui.center(location)
                pyautogui.rightClick(center.x, center.y)
                print(f"右键点击了箭头位置: ({center.x}, {center.y})")
                time.sleep(1)

                try:
                    download_btn = pyautogui.locateOnScreen(download, confidence=0.7, minSearchTime=3)
                    if download_btn:
                        pyautogui.click(pyautogui.center(download_btn))
                        print("点击下载按钮")
                        time.sleep(1)
                    else:
                        print("未找到下载按钮")
                        continue
                except Exception as e:
                    print(f"下载按钮处理失败: {e}")

                try:
                    add_btn = pyautogui.locateOnScreen(addsong, confidence=0.7, minSearchTime=3)
                    if add_btn:
                        pyautogui.click(pyautogui.center(add_btn))
                        print("点击添加歌曲按钮")
                        time.sleep(1)
                    else:
                        print("未找到添加歌曲按钮")
                except Exception as e:
                    print(f"添加按钮处理失败: {e}")

            except Exception as e:
                print(f"处理箭头时发生错误: {e}")
                continue

        scroll_down()
        time.sleep(2)
        scroll_count += 1

    print("四次翻页结束")

# 步骤4: 模拟鼠标下滑操作
def scroll_down():
    global scroll_count
    screen_width, screen_height = pyautogui.size()
    center_x, center_y = screen_width // 2, screen_height // 2
    pyautogui.moveTo(center_x, center_y)
    pyautogui.scroll(-900)
    print("向下滚动")
    scroll_count += 1

# 步骤5: 执行自动化任务
def automate_task():
    print("请在5秒内切换到目标页面...")
    time.sleep(5)

    while True:
        found_singers = find_and_click_singers(singers, clicked_singers)

        if not found_singers:
            print("未找到新的可点击的歌手，准备滚动页面...")
            scroll_down()
            time.sleep(2)
            if scroll_count >= max_scroll_count:
                print(f"已达到最大翻页次数 ({max_scroll_count})，停止任务。")
                break
            continue

        for singer in found_singers:
            time.sleep(2)  # 等待页面加载
            right_click_arrows(template_path_arrow)
            time.sleep(2)  # 等待页面加载
            click_return_button(template_path_return)
            time.sleep(2)  # 等待页面加载

        all_clicked = all(clicked_singers.values())
        if all_clicked:
            break

    clicked = [singer for singer, clicked in clicked_singers.items() if clicked]
    not_clicked = [singer for singer, clicked in clicked_singers.items() if not clicked]

    print("\n点击过的歌手:")
    for singer in clicked:
        print(singer)

    print("\n未点击过的歌手:")
    for singer in not_clicked:
        print(singer)

# 步骤6: 点击返回按钮
def click_return_button(template_path):
    try:
        location = pyautogui.locateOnScreen(template_path, confidence=0.8)
        if location is not None:
            center = pyautogui.center(location)
            pyautogui.click(center.x, center.y)
            print(f"点击了返回按钮位置: ({center.x}, {center.y})")
            return True
        else:
            print("未找到返回按钮")
            return False
    except Exception as e:
        print(f"无法读取模板 {template_path}: {e}")
        return False

if __name__ == "__main__":
    automate_task()
