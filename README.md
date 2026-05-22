# 🍅 ポモドーロタイマー

ターミナルで動くシンプルなポモドーロタイマーです（Windows 専用）。

## 使い方

### ダブルクリックで起動
`start.bat` をダブルクリックするだけで起動します。

### コマンドラインで起動
```
python pomodoro.py
```

## キー操作

| キー | 動作 |
|------|------|
| `Enter` / `Space` | 開始 / 一時停止 |
| `s` | 現在のフェーズをスキップ |
| `q` | 終了 |

## タイマー設定

`pomodoro.py` の先頭にある定数を変更することで調整できます。

```python
WORK_MINUTES = 25          # 作業時間（分）
SHORT_BREAK_MINUTES = 5    # 短い休憩（分）
LONG_BREAK_MINUTES = 15    # 長い休憩（分）
LONG_BREAK_INTERVAL = 4    # 何ポモドーロごとに長い休憩を入れるか
```

## 必要環境

- Windows 10 / 11
- Python 3.x
