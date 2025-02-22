import os
import pandas as pd
from fuzzywuzzy.string_processing import string

#对比文件夹里面的歌曲文件和存储的歌曲信息是否一致11111111111111111111111
def find_missing_songs(csv_file, folder_path):
    # 读取CSV文件，假设第一列是ID，第二列是歌曲名
    df = pd.read_csv(csv_file)
    # 获取第二列的歌曲名，并去除空白字符和空值
    csv_songs = df.iloc[:, 1].dropna().str.strip()
    # 获取第一列的ID
    csv_ids = df.iloc[:, 0]

    # 创建一个字典，将歌曲名映射到对应的ID
    song_to_id = dict(zip(csv_songs, csv_ids))

    # 获取文件夹中的所有歌曲文件（支持 .mp3 和 .ncm 文件）
    folder_songs = set()
    for file in os.listdir(folder_path):
        if file.endswith((".mp3", ".ncm")):  # 支持 .mp3 和 .ncm 文件
            # 提取 - 之后的部分作为歌曲名
            song_name = file.rsplit(".", 1)[0].strip()
            folder_songs.add(song_name)

            # 如果歌曲名在CSV中，则重命名文件
            if song_name in song_to_id:
                # 获取对应的ID
                song_id = song_to_id[song_name]
                # 构建新的文件名
                new_name = string(song_id)
                # 获取文件的完整路径
                old_file_path = os.path.join(folder_path, file)
                new_file_path = os.path.join(folder_path, new_name + os.path.splitext(file)[1])
                # 重命名文件
                os.rename(old_file_path, new_file_path)
                print(f"重命名文件: {file} -> {new_name}")

    # 找出缺少的歌曲
    missing_songs = set(csv_songs) - folder_songs

    # 输出结果
    if missing_songs:
        print("缺少的歌曲文件：")
        for song in missing_songs:
            print(song)
    else:
        print("没有缺少的歌曲文件。")

if __name__ == "__main__":
    # CSV文件路径
    csv_file = "songs33.csv"
    # 文件夹路径
    folder_path = r"E:\CloudMusic\VipSongsDownload\song"

    # 调用函数查找缺少的歌曲
    find_missing_songs(csv_file, folder_path)