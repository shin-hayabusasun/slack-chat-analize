import json
import csv
import os
import pandas as pd
import re

# JSONファイルが格納されているディレクトリ
json_dir = r"C:\Users\looka\Downloads\lbs-pf-dx診断サービス (2)\lbs-pf-dx診断サービス"

# 出力CSVファイル
output_csv = "農林中金デモ_チャット分析 - 送信者あり_点数定義.csv"

# テキストの正規化関数
def normalize_text(text):
    if not isinstance(text, str):
        return ""
    # 空白と改行を削除
    text = re.sub(r'\s+', ' ', text).strip()
    return text

print(f"既存のCSVファイルを読み込んでいます: {output_csv}")

# 既存のCSVファイルを読み込む
df = pd.read_csv(output_csv)

# B列のテキストを取得
texts_in_csv = df.iloc[:, 1].tolist()
normalized_texts_in_csv = [normalize_text(text) for text in texts_in_csv]

print(f"CSVから {len(texts_in_csv)} 行のテキストを読み込みました")

# ユーザー情報を格納する辞書を作成
user_text_map = {}
channel_join_map = {}
matches_count = 0

# JSONファイルからユーザー情報を抽出
print(f"JSONディレクトリを処理しています: {json_dir}")
for filename in os.listdir(json_dir):
    if not filename.endswith('.json'):
        continue
    
    file_path = os.path.join(json_dir, filename)
    print(f"処理中: {filename}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            for item in data:
                # 通常のメッセージ
                if 'text' in item and 'user' in item:
                    text = item['text']
                    user = item['user']
                    user_text_map[text] = user
                    user_text_map[normalize_text(text)] = user
                
                # チャンネル参加メッセージ
                if 'subtype' in item and item['subtype'] == 'channel_join' and 'text' in item and 'user' in item:
                    text = item['text']
                    user = item['user']
                    channel_join_map[text] = user
                    channel_join_map[normalize_text(text)] = user
                    
        except json.JSONDecodeError:
            print(f"JSONのデコードエラー: {file_path}")
        except Exception as e:
            print(f"ファイル処理エラー: {file_path}, エラー: {str(e)}")

print(f"JSONから {len(user_text_map)} 件のメッセージと {len(channel_join_map)} 件のチャンネル参加メッセージを抽出しました")

# CSVファイルのB列に対応するユーザーをA列に設定
for i, (text, norm_text) in enumerate(zip(texts_in_csv, normalized_texts_in_csv)):
    if text in user_text_map:
        df.iloc[i, 0] = user_text_map[text]
        matches_count += 1
    elif norm_text in user_text_map:
        df.iloc[i, 0] = user_text_map[norm_text]
        matches_count += 1
    elif text in channel_join_map:
        df.iloc[i, 0] = channel_join_map[text]
        matches_count += 1
    elif norm_text in channel_join_map:
        df.iloc[i, 0] = channel_join_map[norm_text]
        matches_count += 1
    # チャンネル参加のパターンの検出
    elif isinstance(text, str) and "さんがチャンネルに参加しました" in text:
        user_id_match = re.search(r'<@([A-Z0-9]+)>', text)
        if user_id_match:
            df.iloc[i, 0] = user_id_match.group(1)
            matches_count += 1

print(f"全 {len(texts_in_csv)} 行中 {matches_count} 行にユーザーIDを割り当てました")

# 更新したデータフレームをCSVに書き込む
df.to_csv(output_csv, index=False)

print(f"{output_csv} が更新されました。") 