from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import csv
import os
import time

# 初始化浏览器驱动
service = Service('D:\\Download\\chromedriver-win64\\chromedriver.exe')
driver = webdriver.Chrome(service=service)
wait = WebDriverWait(driver, 15)

def switch_to_content_frame():
    """切换到内容框架"""
    try:
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "g_iframe")))
    except TimeoutException:
        print("无法定位内容框架")


def scrape_songs(artist_id):
    """爬取歌曲数据"""
    driver.get(f'https://music.163.com/#/artist?id={artist_id}')
    switch_to_content_frame()

    # 获取所有歌曲ID
    song_ids = []
    try:
        # 显式等待歌曲列表加载完成
        wait.until(EC.presence_of_element_located((By.XPATH, '//a[contains(@href, "/song?id=")]')))

        # 重新获取歌曲链接元素
        elements = driver.find_elements(By.XPATH, '//a[contains(@href, "/song?id=")]')
        for el in elements:
            try:
                href = el.get_attribute('href')
                if href and href not in song_ids:
                    song_ids.append(href.split('=')[-1])
            except StaleElementReferenceException:
                # 如果元素失效，重新获取元素
                elements = driver.find_elements(By.XPATH, '//a[contains(@href, "/song?id=")]')
                continue
    except TimeoutException:
        print("找不到歌曲列表")
        return []

    # 爬取每首歌曲详情
    songs_data = []
    print(f'歌曲id列表:{song_ids}')
    for song_id in song_ids:  # 爬取所有歌曲
        retry_count = 3  # 重试次数
        while retry_count > 0:
            try:
                driver.get(f'https://music.163.com/#/song?id={song_id}')
                print(f'获取歌曲id:{song_id}')
                switch_to_content_frame()
                time.sleep(1)
                song_info = {'song_id': song_id}
                # 标题
                song_info['title'] = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.tit em.f-ff2'))
                ).text

                # 歌手（可能有多个）
                artists = driver.find_elements(By.XPATH, '//p[@class="des s-fc4" and contains(., "歌手")]//a')
                song_info['artist'] = ' / '.join([a.text for a in artists])

                # 专辑
                song_info['album'] = wait.until(
                    EC.presence_of_element_located((By.XPATH, '//p[contains(., "所属专辑")]/a'))
                ).text

                # 点击展开按钮
                try:
                    expand_btn = driver.find_element(By.ID, 'flag_ctrl')
                    if "展开" in expand_btn.text:
                        driver.execute_script("arguments[0].click();", expand_btn)
                        time.sleep(1)  # 等待1秒，确保歌词加载完成
                except NoSuchElementException:
                    pass  # 如果没有展开按钮，直接跳过

                # 获取歌词内容
                lyric_content = wait.until(
                    EC.presence_of_element_located((By.ID, 'lyric-content'))
                )
                song_info['lyrics'] = lyric_content.text.replace('展开', '').replace('\n', ' ').replace('收起',
                                                                                                        '').strip()

                songs_data.append(song_info)
                print(f'已爬取歌曲: {song_info["title"]}')
                break  # 成功爬取后跳出重试循环
            except Exception as e:
                print(f"歌曲 {song_id} 爬取失败: {str(e)}，剩余重试次数: {retry_count - 1}")
                retry_count -= 1
                if retry_count == 0:
                    print(f"歌曲 {song_id} 爬取失败，跳过该歌曲")
                    break
                time.sleep(2)  # 重试前等待2秒

    return songs_data


def scrape_albums(artist_id):
    """爬取专辑数据"""
    driver.get(f'https://music.163.com/#/artist/album?id={artist_id}')
    switch_to_content_frame()

    # 获取所有专辑ID
    album_ids = []
    try:
        # 定位专辑列表的 ul 元素
        album_list = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//ul[@id="m-song-module" and contains(@class, "m-cvrlst-alb4")]')
        ))
        # 获取每个 li 中的专辑链接（只取第一个符合条件的 a 标签）
        album_links = album_list.find_elements(By.XPATH, './/li//a[contains(@href, "/album?id=")]')

        # 提取唯一的专辑 ID
        for link in album_links:
            href = link.get_attribute('href')
            if href:
                album_id = href.split('=')[-1]
                if album_id not in album_ids:
                    album_ids.append(album_id)
    except TimeoutException:
        print("找不到专辑列表")
        return []

    print(f'专辑id列表:{album_ids}')

    # 爬取每个专辑详情
    albums_data = []
    for album_id in album_ids:  # 爬取所有专辑
        print(f'爬取专辑id:{album_id}')
        driver.get(f'https://music.163.com/#/album?id={album_id}')
        switch_to_content_frame()

        album_info = {'album_id': album_id}
        try:
            # 封面图片
            img = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.cover img.j-img'))
            )
            album_info['cover_url'] = img.get_attribute('src') or img.get_attribute('data-src')

            # 专辑名称
            album_info['name'] = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'h2.f-ff2'))
            ).text

            # 歌手
            album_info['artist'] = wait.until(
                EC.presence_of_element_located((By.XPATH, '//p[@class="intr"]/span/a'))
            ).text

            # 发行时间
            release_text = wait.until(
                EC.presence_of_element_located((By.XPATH, '//p[contains(., "发行时间")]'))
            ).text
            album_info['release_date'] = release_text.split('：')[-1]

            # 专辑介绍
            album_info['description'] = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#album-desc-dot'))
            ).text.replace('\n', ' ')

        except Exception as e:
            print(f"专辑 {album_id} 信息不完整: {str(e)}")
            continue

        albums_data.append(album_info)
        print(f'已爬取专辑: {album_info["name"]}')

    return albums_data

def save_to_csv(data, filename):
    """保存数据到CSV"""
    if not data:
        return
    # 如果文件已存在，则以追加模式打开；否则创建新文件并写入表头
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        if not file_exists:  # 如果文件不存在，写入表头
            writer.writeheader()
        writer.writerows(data)

# 初始化文件路径
songs_filename = 'songs.csv'
albums_filename = 'albums.csv'

# 如果文件已存在，清空文件内容（避免重复数据）
open(songs_filename, 'w', encoding='utf-8-sig').close()
open(albums_filename, 'w', encoding='utf-8-sig').close()

if __name__ == "__main__":
    test_ids = ['57634422', '54684177', '57223695', '54824814', '50187982', '34400502', '52244832', '52235198',
                  '51826727', '51825616', '52274689', '54319722', '52013112', '37059888', '52102740', '50895706',
                  '61905310', '34592139', '51212896']

    for aid in test_ids:
        print(f'正在处理歌手ID: {aid}')

        # 爬取歌曲数据
        songs = scrape_songs(aid)
        save_to_csv(songs, songs_filename)

        # 爬取专辑数据
        albums = scrape_albums(aid)
        save_to_csv(albums, albums_filename)

    driver.quit()
    print("爬取任务完成")