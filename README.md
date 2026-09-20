**Hierarchical Merkle tree with Fibonacci branching for Delay-Tolerant Networks.**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22858947.svg)](https://doi.org/10.5281/zenodo.22858947)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## What is FibTree?

FibTree is a data structure for distributing large datasets over networks with intermittent connectivity. Unlike flat structures (BitTorrent) or binary Merkle trees (Bitcoin, Git), FibTree organizes data in a hierarchy where each node has F(n) children, with F being the Fibonacci sequence.

## Key properties

- Partial verification in O(log n)
- Differential sync between peers: 60–95% bandwidth savings
- Hierarchical resilience: subtrees survive parent loss
- Works over Wi-Fi Direct, BLE, LoRa, 4G — anything

## Paper

Read the full paper (DOI: [10.5281/zenodo.22858947](https://doi.org/10.5281/zenodo.22858947))

## Why Fibonacci?

Fibonacci grows faster than linear (allowing larger groupings at top levels) but slower than powers of 2 (avoiding metadata explosion). This makes it ideal for data with natural hierarchical structure.

## Use cases

| Domain | Pain | FibTree gain |
|---|---|---|
| AI model distribution | 810 GB downloads | 60–80% bandwidth reduction |
| OTA vehicle updates | Re-download on failure | Incremental by level |
| Blockchain block relay | Orphan blocks cost $200k | 20–40% faster propagation |
| Space communication | Minutes of latency | Partial delivery per window |
| Offline mesh | Short encounters | Reconstruct from fragments |
| Repository sync | Full clone | Only diverging branches |

## Theoretical results

| Metric | Fibonacci (L=5) | RS flat (10,15) |
|---|---|---|
| Overhead | 776% | 50% |
| P(delivery) at p=0.5 | 99.00% | 15.09% |
| P(delivery) at p=0.7 | 99.99% | 72.14% |
| Sync bandwidth saving | 80–95% | — |

Full analysis in the paper.

## Status

- [x] Formal specification
- [x] Reference implementation in Kotlin
- [x] Theoretical analysis
- [x] Paper published on Zenodo
- [ ] Empirical validation
- [ ] Production hardening

## Contributing

Pull requests welcome. For major changes, please open an issue first.

## License

MIT — free for commercial and non-commercial use.

## Author

Fabio Pimenta Pinto — Pesquisador Independente
