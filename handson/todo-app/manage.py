from todoapp import app
from todoapp.models import Todo, User, Tab
import todoapp.views
from apscheduler.scheduler import Scheduler
from flask import session, g
import requests
import datetime

cron = Scheduler(daemon=True)
cron.start()


# Slack_API
class SlackDriver:

    def __init__(self):
        self._token = 'xoxp-1245463732644-1224536410103-1239501050850-2c7a70eca450a090df37c9a5711698aa'
        self._headers = {'Content-Type': 'application/json'}

    def send_message(self, message, channel):
        params = {"token": self._token, "channel": channel, "text": message}

        r = requests.post('https://slack.com/api/chat.postMessage',
                          headers=self._headers,
                          params=params)
        print("return ", r.json())


slack = SlackDriver()


@cron.interval_schedule(minutes=15)
def slack():
    tasks = Todo.query.filter(Todo.deadline == datetime.date.today(),
                              Todo.completed == False).order_by(
        Todo.date_created).all()

    tasks_num = len(tasks)

    if tasks_num == 0:
        slack.send_message('今日は完璧!!!!', "#random")
    else:
        for i in tasks:
            print(i.content)
            slack.send_message('期限が近いタスクがあります。' \
                               + i.content, "#random")  # 部屋が一つのため全ユーザーに通知が行く(良くない)


if __name__ == '__main__':
    tasks = Todo.query.filter(Todo.deadline == datetime.date.today(),
                              Todo.completed == False).order_by(
        Todo.date_created).all()
    token = ''  # TODO your token.
    slack = SlackDriver()
    # slack.send_message('Todolistからのお知らせ', "#random")

app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
