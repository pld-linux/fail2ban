Summary:	Ban IPs that make too many password failures
Summary(pl.UTF-8):	Blokowanie IP powodujących zbyt dużo prób logowań z błędnym hasłem
Name:		fail2ban
Version:	0.8.4
Release:	4
License:	GPL
Group:		Daemons
Source0:	http://dl.sourceforge.net/fail2ban/%{name}-%{version}.tar.bz2
# Source0-md5:	df94335a5d12b4750869e5fe350073fa
Source1:	%{name}.init
Source2:	%{name}.tmpfiles
Patch0:		%{name}-CVE-2009-5023.patch
URL:		http://fail2ban.sourceforge.net/
BuildRequires:	python-devel
BuildRequires:	python-modules
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.219
Requires(post,preun):	/sbin/chkconfig
Requires:	python-log4py
Requires:	rc-scripts
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
%{__python} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d \
	$RPM_BUILD_ROOT%{_mandir}/man1 \
	$RPM_BUILD_ROOT/usr/lib/tmpfiles.d

PYTHONPATH=$RPM_BUILD_ROOT%{py_sitescriptdir}; export PYTHONPATH

%{__python} setup.py install \
	--optimize=2 \
	--root=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/fail2ban
install man/*.1 $RPM_BUILD_ROOT%{_mandir}/man1

install %{SOURCE2} $RPM_BUILD_ROOT/usr/lib/tmpfiles.d/%{name}.conf

%py_postclean

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add %{name}
%service %{name} restart

%preun
if [ "$1" = "0" ]; then
	%service -q %{name} stop
	/sbin/chkconfig --del %{name}
fi

%files
%defattr(644,root,root,755)
%doc ChangeLog README TODO COPYING
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(755,root,root) %{_bindir}/%{name}-*
/usr/lib/tmpfiles.d/%{name}.conf
%dir /var/run/%{name}
%dir %{_sysconfdir}/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/*
%{py_sitescriptdir}/*
%{_mandir}/man1/*
