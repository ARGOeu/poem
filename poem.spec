# sitelib 
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           poem
Version:        0.10.7
Release:        4%{?dist}
Summary:        Profile Management (POEM) system for Service Availability Monitoring (SAM).
Group:          Web application
License:        ASL 2.0
Vendor:         CERN
URL:            https://tomtools.cern.ch/confluence/display/SAM/POEM
Source0:        poem-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
Requires:       Django >= 1.1
Requires:       django-ajax-selects
Requires:       mod_wsgi
Requires:       mod_ssl 

%description
The Profile Management (POEM) system couples metrics and services and enables
profile-based configuration of SAM Nagios.

%prep
%setup -q

%build
%{__python} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
python setup.py install --root=$RPM_BUILD_ROOT 

install -d -m 755 $RPM_BUILD_ROOT/var/log/%{name}/
install -d -m 755 $RPM_BUILD_ROOT/var/lib/%{name}/
install -d -m 755 $RPM_BUILD_ROOT/%{_datadir}/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%files 
%defattr(-,root,root,-)
%{python_sitelib}/Poem/*
%{python_sitelib}/*egg-info

%{_bindir}/poem-syncservtype
%{_bindir}/poem-syncvo
%{_bindir}/poem-createdb
%{_bindir}/poem-importprofiles

%config %{_sysconfdir}/%{name}/poem_logging.ini
%config %{_sysconfdir}/httpd/conf.d/poem.conf
%attr(0640,root,apache)
%config(noreplace) %{_sysconfdir}/%{name}/poem.ini
%attr(0644,root,root) %{_sysconfdir}/cron.d/poem-syncvosf

%{_datadir}/%{name}/apache/poem.wsgi
%{_datadir}/%{name}/media/*


%defattr(-,apache,apache,-)
%dir %{_var}/lib/%{name}
%dir %{_var}/log/%{name}

%pre 

%changelog
* Sat Jun 27 2015 Daniel Vrcic <dvrcic@srce.hr> - 0.10.7-4
- introduced groups of profiles
* Tue Jun 16 2015 Daniel Vrcic <dvrcic@srce.hr> - 0.10.7-3
- fixed bug with assignment of readonly perm for new user
* Mon Mar 23 2015 Daniel Vrcic <dvrcic@srce.hr> - 0.10.7-2
- remove deprecations
* Wed Feb 25 2015 Daniel Vrcic <dvrcic@srce.hr> - 0.10.7-1
- removed embedded jquery and django-admin static files
- django-ajax-selects for autocompletion
  https://github.com/ARGOeu/poem/issues/8
* Tue Feb 17 2015 Daniel Vrcic <dvrcic@srce.hr> - 0.10.6-3
- fixed bug when superuser wants to create completely new profile
* Wed Feb 11 2015 Daniel Vrcic <dvrcic@srce.hr> - 0.10.6-2
- added forgotten completion for metrics
- SRMv2 service type is now manually added in syncservtype
* Thu Feb 5 2015 Daniel Vrcic <dvrcic@srce.hr> - 0.10.6-1
- update deprecated manage.py django project setter
- automate superuser creation: createdb tool doesn't need to be interactive anymore
  https://github.com/ARGOeu/poem/issues/9
* Sat Jan 17 2015 Daniel Vrcic <dvrcic@srce.hr> - 0.10.5-2
- rid of django-piston
- redesigned metrics_in_profiles API for ar-sync
- prevent potential malicious profile change due to django bug
- more verbose syncers
- cert DN as a owner of profile
- augment completion with service types not in GOCDB
- readonly mode
- redundant Poem link in UI removed
- RPM build from .spec stored in tarball
- deleted leftovers
* Wed Nov 19 2014 Daniel Vrcic <dvrcic@srce.hr> - 0.10.0-1
- POEM for ARGO framework
* Fri Jan 24 2014 Marian Babik <marian.babik@cern.ch> - 0.9.91-1
- SAM-3326 poem: fix redirect for /poem
* Mon Jun 17 2013 Paloma Fuente <pfuentef@cern.ch> - 0.9.84-1
- SAM-3299 poem: Missing backward compatible handler for api/expressions
* Fri May 17 2013 Marian Babik <marian.babik@cern.ch> - 0.9.83-1
- SAM-3273 Add new ARC metrics
* Mon May 06 2013 Paloma Fuente <pfuentef@cern.ch> - 0.9.82-1
- SAM-3263 poem: remove org.sam.mpi.CE-JobSubmit
* Thu Apr 18 2013 Marian Babik <marian.babik@cern.ch> - 0.9.81-1
- SAM-3239 poem: metric mapping configuration
* Tue Mar 26 2013 Marian Babik <marian.babik@cern.ch> - 0.9.80-1
- SAM-3240 poem: update unit tests in nightly build
- SAM-3239 poem: metric mapping configuration
- SAM-3238 poem_sync: patch synchronizer to support metric renaming
- SAM-3208 poem: new version of metricinstances api
- SAM-3191 poem: create poem diff script
- SAM-2596 poem_sync: check if configuration is sane after initial yaim
* Tue Jan 29 2013 Marian Babik <marian.babik@cern.ch> - 0.9.71-1
- SAM-3187 poem: Add emi.wn.WN metrics to the poem NV fixture
* Thu Jan 25 2013 Marian Babik <marian.babik@cern.ch> - 0.9.70-1
- SAM-3173 Change metric namespaces in all profiles for NV
- SAM-2544  Restore POEM web config when web is enabled
- POEM synchronizer will now fail with status 2 if it ends up with no profiles 
* Wed Jul 25 2012 Marian Babik <marian.babik@cern.ch> - 0.9.63-1
- Removed nagios tag implementation (keeping POEM_NAGIOS_PROFILES)
- SAM-2372 poem: source code documentation
- SAM-2828 Add QCG services to ROC profile
- SAM-2844 service flavours and vo are needed by poem web interface
* Mon Jul 23 2012 Marian Babik <marian.babik@cern.ch> - 0.9.62-1
- SAM-2072 Change to Django-1.3
* Fri Jul 06 2012 Marian Babik <marian.babik@cern.ch> - 0.9.61-1
- SAM-2472 Add tagging mechanism to POEM
- SAM-2072 Change to Django-1.3
- SAM-2770 poem: Change to new atp dependencies
* Tue Jun 26 2012 Marian Babik <marian.babik@cern.ch> - 0.9.6-1
- SAM-2774 Errors in ncg.log (samval009) - hr.srce.RGMA-CertLifetime
* Sat Jun 16 2012 Marian Babik <marian.babik@cern.ch> - 0.9.5-1
- SAM-2749 poem: generate new bootstrapping file for the nightly validation
* Fri Jun 15 2012 Marian Babik <marian.babik@cern.ch> - 0.9.4-1
- SAM-2743poem_sync: fail if atp doesn't provide services for all VOs
* Tue Jun 12 2012 Marian Babik <marian.babik@cern.ch> - 0.9.3-1
- SAM-2735  poem_sync: change implementation for getting services
* Tue Jun 12 2012 Marian Babik <marian.babik@cern.ch> - 0.9.2-1
- SAM-2736  poem_sync: introduce yaim variable
- SAM-2735  poem_sync: change implementation for getting services
* Mon May 21 2012 Marian Babik <marian.babik@cern.ch> - 0.9.1-1
- SAM-2523 poem_sync: change cronjob user to daemon_user
- SAM-2325 Remove metric org.arc.RLS from ARC-CE service
- SAM-2557 poem: bootstrapping from file fails due to unique constraint
* Tue Apr 17 2012 Marian Babik <marian.babik@cern.ch> - 0.8.21-1
- SAM-2622 poem logging configuration
* Mon Mar 26 2012 Marian Babik <marian.babik@cern.ch> - 0.8.20-1
- SAM-2557 poem: bootstrapping from file fails due to unique constraint
- SAM-2558 poem_sync: servicemetricinstances returns empty tuples
* Fri Mar 23 2012 Marian Babik <marian.babik@cern.ch> - 0.8.19-1
- SAM-2485 Support for VO independent metrics and services in bootstrapping
- SAM-2511 Add DesktopGrid services to ROC profile
* Wed Mar 21 2012 Marian Babik <marian.babik@cern.ch> - 0.8.18-1
- SAM-2490 atp_synchro and poem_sync init.d scripts signal themselves on service stop
* Wed Mar 14 2012 Marian Babik <marian.babik@cern.ch> - 0.8.17-1
- SAM-2371 poem: remove vo per metric in the profile form
- SAM-2429 poem: generate new bootstrapping file for the nightly validation (udpate GLEXEC)
* Fri Mar 02 2012 Marian Babik <marian.babik@cern.ch> - 0.8.16-1
- SAM-2453 poem_sync: Fix poem_sync API fqan behaviour
* Wed Feb 29 2012 Marian Babik <marian.babik@cern.ch> - 0.8.15-1
- SAM-2448 poem: vo doesn't need to be provided for metric instance
- SAM-2429 poem: generate new bootstrapping file for the nightly validation
* Tue Feb 28 2012 Marian Babik <marian.babik@cern.ch> - 0.8.14-1
- SAM-2315 poem_sync: call to urllib.urlopen blocks and never returns
- SAM-2430 poem_sync: Fix poem namespace sanity check
- SAM-2431 poem_sync: Fix poem_sync behavior when namespace is removed
- SAM-2417 poem_sync: config_poem_sync should fail yaim if unable to boostrap empty database
- SAM-2310 poem_sync: Fix poem_sync output redirection in yaim
* Fri Feb 22 2012 Marian Babik <marian.babik@cern.ch> - 0.8.13-1
- SAM-2218 poem_sync errors shown during fresh install of sam-gridmon
- SAM-2369  poem_sync: restricted synchronization can ignore profiles with lowercase letters
- SAM-2370  poem: default debug level should be set to false
- SAM-2424  poem: introduce metricinstance tuples for ncg
- SAM-2417 poem_sync: config_poem_sync should fail yaim if unable to boostrap empty database
* Fri Jan 13 2012 Marian Babik <marian.babik@cern.ch> - 0.8.12-1
- SAM-2304 poem: import mddb profiles in yaim
- SAM-2306 poem_testcase failing on SAM Nagios 
* Tue Jan 10 2012 Marian Babik <marian.babik@cern.ch> - 0.8.11-1
- SAM-2240  POEM_SYNC: function returning list of tuples for which MRS is supposed to receive data
- POEM_SYNC: Web API won't list deleted profiles by default
* Fri Dec 23 2011 Marian Babik <marian.babik@cern.ch> - 0.8.10-1
- Fixing bug in import profiles from poem instance
* Wed Dec 20 2011 Marian Babik <marian.babik@cern.ch> - 0.8.9-1
- SAM-2280 invalid db objects for metric_obj and profile_obj
- Service poem_sync installed with incorrect permissions
* Tue Dec 19 2011 Marian Babik <marian.babik@cern.ch> - 0.8.8-1
- SAM-2273  missing (/)s in install/update oracle sql for db 1.2 in poem-sync-0.8.7
- SAM-2266  SAM-2218 MySQL: Upgrade of POEM fails on nightly validation
- Fixing missing commits in poem-sync MySQL schemas
* Sun Dec 18 2011 Marian Babik <marian.babik@cern.ch> - 0.8.7-1
- Fixing MySQL upgrade syntax error
* Fri Dec 16 2011 Marian Babik <marian.babik@cern.ch> - 0.8.6-1
- SAM-2264 poem: introduce filter for profiles
* Fri Dec 16 2011 Marian Babik <marian.babik@cern.ch> - 0.8.5-1
- SAM-2261 poem: schema 1.3 does have proper dependencies
* Fri Dec 02 2011 Marian Babik <marian.babik@cern.ch> - 0.8.4-1
- SAM-2063 poem_sync: establish mechanism to restrict which profiles are to be synchronized
- SAM-2238  POEM_SYNC FUNCTION getMetricsInProfile(serviceId, profileId, voId, fqanName, check_time) - partially
- SAM-2207  POEM_SYNC function getProfiles(serviceId, metricId, fqan, voId, check_time) - partially
- SAM-2205  function getPoemSyncMetricIdForName - partially
- SAM-1745 Create service for cronjob ch.cern.sam.POEMSync
- SAM-2061  poem: introduce bootstrapping of profiles
- SAM-2216  poem: fix glite-yaim-nagios config
- SAM-2199  poem: Develop JavaScript features for the new views
- SAM-2198  poem: Change django admin views
- SAM-2197  poem: Change model for metric instances
- SAM-2209  poem: fix django piston (Web API) to reflect new models
- SAM-2208  poem: fix import from MDDB to reflect new schema
- SAM-2058  poem: integrate TIME_ZONE in the configuration
- SAM-1745 Create locking mechanism for POEM
- SAM-2184  poem_sync: Fixtures for nightly build need to be regenerated
* Wed Nov 23 2011 Kumar Vaibhav <vaibhav.kumar@cern.ch> - 0.8.3-1
- SAM-2186 Changed the probe implementation
- SAM-2063 Slective Profile synchronization enabled
* Wed Nov 16 2011 Kumar Vaibhav <vaibhav.kumar@cern.ch> - 0.8.2-1
- SAM-2190 MySQL POEM_SYNC table aren't created in InnoDB engine
* Tue Nov 15 2011 Marian Babik <marian.babik@cern.ch> - 0.8.1-1
- SAM-2169  poem_sync: Add vo as an attribute of metric_instances
- SAM-2153  Strange table name in Poem_Sync - POEM_SYNC_PROFILE_METRICINC26
* Fri Oct 21 2011 Marian Babik <marian.babik@cern.ch> - 0.7.7-1
- SAM-2080 poem: exception thrown while trying to update groups
* Wed Oct 19 2011 Marian Babik <marian.babik@cern.ch> - 0.7.6-1
- SAM-2073 poem: instance needs to have a primary key value before ...
* Tue Oct 18 2011 Marian Babik <marian.babik@cern.ch> - 0.7.5-1
- SAM-1731  Fix nightly build for poem to cover Update-13 changes
- SAM-2038  poem_sync: schema fixes
- SAM-2039  poem: logging changes
- SAM-2059  poem: extend profile name field
* Wed Oct 12 2011 Marian Babik <marian.babik@cern.ch> - 0.7.4-1
- fixed poem_sync schema versioning
* Mon Oct 10 2011 Marian Babik <marian.babik@cern.ch> - 0.7.3-1
- fixed namespace bootstrapping if database is empty
- changes in poem logging configuration
* Thu Oct 06 2011 Marian Babik <marian.babik@cern.ch> - 0.7.2-1
- SAM-2010 poem_sync: schema structure
* Wed Oct 05 2011 Marian Babik <marian.babik@cern.ch> - 0.7.1-1
- SAM-1969 poem_sync: schema details
- SAM-1963  POEM create_structure.sql invalid sequence when doing INSERT INTO schema_details
- SAM-1956  Replace LCG_SAM_MDDB_DEV2@LCG_DEV_DB with LCG_SAM_POEM_DEV@LCG_DEV_DB
- SAM-1882  poem: revise config_poem_mysql
- SAM-1881  poem: create MySQL schema for poem-web/api
- SAM-1880  poem: poem-web needs to become namespace-aware
- SAM-1872  poem_sync: Configure check_poem_sync via glite-yaim-nagios
- SAM-1731 Fix nightly build for poem to cover Update-13 changes
* Wed Sep 07 2011 Marian Babik <marian.babik@cern.ch> - 0.6.1-1
- SAM-1735  poem: jquery images are missing in the distribution
- SAM-1736  poem: trying to save profile hangs for users without permissions
- SAM-1743  poem: create scripts to update permissions and content types
- SAM-1746  poem: check client certificate
- SAM-1762  poem_sync: Nagios probe
- SAM-1763  poem_sync: poem_sync_schema-1.0.sql error
- SAM-1764 poem_sync: no apache configuration and missing poem_sync_api
- SAM-1768  poem_sync: contract issues
- SAM-1811  poem: add description field to the API
- SAM-1880  poem: poem-web needs to become namespace-aware (API only)
* Thu Aug 11 2011 Marian Babik <marian.babik@cern.ch> - 0.5.6-1
- SAM-1764 poem_sync: no apache configuration and missing poem_sync_api
* Wed Aug 10 2011 Marian Babik <marian.babik@cern.ch> - 0.5.5-1
- SAM-1738 poem: config_poem (glite-yaim-nagios) additions
- SAM-1764 poem_sync: no apache configuration and missing poem_sync_api
* Tue Aug 09 2011 Marian Babik <marian.babik@cern.ch> - 0.5.4-1
- SAM-1738 poem: config_poem (glite-yaim-nagios) additions
* Wed Jul 27 2011 Marian Babik <marian.babik@cern.ch> - 0.5.3-1
- SAM-1734 poem: make certificate login optional
* Mon Jul 25 2011 Marian Babik <marian.babik@cern.ch> - 0.5.2-1
- SAM-1732 Poem schema initialization script for schema 1.2 in poem-0.5.1 fails
* Fri Jul 22 2011 Marian Babik <marian.babik@cern.ch> - 0.5.1-1
- SAM-1702 poem: create homepage
- SAM-1697  poem: perform schema changes
- SAM-1696  poem: sync ATP groups
- SAM-1695  poem: profile validation
- SAM-1694  poem: authorization
- SAM-1451  poem: authentication
* Mon Jun 27 2011 Marian Babik <marian.babik@cern.ch> - 0.4.3-1
- SAM-1045  Add the namespace information to poem_sync database to bootstrap the poem_sync
- SAM-1044  Change poem_sync fixtures to have a valid namespace
- SAM-1380  Implement config_poem_sync and config_poem_sync_mysql
* Wed Jun 15 2011 Marian Babik <marian.babik@cern.ch> - 0.4.2-1
- fixed poem-sync schema files
* Tue Jun 14 2011 Marian Babik <marian.babik@cern.ch> - 0.4.1-1
- SAM-1479 Add schema files to the poem and poem_sync packages
- SAM-1597  Add description field to profiles
* Thu Apr 28 2011 Marian Babik <marian.babik@cern.ch> - 0.3-1
- SAM-1449 Fix media URL for admin pages
- SAM-1445 Fix httpd configuration for poem
- SAM-1444 Change poem admin profile layout
- SAM-1450 Make admin the default poem page
- SAM-1453 Fix handling of media files in setup.py
* Wed Apr 27 2011 Marian Babik <marian.babik@cern.ch> - 0.2-2
- SAM-1445  Fix httpd configuration for poem
- SAM-1446  Add admin media files to poem package
* Tue Mar 26 2011 Marian Babik <marian.babik@cern.ch> - 0.2-1
- SAM-1109  Change field 'metrics' to 'metricinstances' in 'profile' model of POEM
- SAM-1046  POEM synchronizer crashes over vo names
- SAM-1043  Packaging Errors in POEM Packages
- SAM-1379  Revise glite-yaim-nagios config_poem and config_poem_mysql
- SAM-1228  Creation of a Production URL of POEM 
* Thu Nov 11 2010 Marian Babik <marian.babik@cern.ch> - 0.1-1
- initial version
