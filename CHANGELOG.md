# Changelog

## [2.2.0] - 2019-02-05
### Added 
- ARGO-1580 Minimal container for tests
- ARGO-1572 Public profiles, probes and metric pages
- ARGO-1524 Introduce services and probes view
- ARGO-1501 Tests for API methods
- ARGO-1449 Add ability to browse all recent actions
- ARGO-1442 Token and session authenticated REST API
- ARGO-1442 Tests for authenticated REST API
- ARGO-1371 Make use of full-blown DBMS

### Fixed
- ARGO-1628 Refine log entries view
- ARGO-1612 Fix tests by creating all needed tables in in-memory-DB
- ARGO-1568 History comments not rendered properly


## [2.1.0] - 2018-11-30
### Added
- ARGO-1497 Publicly available Probes pages
- ARGO-1448 Active/Passive metric designation in metric configuration UI page
- ARGO-1309 Static Metric Config attribute with predefined keys
- ARGO-1370 Optimize connectors queries to POEM
- ARGO-1327 Update probe data without creating new version

### Changed 
- ARGO-1500 Reformat None/NULL field values fetched from DB to empty string in API views
- ARGO-1499 Do not allow probe name changes to existing probe
- ARGO-1485 Sorted autocompletion Metric entries
- ARGO-1482 Allow empty values for keys in metric configuration
- ARGO-1372 Use Apache and mod-wsgi from Software Collections
- ARGO-565 Move to Django 2.0 version

### Fixed
- ARGO-1462 Plaintext LogEntry comments
- ARGO-950 Metric history browse always show most recent changes
