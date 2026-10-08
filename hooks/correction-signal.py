#!/usr/bin/env python3
"""UserPromptSubmit hook: detect a correction/complaint signal in the user's
message and remind the model to run the learn-from-correction pipeline.
Silent (no output) when no signal is found."""
import sys, re, json

try:
    raw = sys.stdin.read()
except Exception:
    sys.exit(0)

try:
    d = json.loads(raw)
    text = d.get("prompt") or d.get("user_prompt") or d.get("message") or raw
except Exception:
    text = raw

t = str(text).lower()

# Correction / complaint signals (RU). Word-ish boundaries where a bare
# stem would over-match.
SIGNAL = re.compile(
    r"неправильн|некорректн|ошибк|ошибся|ошиблась|"
    r"ты не так|\bне то\b|\bопять\b|почему ты|"
    r"я же (говорил|сказал|сказала|просил|просила)|"
    r"на самом деле|вообще-то|это не так|это неверно|"
    r"не должен был|не должна была|зачем ты|"
    r"фактическая ошибка|ты (дурак|тупой|дебил|тупишь)|не так сделал|переделай|"
    r"перепутал|переврал|наврал|додумал|притянул"
)

if SIGNAL.search(t):
    msg = (
        "⚠️ Обнаружен корректирующий сигнал в сообщении пользователя. "
        "Прежде чем отвечать — вызови скилл learn-from-correction (Skill tool) и "
        "пройди шаги 0–5 скилла: признать → исправить все похожие места → "
        "понять класс ошибки → записать урок в файл → строка в ~/.claude/corrections-log.md. "
        "Если это НЕ претензия к качеству, а обычная итерация "
        "(«сделай короче», «добавь X», уточняющий вопрос, новая задача) — "
        "пайплайн НЕ запускать."
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": msg
        }
    }))
