from channels.generic.http import AsyncHttpConsumer, StopConsumer
import json
from celery.result import AsyncResult
import asyncio


class ServerSentEventsConsumer(AsyncHttpConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keepalive = False

    async def handle(self, body):
        await self.send_headers(headers=[
            (b'Cache-Control', b'no-cache'),
            (b'Content-Type', b'text/event-stream'),
            (b"Transfer-Encoding", b"chunked"),
            (b'Access-Control-Allow-Origin', b'*'),
        ])
        task_id = json.loads(body)['task_id']
        task = AsyncResult(task_id)
        
        if task.state == 'FAILURE' or task.state == 'PENDING':
            resp = {
                'state': task.state, 
                'progression': "None",
                'info': str(task.info)
                }
            await self.send_body(json.dumps(resp).encode('utf-8'), more_body=False)
        
        while task.state == 'PROGRESS':
            task = AsyncResult(task_id)
            current = task.info.get('current', 0)
            total = task.info.get('total')
            progression = int((current / total) * 100)
            resp = {
                'state': task.state, 
                'progression': progression
                }
            await asyncio.sleep(1)
            await self.send_body((json.dumps(resp) + '\n').encode('utf-8'), more_body=True)            

        if task.state == 'SUCCESS':
            resp = {
                'state': task.state, 
                'progression': 100,
                }
            await self.send_body((json.dumps(resp) + '\n').encode('utf-8'), more_body=False)

        await self.channel_layer.group_add('track', self.channel_name)

    async def send_body(self, body, *, more_body=False):
        if more_body:
            self.keepalive = True
        assert isinstance(body, bytes), "Body is not bytes"

        await self.send(
            {"type": "http.response.body", "body": body, "more_body": more_body}
        )

    async def http_request(self, message):
        if "body" in message:
            self.body.append(message["body"])
        if not message.get("more_body"):
            try:
                await self.handle(b"".join(self.body))
            finally:
                if not self.keepalive:
                    await self.disconnect()
                    raise StopConsumer()
