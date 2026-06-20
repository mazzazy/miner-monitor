from app.api.braiins import BraiinsAPI
from app.services.reporter import Reporter

api = BraiinsAPI()

workers = api.fetch_workers()

reporter = Reporter()

reporter.save_snapshot(workers)

print(reporter.generate_summary(workers))