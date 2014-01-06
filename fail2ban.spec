Summary:	Ban IPs that make too many password failures
Summary(pl.UTF-8):	Blokowanie IP powodujących zbyt dużo prób logowań z błędnym hasłem
Name:		fail2ban
Version:	0.8.11
Release:	2.4
License:	GPL
Group:		Daemons
Source0:	http://download.sourceforge.net/fail2ban/%{name}-%{version}.tar.gz
# Source0-md5:	2182a21c7efd885f373ffc941d11914d
Source1:	%{name}.init
Source2:	%{name}.logrotate
Patch0:		ipv6.patch
Patch1:		private-scriptdir.patch
URL:		http://fail2ban.sourceforge.net/
BuildRequires:	python-devel
BuildRequires:	python-modules
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.671
Requires(post,preun):	/sbin/chkconfig
Requires(post,preun,postun):	systemd-units >= 38
Requires:	python-log4py
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
%patch1 -p1
rm setup.cfg

# we don't want very generic named dirs directly in py_sitescriptdir
sed -i -e 's|@@SCRIPTDIR@@|"%{py_sitescriptdir}/%{name}"|' fail2ban-{client,regex,server}

%build
%{__python} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{rc.d/init.d,logrotate.d} \
	$RPM_BUILD_ROOT{%{_mandir}/man1,/var/log} \
	$RPM_BUILD_ROOT{%{systemdunitdir},%{systemdtmpfilesdir}}

%{__python} setup.py install \
	--optimize=2 \
	--install-lib=%{py_sitescriptdir}/%{name} \
	--root=$RPM_BUILD_ROOT

install -p man/*.1 $RPM_BUILD_ROOT%{_mandir}/man1

install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/fail2ban
install -p %{SOURCE2} $RPM_BUILD_ROOT/etc/logrotate.d/fail2ban

install -p files/fail2ban-tmpfiles.conf $RPM_BUILD_ROOT%{systemdtmpfilesdir}/fail2ban.conf
install -p files/fail2ban.service $RPM_BUILD_ROOT%{systemdunitdir}/fail2ban.service

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
%doc ChangeLog README.md TODO COPYING
%attr(754,root,root) /etc/rc.d/init.d/fail2ban
%attr(755,root,root) %{_bindir}/fail2ban-client
%attr(755,root,root) %{_bindir}/fail2ban-iptables
%attr(755,root,root) %{_bindir}/fail2ban-regex
%attr(755,root,root) %{_bindir}/fail2ban-server
%{systemdunitdir}/fail2ban.service
%{systemdtmpfilesdir}/fail2ban.conf
%dir /var/run/fail2ban
%dir %{_sysconfdir}/fail2ban
%dir %{_sysconfdir}/fail2ban/action.d
%dir %{_sysconfdir}/fail2ban/fail2ban.d
%dir %{_sysconfdir}/fail2ban/filter.d
%dir %{_sysconfdir}/fail2ban/jail.d
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/fail2ban/*.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/fail2ban/*/*.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/fail2ban
%{py_sitescriptdir}/%{name}
%{_mandir}/man1/fail2ban-client.1*
%{_mandir}/man1/fail2ban-regex.1*
%{_mandir}/man1/fail2ban-server.1*
%{_mandir}/man1/fail2ban.1*
%attr(640,root,logs) %ghost /var/log/fail2ban.log
