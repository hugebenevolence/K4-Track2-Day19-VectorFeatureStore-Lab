# Docker path validation

Tested on Windows / Python 3.13 with Docker Desktop (2026-10-05). The submitted
`notebooks/*.ipynb` retain their Lite outputs; Docker notebooks were executed
separately so both paths were checked without replacing the Lite evidence.

| Check | Observed result |
|---|---:|
| Qdrant, Redis, PostgreSQL | all healthy; `verify_docker.py` passed |
| NB1 / Qdrant server | `bge-m3`, 1024 dimensions, 1,000 vectors indexed |
| NB2 / 50 golden queries | BM25 77.8%, vector 95.2%, hybrid RRF 89.0% Precision@10 |
| NB2 / 15 paraphrases | BM25 33.3%, vector 86.7%, hybrid 66.7% Precision@10 |
| NB4 / PostgreSQL | 100 user, 1,000 item, 100 query-velocity rows loaded |
| NB4 / Redis | all five requested online features populated; lookup P99 7.47 ms (100 calls) |
| NB4 / PIT join | three historical rows returned with the expected values |
| FastAPI / Qdrant server | `/search` HTTP 200, relevant cloud hits |
| FastAPI / persistent index | second process reused the 1,000-vector index in 0.4 s |

The Lite API meets the lab's P99 < 50 ms target (14.3 ms in the submitted
notebook). With `bge-m3` on this CPU, the Docker API's first query took about
13 s while loading the model; five subsequent requests had median 181 ms.
This is a measured latency tradeoff for the much stronger multilingual model,
not a claim that Docker meets the Lite API latency threshold. The Docker Feast
online lookup did remain below its 10 ms target.

To reproduce: run `setup-docker.sh` (or the PowerShell steps in the README),
then execute NB4, NB1, NB2 in that order. The two paths use separate Feast
registry files so switching back to Lite does not carry over a materialization
timestamp from Docker.
