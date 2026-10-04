import threading

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from raquel import Raquel


def test_sqlite_file_backed_concurrent_claims_are_unique(tmp_path):
    db_path = tmp_path / "raquel.sqlite"
    queue = "sqlite-concurrency"
    expected_count = 25

    def make_raquel():
        engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            poolclass=NullPool,
        )
        return Raquel(engine)

    producer = make_raquel()
    producer.create_all()
    for index in range(expected_count):
        producer.enqueue(queue, {"index": index})

    claimed_ids: list[str] = []
    errors: list[str] = []
    lock = threading.Lock()

    def worker(worker_id: int):
        broker = make_raquel()
        while True:
            try:
                job = broker.claim(queue, claim_as=f"worker-{worker_id}")
                if not job:
                    return
                broker.resolve(job.id, attempt_num=max(1, job.attempts + 1))
                with lock:
                    claimed_ids.append(str(job.id))
            except Exception as exc:
                with lock:
                    errors.append(f"{type(exc).__name__}: {exc}")
                return

    threads = [threading.Thread(target=worker, args=(index,)) for index in range(5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert not errors
    assert len(claimed_ids) == expected_count
    assert len(set(claimed_ids)) == expected_count
    assert producer.count(queue, producer.SUCCESS) == expected_count
