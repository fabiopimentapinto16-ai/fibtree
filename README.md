FibTree

Merkle tree with Fibonacci branching for Delay-Tolerant Networks.

https://zenodo.org/badge/DOI/10.5281/zenodo.22863541.svg
https://zenodo.org/badge/DOI/10.5281/zenodo.22861639.svg
https://zenodo.org/badge/DOI/10.5281/zenodo.22858947.svg
https://img.shields.io/badge/License-MIT-yellow.svg

What is FibTree?

FibTree is a data structure for distributing large datasets over networks with intermittent connectivity. Unlike flat structures (BitTorrent) or binary Merkle trees (Bitcoin, Git), FibTree organizes data in a hierarchy where each node has F(n) children, with F being the Fibonacci sequence.

Key properties

· Partial verification in O(log n)
· Differential sync between peers: 60–95% bandwidth savings
· Hierarchical resilience: subtrees survive parent loss
· Per-message end-to-end encryption (X25519 + AES-256-GCM)
· Works over Wi-Fi Direct, BLE, LoRa, 4G — anything

Papers

· v3.0 (English, with E2EE): 10.5281/zenodo.22863541
· v2.0 (English, with experimental validation): 10.5281/zenodo.22861639
· v1.0 (Portuguese, original theoretical analysis): 10.5281/zenodo.22858947

Authors

· Fabio Pimenta Pinto — Independent Researcher
· Flávia Christini de Lima Pinto — Independent Researcher

Experimental results (v3.0)

6,000 simulations across 6 channel loss scenarios:

Metric FibTree Flat RS(10,15)
Delivery at p=0.5 98.9% 14.5%
Delivery at p=0.7 83.8% 0.5%
Latency (p=0.5) 157 ms 1000 ms
Overhead (optimized) -33.8% to 128% 50%

Average gain: +52.85 percentage points.

End-to-end encryption

FibTree v3.0 includes per-message E2EE based on:

· X25519 (ECDH key agreement, RFC 7748)
· Ed25519 (signatures, RFC 8032)
· HKDF-SHA256 (key derivation, RFC 5869)
· AES-256-GCM (authenticated encryption, NIST SP 800-38D)

Validated with three scenarios proving that only the intended recipient can decrypt the message. This feature was proposed by co-author Flávia Christini de Lima Pinto.

Use cases

Domain Pain FibTree gain
AI model distribution 810 GB downloads 60–80% bandwidth reduction
OTA vehicle updates Re-download on failure Incremental by level
Blockchain block relay Orphan blocks cost $200k 20–40% faster propagation
Space communication Minutes of latency Partial delivery per window
Offline mesh Short encounters Reconstruct from fragments
Repository sync Full clone Only diverging branches
Industrial IoT LoRaWAN 0.3-50 kbps Hierarchical updates

Status

☑ Formal specification
☑ Reference implementation in Kotlin
☑ Reference implementation in Python
☑ Theoretical analysis
☑ Experimental validation (6,000 simulations)
☑ Overhead optimization techniques
☑ End-to-end encryption (validated)
☐ Field deployment with real devices

Contributing

Pull requests welcome. For major changes, please open an issue first.

License

MIT — free for commercial and non-commercial use.

---

FIM

