Summary:	Ban IPs that make too many password failures
Summary(pl.UTF-8):	Blokowanie IP powodujących zbyt dużo prób logowań z błędnym hasłem
Name:		fail2ban
Version:	0.10.4
Release:	2
License:	GPL
Group:		Daemons
Source0:	https://github.com/fail2ban/fail2ban/archive/%{version}.tar.gz
# Source0-md5:	5df67c74c14e6da26df8e798deefca13
Source1:	%{name}.init
Source2:	%{name}.logrotate
Source3:	paths-pld.conf
Source4:	%{name}.sysconfig
Patch0:		logifiles.patch
URL:		http://fail2ban.sourceforge.net/
BuildRequires:	python-devel
BuildRequires:	python-modules
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.710
Requires(post,preun):	/sbin/chkconfig
Requires(post,preun,postun):	systemd-units >= 38
Requires:	python-dnspython
Requires:	python-log4py
Requires:	python-modules-sqlite
Requires:	python-pyinotify >= 0.8.3
Requires:	rc-scripts
Requires:	systemd-units >= 38
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Fail2Ban scans log files like /var/log/secure and bans IP that makes
too many password failures. It updates firewall rules to reject the IP
address. These rules can be defined by the user. Fail2Ban can read
multiple log files including sshd or Apache web server logs.

%description -l pl.UTF-8
Fail2Ban skanuje pliki logów takie jak /var/log/secure i blokuje IP
powodujące zbyt dużo prób logowań z błędnym hasłem. Uaktualnia regułki
firewalla, aby odrzucić adres IP. Regułki te mogą być definiowane
przez użytkownika. Fail2Ban potrafi czytać wiele plików logów włącznie
z sshd czy plikami logów serwera WWW Apache.

%prep
%setup -q
%patch0 -p1
rm setup.cfg

%build
%py_build

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{rc.d/init.d,logrotate.d,sysconfig} \
	$RPM_BUILD_ROOT{%{_mandir}/man1,/var/{log,run/fail2ban}} \
	$RPM_BUILD_ROOT{%{systemdunitdir},%{systemdtmpfilesdir}}

%py_install \
	--install-lib=%{py_sitescriptdir} \
	--root=$RPM_BUILD_ROOT

install -p man/*.1 $RPM_BUILD_ROOT%{_mandir}/man1

install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/fail2ban
install -p %{SOURCE2} $RPM_BUILD_ROOT/etc/logrotate.d/fail2ban
install -p %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/fail2ban/paths-pld.conf
install -p %{SOURCE4} $RPM_BUILD_ROOT/etc/sysconfig/%{name}

install -p files/fail2ban-tmpfiles.conf $RPM_BUILD_ROOT%{systemdtmpfilesdir}/fail2ban.conf
install -p build-2/fail2ban.service $RPM_BUILD_ROOT%{systemdunitdir}/fail2ban.service

:> $RPM_BUILD_ROOT/var/log/fail2ban.log

%py_postclean

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add %{name}
%service %{name} restart
%systemd_post fail2ban.service

%preun
if [ "$1" = "0" ]; then
	%service -q %{name} stop
	/sbin/chkconfig --del %{name}
fi
%systemd_preun fail2ban.service

%postun
%systemd_reload

%triggerpostun -- fail2ban < 0.8.11-3
%systemd_trigger fail2ban.service

%files
%defattr(644,root,root,755)
%doc CONTRIBUTING.md ChangeLog DEVELOP FILTERS README.md RELEASE THANKS TODO COPYING FILTERS doc/run-rootless.txt
%attr(754,root,root) /etc/rc.d/init.d/fail2ban
%attr(755,root,root) %{_bindir}/fail2ban-client
%attr(755,root,root) %{_bindir}/fail2ban-python
%attr(755,root,root) %{_bindir}/fail2ban-regex
%attr(755,root,root) %{_bindir}/fail2ban-server
%attr(755,root,root) %{_bindir}/fail2ban-testcases
%{systemdunitdir}/fail2ban.service
%{systemdtmpfilesdir}/fail2ban.conf
%dir /var/run/fail2ban
%dir %{_sysconfdir}/fail2ban
%dir %{_sysconfdir}/fail2ban/action.d
%attr(755,root,root) %{_sysconfdir}/fail2ban/action.d/badips.py
%attr(755,root,root) %{_sysconfdir}/fail2ban/action.d/smtp.py
%dir %{_sysconfdir}/fail2ban/fail2ban.d
%dir %{_sysconfdir}/fail2ban/filter.d
%dir %{_sysconfdir}/fail2ban/filter.d/ignorecommands
%attr(755,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/fail2ban/filter.d/ignorecommands/apache-fakegooglebot
%dir %{_sysconfdir}/fail2ban/jail.d
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/fail2ban/*.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/fail2ban/*/*.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/fail2ban
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%{py_sitescriptdir}/%{name}
%{py_sitescriptdir}/%{name}-%{version}-py*.egg-info
%{_mandir}/man1/fail2ban-client.1*
%{_mandir}/man1/fail2ban-python.1*
%{_mandir}/man1/fail2ban-regex.1*
%{_mandir}/man1/fail2ban-server.1*
%{_mandir}/man1/fail2ban-testcases.1*
%{_mandir}/man1/fail2ban.1*
%attr(750,root,root) %dir /var/lib/%{name}
%attr(640,root,logs) %ghost /var/log/fail2ban.log
