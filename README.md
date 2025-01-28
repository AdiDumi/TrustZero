# TrustZero

This is the repository for the TrustZero master thesis, a scalable layer of zero-trust security
built around a universal ”trust token” - a non-revocable self sovereign identity with cryptographic signatures to enable robust, mathematically grounded trust attestation.

## Structure

- [app.py](app.py) - python application that uses flask to simulate a server accepting requests
- [check_signatures.py](check_signatures.py) - python script used by ModSecurity to verify signatures from requests
- [custom_rules.conf](custom_rules.conf) - custom rules used by ModSecurity to check requests/responses to servers
- [test](test) - directory with the test scripts that were used in experiments
- [results](results) - directory that stores the results of the experiments

## Experimental setup

TrustZero requires [docker](https://www.docker.com/) and python >= 3.8

In order to activate the environment used in experiments, the script `run.sh` needs execute permissions.
```sh
./run.sh
```
Running it, activates 5 docker containers that contain a running python server alongside a ModSecurity instance that works as a reverse proxy.
Now the experiments can be ran:
- [test1](test/test1.py) - comparison between 2 clients of their signature latencies(0 vs 5) on 500 requests
- [test2](test/test2.py) - measurements based on different behaviours of clients (honest vs malicious)
- [test3](test/test3.py) - very big experiment with deploying up to 2000 users in threads fo a DDoS scenario
- [signatures_test](test/signature_type_test.py) - test to plot the difference in storage in using different signature types
