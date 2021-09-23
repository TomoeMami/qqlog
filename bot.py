import mirai as mi
if __name__ == '__main__':
    bot = mi.Mirai(
        qq=3337523821, # 改成你的机器人的 QQ 号
        adapter=mi.WebSocketAdapter(
            verify_key='yirimirai', host='localhost', port=8080
        )
    )

    @bot.on(mi.FriendMessage)
    def on_friend_message(event: mi.FriendMessage):
        if str(event.message_chain) == '你好':
            return bot.send(event, 'Hello, World!')
    @bot.on(mi.RequestEvent.BotInvitedJoinGroupRequestEvent)
    def on_group_invited(event: mi.RequestEvent.BotInvitedJoinGroupRequestEvent):
        if str(event.from_id) == '1747222904':
            print(str(event.group_name))
    bot.run()
