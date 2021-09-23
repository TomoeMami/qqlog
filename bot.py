from mirai import Mirai, WebSocketAdapter, FriendMessage
from mirai import RequestEvent
if __name__ == '__main__':
    bot = Mirai(
        qq=3337523821, # 改成你的机器人的 QQ 号
        adapter=WebSocketAdapter(
            verify_key='yirimirai', host='localhost', port=8080
        )
    )

    @bot.on(FriendMessage)
    def on_friend_message(event: FriendMessage):
        if str(event.message_chain) == '你好':
            return bot.send(event, 'Hello, World!')
    @bot.on(Event)
    def on_group_invited(event: Event):
        print(Event)
    bot.run()
