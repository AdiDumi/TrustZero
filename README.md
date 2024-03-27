# IpRepMaster

Master thesis in progress for DDoS hardening using IP reputation.


Docker files needed for deployment of a server with ModSecurity rules and a container with Slowhttptest application for stress testing the server.


In order to run the configuration, docker is required, with the command:
`docker compose up`

The default test has the following attributes:

test type	- SLOW HEADERS

number of connections -	50

URL -	http://localhost/

verb	- GET

interval between follow up data -	10 seconds

connections per second -	50

test duration -	240 seconds

probe connection timeout -	5 seconds

max length of followup data field -	32 bytes
