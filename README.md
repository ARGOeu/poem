# POEM service for ARGO framework

## Description

POEM service is a light web application used in ARGO framework that holds list
of services, metrics and probes used within EGI infrastructure. Services and
associated metrics are grouped into POEM profiles that instruct monitoring
instances what kind of tests to execute for given service. Additionally, it is
a register of probes and Nagios metric configurations exposed to monitoring
instances via REST API.

It is based on Django web framework, specifically extension of its admin
interface and several Django modules. EGI users are allowed to sign-in through
EGI CheckIn federated authentication mechanism. Application is served with
Apache web server and all its information is stored in light SQLite database.

Devel instance: https://poem-devel.argo.grnet.gr/

Production instance: http://poem.egi.eu/

More info: http://argoeu.github.io/guides/poem
