from google.cloud import storage
from google.cloud import tasks_v2
import asyncio
import json

cf = "https://us-central1-www-wowless-dev.cloudfunctions.net/addon-downloader"


async def do_publish():
    parent = (
        "projects/www-wowless-dev/locations/us-central1/queues/addon-downloads"
    )
    tasks_client = tasks_v2.CloudTasksAsyncClient()
    async for _ in await tasks_client.list_tasks(parent=parent):
        print("tasks are present, so nothing to do")
        return
    print("creating tasks...")
    await asyncio.gather(
        *[
            tasks_client.create_task(
                parent=parent,
                task={"http_request": {"url": f'{cf}?cfid={x["id"]}'}},
            )
            for x in json.loads(
                storage.Client()
                .bucket("wowless.dev")
                .blob("addons.json")
                .download_as_bytes()
            )["cf"]
        ]
    )
    print("created tasks")


def publish(_):
    asyncio.run(do_publish())
    return ""


if __name__ == "__main__":
    publish(None)
