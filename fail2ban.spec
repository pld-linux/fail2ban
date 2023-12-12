Summary:	Ban IPs that make too many password failures
Summary(pl.UTF-8):	Blokowanie IP powodujących zbyt dużo prób logowań z błędnym hasłem
Name:		fail2ban
Version:	1.0.2
Release:	3
License:	GPL
Group:		Daemons
Source0:	https://github.com/fail2ban/fail2ban/archive/%{version}.tar.gz
# Source0-md5:	96582af04e60bf56617da9f9cbda0aa7
Source1:	%{name}.init
Source2:	%{name}.logrotate
Source3:	paths-pld.conf
Source4:	%{name}.sysconfig
Patch0:		logifiles.patch
URL:		http://fail2ban.sourceforge.net/
BuildRequires:	python3-2to3
BuildRequires:	python3-devel
BuildRequires:	python3-modules
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.710
Requires(post,preun):	/sbin/chkconfig
Requires(post,preun,postun):	systemd-units >= 38
Requires:	python3-dns
Requires:	python3-pyinotify >= 0.8.3
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

sed -E -i -e '1s,#!\s*/usr/bin/env\s+python2(\s|$),#!%{__python3}\1,' -e '1s,#!\s*/usr/bin/env\s+python(\s|$),#!%{__python3}\1,' -e '1s,#!\s*/usr/bin/python(\s|$),#!%{__python3}\1,' \
      bin/fail2ban-client \
      bin/fail2ban-regex \
      bin/fail2ban-server \
      bin/fail2ban-testcases \
      setup.py

sed -E -i -e '1s,#!\s*/usr/bin/env\s+(.*),#!%{__bindir}\1,' \
      config/filter.d/ignorecommands/apache-fakegooglebot \
      fail2ban/tests/files/config/apache-auth/digest.py \
      fail2ban/tests/files/ignorecommand.py

sed -i -e 's#2to3#2to3-%{py3_ver}#g' fail2ban-2to3
./fail2ban-2to3

%build
%py3_build

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{rc.d/init.d,logrotate.d,sysconfig} \
	$RPM_BUILD_ROOT{%{_mandir}/man{1,5},/var/{log,run/fail2ban}} \
	$RPM_BUILD_ROOT{%{systemdunitdir},%{systemdtmpfilesdir}}

%py3_install \
	--install-lib=%{py3_sitescriptdir} \
	--root=$RPM_BUILD_ROOT

install -p man/*.1 $RPM_BUILD_ROOT%{_mandir}/man1
install -p man/*.5 $RPM_BUILD_ROOT%{_mandir}/man5

install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/fail2ban
install -p %{SOURCE2} $RPM_BUILD_ROOT/etc/logrotate.d/fail2ban
install -p %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/fail2ban/paths-pld.conf
install -p %{SOURCE4} $RPM_BUILD_ROOT/etc/sysconfig/%{name}

sed -e 's# /run# /var/run#g' files/fail2ban-tmpfiles.conf > $RPM_BUILD_ROOT%{systemdtmpfilesdir}/fail2ban.conf
install -p build-3/fail2ban.service $RPM_BUILD_ROOT%{systemdunitdir}/fail2ban.service

:> $RPM_BUILD_ROOT/var/log/fail2ban.log

%py_postclean

rm $RPM_BUILD_ROOT%{_bindir}/fail2ban-testcases

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
%doc CONTRIBUTING.md ChangeLog DEVELOP FILTERS README.md RELEASE THANKS TODO COPYING doc/run-rootless.txt
%attr(754,root,root) /etc/rc.d/init.d/fail2ban
%attr(755,root,root) %{_bindir}/fail2ban-client
%attr(755,root,root) %{_bindir}/fail2ban-python
%attr(755,root,root) %{_bindir}/fail2ban-regex
%attr(755,root,root) %{_bindir}/fail2ban-server
%{systemdunitdir}/fail2ban.service
%{systemdtmpfilesdir}/fail2ban.conf
%dir /var/run/fail2ban
%dir %{_sysconfdir}/fail2ban
%dir %{_sysconfdir}/fail2ban/action.d
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
%{py3_sitescriptdir}/%{name}
%{py3_sitescriptdir}/%{name}-%{version}-py*.egg-info
%{_mandir}/man1/fail2ban-client.1*
%{_mandir}/man1/fail2ban-python.1*
%{_mandir}/man1/fail2ban-regex.1*
%{_mandir}/man1/fail2ban-server.1*
%{_mandir}/man1/fail2ban-testcases.1*
%{_mandir}/man1/fail2ban.1*
%{_mandir}/man5/jail.conf.5*
%attr(750,root,root) %dir /var/lib/%{name}
%attr(640,root,logs) %ghost /var/log/fail2ban.log
