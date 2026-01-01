import csv
import re
import pandas as pd
from collections import defaultdict

def extract_mentions(text):
    """メッセージ内のメンションを抽出する関数"""
    if not isinstance(text, str):
        return []
    
    # メンションのパターン: <@UXXXXXXXX>
    pattern = r'<@(U[A-Z0-9]+)>'
    mentions = re.findall(pattern, text)
    
    # 'all'や'here'は除外
    filtered_mentions = [mention for mention in mentions if mention.lower() not in ['all', 'here']]
    return filtered_mentions

def calculate_average(values):
    """-1や空の値を除外して平均を計算する関数"""
    valid_values = [float(val) for val in values if val and val != '-1' and val != '']
    if not valid_values:
        return ''
    return round(sum(valid_values) / len(valid_values), 2)

def main():
    # 入力と出力のファイルパス
    input_file = '農林中金デモ_チャット分析 - 送信者あり_点数定義 (1).csv'
    output_file = 'result.csv'
    
    # CSVファイルの読み込み（エンコーディングを指定）
    try:
        # 結果を格納するデータ構造
        # {送信者: {受信者: {'期待支援力': [値のリスト], '行動支援力': [値のリスト], ...}}}
        data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        
        # 列のインデックスを固定で設定
        sender_idx = 0  # 送信者は最初のカラム
        chat_idx = 1    # チャットメッセージは2番目のカラム
        
        # 評価指標のインデックスを直接指定
        metric_indices = {
            '期待支援力': 2,
            '行動支援力': 3,
            '指示が明確か': 4,
            '責任が明確か': 5,
            '言い回し力': 6
        }
        
        print("メトリックインデックス:", metric_indices)
        
        # CSVファイルを読み込む
        with open(input_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            headers = next(reader)  # ヘッダー行をスキップ
            
            # 各行を処理
            line_count = 0
            mention_count = 0
            
            for row in reader:
                line_count += 1
                
                if len(row) <= 1:  # 空行または不正な行はスキップ
                    continue
                
                sender = row[sender_idx] if len(row) > sender_idx else ""
                if not sender:  # 送信者が空の場合はスキップ
                    continue
                
                chat_text = row[chat_idx] if len(row) > chat_idx else ""
                mentions = extract_mentions(chat_text)
                
                # メンションがない場合は次の行へ
                if not mentions:
                    continue
                
                mention_count += 1
                
                # 評価指標の値を取得
                metrics_values = {}
                for metric, idx in metric_indices.items():
                    if len(row) > idx:
                        value = row[idx].strip() if row[idx] else ""
                        metrics_values[metric] = value
                    else:
                        metrics_values[metric] = ""
                
                # デバッグ出力
                if mention_count <= 5:  # 最初の5件だけ表示
                    print(f"行 {line_count}: 送信者={sender}, 受信者={mentions}, 指標={metrics_values}")
                
                # 各受信者に対してデータを格納
                for mention in mentions:
                    for metric, value in metrics_values.items():
                        data[sender][mention][metric].append(value)
            
            print(f"処理行数: {line_count}, メンションがある行数: {mention_count}")
        
        # デバッグ: データ構造の内容を確認 (一部のみ表示)
        print("\nデータ構造の内容 (一部):")
        count = 0
        for sender, receivers in data.items():
            if count >= 3:  # 最初の3人の送信者のみ表示
                break
            count += 1
            for receiver, metrics in receivers.items():
                print(f"送信者: {sender}, 受信者: {receiver}")
                for metric, values in metrics.items():
                    print(f"  {metric}: {len(values)}個の値")
        
        # 平均値を計算して結果を作成
        results = []
        for sender, receivers in data.items():
            for receiver, metrics in receivers.items():
                row = {
                    '送信者': sender,
                    '受信者': receiver
                }
                for metric, values in metrics.items():
                    row[metric] = calculate_average(values)
                results.append(row)
        
        # 結果をDataFrameに変換
        df = pd.DataFrame(results)
        
        # データがあるか確認
        if df.empty:
            print("警告: 結果のデータフレームが空です。メンションを含むデータが見つかりませんでした。")
        else:
            print(f"データ件数: {len(df)}行")
            print("DataFrame先頭5行:")
            print(df.head())
        
        # CSVヘッダーと結果をそれぞれ書き込む
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            
            # ヘッダー行を書き込む
            headers = ['送信者', '受信者', '期待支援力', '行動支援力', '指示が明確か', '責任が明確か', '言い回し力']
            writer.writerow(headers)
            
            # データ行を書き込む
            for _, row in df.iterrows():
                writer.writerow([
                    row['送信者'],
                    row['受信者'],
                    row['期待支援力'],
                    row['行動支援力'],
                    row['指示が明確か'],
                    row['責任が明確か'],
                    row['言い回し力']
                ])
        
        print(f'結果が{output_file}に保存されました')
    
    except Exception as e:
        import traceback
        print(f"エラーが発生しました: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    main() 