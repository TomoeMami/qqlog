from mirai import Mirai, WebSocketAdapter, FriendMessage
from mirai.models.events import BotInvitedJoinGroupRequestEvent,MemberJoinRequestEvent
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
            
    @bot.on(BotInvitedJoinGroupRequestEvent)
    def on_group_invited(event: BotInvitedJoinGroupRequestEvent):
        if str(event.from_id) == '1747222904':
            return bot.allow(event)

    @bot.on(MemberJoinRequestEvent)
    def on_group_join(event: MemberJoinRequestEvent):
        print(str(event.group_name))
        print(str(event.nick))
        print(str(event.message))
        blocklist = ['']
        if(event.from_id in blocklist):
            return bot.decline(event, '您已被加入黑名单')
        else:
            return bot.allow(event)
    bot.run()
