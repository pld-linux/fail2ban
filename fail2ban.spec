Summary:	Ban IPs that make too many password failures
Name:		fail2ban
Version:	0.6.0
Release:	1
License:	GPL
Group:		Daemons
URL:		http://fail2ban.sourceforge.net/
Source0:	http://dl.sourceforge.net/fail2ban/%{name}-%{version}.tar.bz2
# Source0-md5:	129c4e76539a22ab60d025fbf137f962
BuildRequires:	dos2unix
Requires:	python-log4py
BuildArch:	noarch
BuildRoot:      %{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Fail2Ban scans log files like /var/log/secure and bans IP that makes
too many password failures. It updates firewall rules to reject the IP
address. These rules can be defined by the user. Fail2Ban can read
multiple log files including sshd or Apache web server logs.

%prep
%setup -q

%build
rm setup.cfg
%{__python} setup.py build

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/etc/rc.d/init.d/
PYTHONPATH=$RPM_BUILD_ROOT%{py_sitescriptdir}; export PYTHONPATH

python setup.py install \
  --optimize=2 \
	--root=$RPM_BUILD_ROOT

find $RPM_BUILD_ROOT%{py_sitescriptdir} -name \*.py -exec rm {} \;
dos2unix config/redhat-initd
install config/redhat-initd $RPM_BUILD_ROOT/etc/rc.d/init.d/fail2ban
install config/fail2ban.conf.default $RPM_BUILD_ROOT%{_sysconfdir}/fail2ban.conf

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
%doc CHANGELOG README TODO
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(755,root,root) %{_bindir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}.conf
%{py_sitescriptdir}/*
